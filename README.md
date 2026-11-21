# Major → Outcomes

A small website that shows career outcomes for each **Rutgers–New Brunswick** bachelor's major
(earnings, employment, employers, job growth) next to national and New Jersey benchmarks.
Every source is joined on federal **CIP codes** (4-digit, e.g. `11.01` Computer Science).
Rutgers–Camden and Rutgers–Newark are intentionally excluded.

Features: search majors, compare up to 3 side by side, earnings-over-time charts
(1–10 years after graduation and by graduating class), Rutgers vs. national, industry and region
of employment, top employers, related occupations with BLS growth, and a caveats section for every source.

## Run it

```bash
pip install -r requirements.txt
python -m pipeline.build      # raw files -> data/processed/majors.json + meta.json
python run.py                 # http://127.0.0.1:5000
pytest -q
```

The processed JSON is committed, so `python run.py` works without rebuilding.
Chart.js 4.4.1 is vendored in `app/static/vendor/` (MIT), so the site works offline.

## Data sources

| Source | What it gives | File(s) |
|---|---|---|
| [College Scorecard field of study](https://collegescorecard.ed.gov/data/) (Oct 2026 release) | IRS-based median earnings at 1, 4, 5, 7 yrs for Rutgers–NB (UNITID 186380) and national medians (`EARN_MDN_*_NAT`), median debt | `data/raw/scorecard/` |
| [Census PSEO](https://lehd.ces.census.gov/data/pseo/) (NJ, Aug 2026 release) | Earnings p25/p50/p75 at 1, 5, 10 yrs by CIP-4 for Rutgers–NB (`00262900`) and NJ statewide; by graduating cohort; industry (NAICS sector) and Census-division destinations by CIP-2 | `data/raw/pseo/` |
| [Rutgers First-Destination Survey](https://careers46.rutgers.edu/public/new_webpage_gradsurveyHome.cfm) | Starting salary, outcomes and knowledge rate, top employers and grad schools | `data/raw/rutgers_fds/` |
| [NY Fed: Labor Market for Recent College Graduates](https://www.newyorkfed.org/research/college-labor-market) | Unemployment, underemployment, early/mid-career wages by major | `data/raw/nyfed/` |
| [BLS Employment Projections](https://www.bls.gov/emp/tables.htm) 2025–35 + [NCES CIP→SOC crosswalk](https://nces.ed.gov/ipeds/cipcode/resources.aspx?y=56) | Occupations linked to each major, 10-yr growth, median wage | `data/raw/bls/`, `data/raw/nces/` |
| [NACE Winter 2026 Salary Survey summary](https://naceweb.org/job-market/compensation/class-of-2026-salary-projections-are-promising) | Projected average starting salary for 4 broad categories | `data/crosswalks/nace_2026.csv` |

Not used: ACS/IPUMS microdata (needs an IPUMS account; the NY Fed tables are built from ACS),
and LinkedIn (scraping is against its terms).

### Notes on collection (Nov 2026)

* The raw files were downloaded with a regular browser; the URLs are in `pipeline/config.py`.
  `python -m pipeline.fetch` re-downloads anything missing.
* **First-Destination Survey:** careers46.rutgers.edu was returning a server error on 2026-11-21, so the
  committed data are parsed from Internet Archive snapshots of the public pages
  (14 school-level pages including the all-campus summary, mostly Class of 2024, plus the major-level pages that were archived:
  Computer Science and Women's & Gender Studies with stats). When the site is back,
  `python -m pipeline.fetch --fds` scrapes every school and major page into `fds_live.json`,
  which the build then prefers.
* PSEO confirms Rutgers–New Brunswick, Camden and Newark are all in the NJ release; only New Brunswick is used.

## How the join works

* `pipeline/scorecard.py`, `pipeline/pseo.py`, `pipeline/fds.py`, `pipeline/national.py` each load one source.
* `pipeline/build.py` takes every 4-digit CIP that Rutgers–NB reports in Scorecard or PSEO and attaches:
  Scorecard (Rutgers + national), PSEO (Rutgers + NJ + cohorts + CIP-2 flows), FDS (school-level, plus
  major-level when available), NY Fed, BLS and NACE.
* Hand-built crosswalks live in `data/crosswalks/`:
  `fds_major_cip.csv` (Rutgers major → CIP), `cip4_fds_school.csv` (CIP → school),
  `nyfed_major_cip.csv` (NY Fed major → CIP prefix, longest prefix wins), `nace_2026.csv`.
* Caveat text shown on the site is in `pipeline/caveats.py`.

## Layout

```
app/            Flask app (templates, CSS, charts.js, vendored Chart.js)
pipeline/       download, parse, join -> data/processed
data/raw/       source files as downloaded
data/crosswalks hand-built mappings
data/processed  majors.json, meta.json (what the site reads)
tests/
```
