# Downloaded job-market data

Downloaded on 2026-09-07. Original analysis files remain in the parent folder.

- `job_bank/`: all English CSV resources available in the Job Bank catalogue at download time. `catalog.json` preserves the source metadata; `download_manifest.json` records source URLs, row counts, encodings, separators, and SHA-256 checksums. French copies are excluded to avoid counting translated records twice.
- `statcan/14100444.csv`: full Statistics Canada table 14-10-0444-01, vacancies and offered hourly wages by occupation and geography. The source ZIP, metadata CSV, and download manifest are included.

Job Bank files can use UTF-16 encoding and tab separators despite the `.csv` extension. Use the encoding and separator in each manifest entry when loading a file. Check duplicates and schema differences before combining months. These are advertised records, not a complete count of Canadian vacancies.

For Statistics Canada, filter `Statistics` to `Job vacancies`, select the occupation codes and provinces of interest, and compare the same `REF_DATE`. Inspect `STATUS`, `UOM`, and `SCALAR_FACTOR`. Missing or suppressed values are not zero. Do not sum overlapping geography or occupation totals. These are survey estimates, not individual advertisements.

Sources:

- [Job Bank catalogue](https://open.canada.ca/data/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072)
- [Statistics Canada table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410044401)
