#!/usr/bin/env python3
"""Process Wimbledon source data and optionally upload outputs to GCP."""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def normalize_date(raw: str, fmt: str) -> str:
    cleaned = raw.strip()
    if not cleaned:
        return ""
    parsed = datetime.strptime(cleaned, fmt)
    return parsed.strftime("%Y-%m-%d")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_match_history() -> tuple[list[dict[str, str]], list[str]]:
    atp_rows = read_csv_rows(DATA_DIR / "atp_tennis.csv")
    wta_rows = read_csv_rows(DATA_DIR / "wta.csv")

    atp_fields = list(atp_rows[0].keys())
    wta_fields = list(wta_rows[0].keys())
    extra_fields = ["tour", "match_date", "source_file", "is_wimbledon", "is_grass", "season", "winner_is_player_1"]
    all_fields = sorted(set(atp_fields) | set(wta_fields) | set(extra_fields))

    normalized: list[dict[str, str]] = []

    for row in atp_rows:
        out = {field: row.get(field, "") for field in all_fields}
        out["tour"] = "ATP"
        out["match_date"] = normalize_date(row["Date"], "%d-%m-%Y")
        out["source_file"] = "atp_tennis.csv"
        out["is_wimbledon"] = str(row["Tournament"] == "Wimbledon").lower()
        out["is_grass"] = str(row["Surface"] == "Grass").lower()
        out["season"] = out["match_date"][:4]
        out["winner_is_player_1"] = str(row["Winner"] == row["Player_1"]).lower()
        normalized.append(out)

    for row in wta_rows:
        out = {field: row.get(field, "") for field in all_fields}
        out["tour"] = "WTA"
        out["Series"] = row.get("Series", "WTA")
        out["match_date"] = normalize_date(row["Date"], "%Y-%m-%d")
        out["source_file"] = "wta.csv"
        out["is_wimbledon"] = str(row["Tournament"] == "Wimbledon").lower()
        out["is_grass"] = str(row["Surface"] == "Grass").lower()
        out["season"] = out["match_date"][:4]
        out["winner_is_player_1"] = str(row["Winner"] == row["Player_1"]).lower()
        normalized.append(out)

    normalized.sort(key=lambda row: (row["match_date"], row["tour"], row["Tournament"], row["Round"]))
    return normalized, all_fields


def parse_entry_pdf(pdf_path: Path, tour: str) -> tuple[list[dict[str, str]], list[str]]:
    text = "\n".join((page.extract_text() or "") for page in PdfReader(str(pdf_path)).pages)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    records: list[dict[str, str]] = []
    rank_date = ""
    pattern = re.compile(r"^(\d+)\s+(\d+)\s+(.+?)\s{2,}|^(\d+)\s+(\d+)\s+(.+)$")

    for line in lines:
        if line.startswith("Rank Date:"):
            rank_date = line.replace("Rank Date:", "").split("THE CHAMPIONSHIPS")[0].strip()
            continue
        if line.startswith("Player Rank") or line.startswith("Q ="):
            break
        match = pattern.match(line)
        if not match:
            continue
        draw_order = match.group(1) or match.group(4) or ""
        rank = match.group(2) or match.group(5) or ""
        player = (match.group(3) or match.group(6) or "").strip()
        records.append(
            {
                "tour": tour,
                "entry_rank_date_raw": rank_date,
                "entry_rank_date": datetime.strptime(rank_date, "%d/%m/%Y").strftime("%Y-%m-%d") if rank_date else "",
                "draw_order": draw_order,
                "rank": rank,
                "player_raw": player,
                "source_file": pdf_path.name,
            }
        )

    fields = ["tour", "entry_rank_date_raw", "entry_rank_date", "draw_order", "rank", "player_raw", "source_file"]
    return records, fields


def write_csv(path: Path, rows: Iterable[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def upload_file(bucket_name: str, source_path: Path, destination_blob: str) -> None:
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    bucket.blob(destination_blob).upload_from_filename(source_path)


def ensure_bigquery_dataset(project: str, dataset: str, location: str) -> None:
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound

    client = bigquery.Client(project=project)
    dataset_id = f"{project}.{dataset}"
    try:
        client.get_dataset(dataset_id)
    except NotFound:
        ds = bigquery.Dataset(dataset_id)
        ds.location = location
        client.create_dataset(ds)


def load_csv_to_bigquery(project: str, dataset: str, table: str, csv_path: Path) -> None:
    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    table_id = f"{project}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        skip_leading_rows=1,
        source_format=bigquery.SourceFormat.CSV,
        write_disposition="WRITE_TRUNCATE",
    )
    with csv_path.open("rb") as handle:
        job = client.load_table_from_file(handle, table_id, job_config=job_config)
    job.result()


def ensure_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Process local Wimbledon data and optionally upload outputs to GCP.")
    parser.add_argument("--env-file", default=".env", help="Optional env file to load before running.")
    parser.add_argument("--upload-gcs", action="store_true", help="Upload processed files to Cloud Storage.")
    parser.add_argument("--load-bigquery", action="store_true", help="Load processed tables into BigQuery.")
    parser.add_argument("--gcs-prefix", default="processed", help="Bucket prefix for uploaded files.")
    parser.add_argument("--bq-location", default="US", help="BigQuery dataset location.")
    args = parser.parse_args()

    load_env_file(ROOT / args.env_file)

    match_rows, match_fields = build_match_history()
    mens_rows, entry_fields = parse_entry_pdf(DATA_DIR / "MS_Entries.pdf", "ATP")
    womens_rows, _ = parse_entry_pdf(DATA_DIR / "LS_Entries.pdf", "WTA")

    outputs = {
        "match_history": PROCESSED_DIR / "match_history_combined.csv",
        "mens_entries": PROCESSED_DIR / "wimbledon_2026_mens_entries.csv",
        "womens_entries": PROCESSED_DIR / "wimbledon_2026_womens_entries.csv",
    }

    write_csv(outputs["match_history"], match_rows, match_fields)
    write_csv(outputs["mens_entries"], mens_rows, entry_fields)
    write_csv(outputs["womens_entries"], womens_rows, entry_fields)

    print("Local outputs written:")
    for label, path in outputs.items():
        print(f"  - {label}: {path}")

    if args.upload_gcs:
        bucket = ensure_required_env("GCP_BUCKET")
        for path in outputs.values():
            destination = f"{args.gcs_prefix}/{path.name}"
            upload_file(bucket, path, destination)
            print(f"Uploaded gs://{bucket}/{destination}")

    if args.load_bigquery:
        project = ensure_required_env("GOOGLE_CLOUD_PROJECT")
        dataset = ensure_required_env("BIGQUERY_DATASET")
        ensure_bigquery_dataset(project, dataset, args.bq_location)
        load_csv_to_bigquery(project, dataset, "match_history_combined", outputs["match_history"])
        load_csv_to_bigquery(project, dataset, "wimbledon_2026_mens_entries", outputs["mens_entries"])
        load_csv_to_bigquery(project, dataset, "wimbledon_2026_womens_entries", outputs["womens_entries"])
        print(f"Loaded tables into {project}.{dataset}")


if __name__ == "__main__":
    main()
