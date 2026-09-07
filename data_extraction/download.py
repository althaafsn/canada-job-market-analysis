"""
Data Extraction Script for Canada Job Market Analysis
=====================================================

This script automates the retrieval, cryptographic verification, and extraction
of open datasets used across this study.

What data is downloaded?
------------------------
The script reads `sources.json` to download datasets in two stages:

1. Stage '01' — Posting Indices (Indeed Hiring Lab)
   Saved to `data/`:
   - `aggregate_job_postings_CA.csv`: Canada-wide daily job postings index (seasonally adjusted & unadjusted).
   - `job_postings_by_sector_CA.csv`: Daily posting index across 47 sectors (e.g. Software Dev, Data & Analytics).
   - `metro_job_postings_CA.csv`: Daily posting index across 45 Canadian metropolitan areas (CMAs).
   - `provincial_postings_ca.csv`: Daily posting index across all 10 Canadian provinces.
   Source: https://github.com/hiring-lab/job_postings_tracker/tree/master/CA (pinned Git revision).

2. Stage '02' — Microdata & Government Statistics
   Saved to `data/job_bank/` and `data/statcan/`:
   - Job Bank Canada Open Data (`data/job_bank/*.csv`):
     43 monthly snapshot CSVs (January 2023 to July 2026) containing granular individual job postings
     with 65 fields (NOC occupation code, job title, wage/salary range, education, experience level,
     location, telework status, and vacancy count).
     Source: Open Government Portal (https://open.canada.ca/data/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072).
   - Statistics Canada Table 14-10-0444-01 (`data/statcan/`):
     Full archive (`14100444-eng.zip`) containing quarterly survey data (Q1 2015 to Q1 2026) on job vacancies,
     offered hourly wages, and payroll counts by occupation and geography (`14100444.csv` and `14100444_MetaData.csv`).
     Source: Statistics Canada (https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410044401).

Key Safety & Reliability Features:
----------------------------------
- SHA-256 Checksum Verification: Every file is checked against `sources.json` to guarantee data integrity.
- Atomic Writes: Downloads stream into a temporary file first and only replace the destination upon passing validation.
- Non-Destructive: Never overwrites an existing local file if it differs (raises an error to preserve local edits).
- Resume / Retry: Network retries up to 3 times with exponential backoff; skips already-verified files.
"""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time
from urllib.request import urlopen
import zipfile

# Project root directory (two levels up from data_extraction/download.py)
ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    """
    Compute the SHA-256 hexadecimal checksum of a file.

    Uses Python 3.11+ `hashlib.file_digest` to efficiently stream file contents
    without loading large multi-megabyte or gigabyte files entirely into memory.
    """
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(item: dict, root: Path) -> None:
    """
    Download a single file entry from `sources.json` and verify its integrity.

    Workflow:
    1. If the file already exists locally:
       - Verify its SHA-256 hash matches the expected hash in sources.json.
       - If it matches, skip downloading (idempotent resume).
       - If it differs, abort to prevent overwriting modified local data.
    2. If the file does not exist:
       - Stream the download in 1 MB chunks into a temporary file.
       - Retry up to 3 times with exponential backoff on network failures.
       - Verify the downloaded file's SHA-256 hash.
       - Atomically replace the temporary file to the final destination path.
    """
    target = root / item['path']

    # Step 1: Check existing local file
    if target.exists():
        if digest(target) != item['sha256']:
            raise ValueError(f"Existing file differs from expected hash; preserved without overwrite: {target}")
        print(f"Checked (already valid): {item['path']}", flush=True)
        return

    # Ensure parent directory exists (e.g. data/job_bank, data/statcan)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Step 2: Download with retry and atomic write
    for attempt in range(3):
        temporary = None
        try:
            # Create a temporary file in the same directory to allow atomic filesystem replace
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as out:
                temporary = Path(out.name)
                # Stream file over HTTP in 1 MB chunks
                with urlopen(item['url'], timeout=120) as response:
                    while chunk := response.read(1024 * 1024):
                        out.write(chunk)

            # Validate cryptographic hash against sources.json
            if digest(temporary) != item['sha256']:
                raise ValueError(f"Downloaded snapshot checksum does not match manifest: {item['url']}")

            # Atomically move temporary file to final target location
            temporary.replace(target)
            print(f"Downloaded and verified: {item['path']}", flush=True)
            return

        except ValueError:
            # Re-raise checksum mismatch or validation error immediately without retrying
            raise
        except Exception as err:
            # Handle transient network / connection errors
            if attempt == 2:
                print(f"Failed to download {item['path']} after 3 attempts: {err}")
                raise
            sleep_sec = 2 ** attempt
            print(f"Download error on {item['path']}: {err}. Retrying in {sleep_sec}s (attempt {attempt + 1}/3)...")
            time.sleep(sleep_sec)
        finally:
            # Clean up temporary file if download or validation failed
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def main():
    """CLI entrypoint for downloading and extracting Canadian job market datasets."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--stage',
        choices=['01', '02', 'all'],
        default='all',
        help=(
            "Which study stage to download: "
            "'01' = Indeed daily indices (4 CSVs in data/); "
            "'02' = Job Bank monthly microdata & Statistics Canada tables; "
            "'all' = both stages (default: 'all')"
        )
    )
    parser.add_argument(
        '--root',
        type=Path,
        default=ROOT,
        help="Destination project root directory (default: parent directory of data_extraction/)"
    )
    args = parser.parse_args()

    # Load manifest of sources, URLs, relative paths, and SHA-256 hashes
    manifest_path = Path(__file__).with_name('sources.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))

    # Download manifest files matching the requested stage
    for item in manifest['files']:
        if args.stage in ('all', item['stage']):
            download(item, args.root)

    # If Stage 02 or 'all' is selected, extract the Statistics Canada ZIP archive
    if args.stage in ('02', 'all'):
        folder = args.root / 'data/statcan'
        zip_path = folder / '14100444-eng.zip'

        if zip_path.exists():
            with zipfile.ZipFile(zip_path) as archive:
                # Extract both data CSV and metadata CSV from the StatCan archive
                for name in ['14100444.csv', '14100444_MetaData.csv']:
                    payload = archive.read(name)
                    target = folder / name

                    if target.exists():
                        # Verify existing extracted file against the archive's internal checksum
                        if digest(target) != hashlib.sha256(payload).hexdigest():
                            raise ValueError(f"Existing extracted file differs from archive content: {target}")
                    else:
                        # Write payload atomically
                        with tempfile.NamedTemporaryFile(dir=folder, delete=False) as f:
                            f.write(payload)
                            temporary = Path(f.name)
                        temporary.replace(target)

            print("Statistics Canada table extraction checked and verified.")


if __name__ == '__main__':
    main()
