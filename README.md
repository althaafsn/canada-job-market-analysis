# Canadian job-market analysis

An ordered record of an exploratory Canadian job-market study. The aim is to understand posting trends, then investigate actual advertised jobs and vacancy estimates by occupation and province.

## Study sequence

| Stage | Work | Status |
| --- | --- | --- |
| 01 | Indeed posting indices: sector trends, regional trends, correlations, and new/total index ratios | Analysis complete; see [summary](ANALYSIS_SUMMARY.md) |
| 02 | Download Job Bank posting records and Statistics Canada occupation vacancy estimates | Data acquired; analysis awaits instructions |

```text
data_analysis/
  01_posting_indices/       # Two notebooks and eight saved plots
data_extraction/
  download.py              # Download and verify sources
  sources.json             # Source URLs and snapshot checksums
  README.md                # Extraction stages and source details
data/                      # Local datasets; excluded from Git
ANALYSIS_SUMMARY.md         # Findings and limits of stage 01
requirements.txt
```

## Run from a fresh clone

```bash
git clone https://github.com/althaafsn/canada-job-market-analysis.git
cd canada-job-market-analysis
```

Requires Python 3.11 or later and several GB of free disk space for the full data collection. Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python data_extraction/download.py --stage 01
jupyter lab
```

Open `data_analysis/01_posting_indices/data_analysis.ipynb`, then `metro_job_analysis.ipynb`, and run their cells in order. The setup cell finds the repository root from either the notebook folder or root. The notebooks recreate the plots in their stage folder.

To acquire stage 02 data, without running a new analysis:

```bash
python data_extraction/download.py --stage 02
```

Use `--stage all` to download both stages. Downloads need no API key and use only the Python standard library. Existing files are checked against the source manifest and reused. A differing file is preserved and reported as an error. Partial downloads use a temporary file and are not treated as complete.

## Reproducibility and interpretation

The source manifest records the snapshots used in this study. Indeed URLs are pinned to a Git revision. Government download URLs can be revised; checksums detect changes and stop the download rather than silently replace the recorded snapshot. If a provider removes or revises a snapshot, exact reproduction needs that original source file. Government data are not archived in this repository.

The first analysis describes data through August 28, 2026. Its new/total ratio compares two indices: it does not measure hiring speed or prove that jobs are stale. See the summary for other limitations. Job Bank records and Statistics Canada survey estimates measure different things and must not be added together.

Raw datasets, local environments, editor settings, and personal planning notes are excluded from Git. Notebook results and plots are retained for reading without downloading data. Data remain subject to their publishers' licences; see [source details](data_extraction/README.md).

Project code is covered by the existing [MIT licence](LICENSE).
