"""Fetch Toronto Open Data sources for shouttest.

Downloads the Licensed Dog and Cat Names CSV + the Off Leash Areas GeoJSON.
Idempotent: skips files already on disk.
"""
from pathlib import Path
import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

CKAN = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset"

# Licensed Dog and Cat Names — "Since 2020" consolidated CSV (datastore-active)
NAMES_DS = "licensed-dog-and-cat-names"
NAMES_URL = (
    f"{CKAN}/{NAMES_DS}/resource/"
    "cad71142-964a-4b2d-a86c-d34b5d2a5369/download/"
    "licensed-dog-and-cat-names-since-2020.csv"
)

# Off Leash Areas — WGS84 GeoJSON (83 point features)
OFFLEASH_DS = "off-leash-areas"
OFFLEASH_URL = (
    f"{CKAN}/{OFFLEASH_DS}/resource/"
    "89ee1e98-f923-4441-830c-b13b6e907058/download/"
    "off-leash-areas-4326.geojson"
)


def download(name: str, url: str) -> None:
    out = RAW / name
    if out.exists():
        print(f"skip {name} ({out.stat().st_size / 1e3:.1f} KB)")
        return
    print(f"download -> {name}")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with out.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print(f"  done: {out.stat().st_size / 1e3:.1f} KB")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    download("pet_names.csv", NAMES_URL)
    download("off_leash_areas.geojson", OFFLEASH_URL)


if __name__ == "__main__":
    main()
