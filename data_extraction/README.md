# Data extraction, in study order

## 01 — Posting indices

Four Canadian CSVs from [Indeed Hiring Lab](https://github.com/hiring-lab/job_postings_tracker/tree/master/CA). Their URLs in `sources.json` use a fixed Git revision. Outputs go to `data/` for the first-stage notebooks. The source repository includes its data licence.

## 02 — Posting records and vacancy counts

- [Job Bank catalogue](https://open.canada.ca/data/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072): 43 English monthly files, January 2023–July 2026. The source catalogue uses the Open Government Licence – Canada. Only one language is downloaded. Files can use different encodings and separators; consult the original download manifest locally before combining them.
- [Statistics Canada table 14-10-0444-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410044401): the full ZIP, data CSV, and metadata CSV. The recorded data span Q1 2015–Q1 2026. Follow Statistics Canada's data-use terms.

`sources.json` records the original URLs and SHA-256 hashes. `download.py` retrieves those snapshots, verifies them, and extracts the two expected Statistics Canada CSVs. It never overwrites a differing existing file. Re-run after an interrupted download to resume at the file level.

To discover future releases, the official catalogue endpoints are:

```text
https://open.canada.ca/data/api/action/package_show?id=ea639e28-c0fc-48bf-b5dd-b8899bd43072
https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/14100444/en
```

Updating to a new snapshot is a separate study step: review the source metadata, record new hashes and dates, and keep the prior analysis labelled with its original period. Stage 02 analysis has not been started.
