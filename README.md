# shouttest

How many dogs will turn around if you yell a name at a Toronto off-leash area?

**Live:** https://ttarabula.github.io/shouttest/

A whimsical static site that crosses two City of Toronto open datasets:

- [Licensed Dog and Cat Names](https://open.toronto.ca/dataset/licensed-dog-and-cat-names/) — name frequency
- [Off-Leash Areas](https://open.toronto.ca/dataset/off-leash-areas/) — 83 parks with area + amenity flags

Given a name and a park, it estimates the expected number of heads that turn and the probability at least one dog reacts. There's also a printable **Off-Leash Bingo** card seeded from the top 100 names.

## Build

```
uv sync
uv run python scripts/fetch.py     # downloads raw CSV + GeoJSON to data/raw/
uv run python scripts/build.py     # writes site/data/shouttest.json
```

Serve `site/` however you like:

```
uv run python -m http.server 8787 --directory site
```

## Data caveats

- Only the top 200 licensed dog names per year are published, so anything off-chart is invisible to the calculator.
- **2023 is the canonical year.** 2024 drops to ~2,800 total dogs (vs ~18k in 2020–2023), and 2025–26 look incomplete. Rebuild when the city's next full year posts.
- Park occupancy is a piecewise estimate from `area_sqm` — calibrated for whimsy, not precision.
- Given *n* dogs and name-share *p*, expected heads = *n · p*; P(at least one) = 1 − (1 − *p*)ⁿ. We assume independence (dogs don't chain-react), which is wrong, but the correction is left as an exercise for the reader.

## Files

- `scripts/fetch.py` — pulls both CKAN resources (idempotent)
- `scripts/eda.py` — schema + coverage check
- `scripts/build.py` — computes the site payload
- `site/index.html` — the Shout Test calculator
- `site/bingo.html` — printable 5×5 bingo, seeded via URL hash

## Licence

Data: [Open Government Licence – Toronto](https://open.toronto.ca/open-data-license/).
Code: MIT.
