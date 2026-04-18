"""Build shouttest derived data: parks.json, names.json, and a combined site payload.

Notes:
- Pet-names dataset on open.toronto.ca drops off a cliff after 2023 (2024 has
  ~2.8k dogs total vs ~18k in 2020-23, 2025-26 look incomplete). Use 2023 as
  the canonical year for the Shout Test frequency distribution.
- Only the top-200 names per year are published, so the distribution is
  upper-bounded at names that are "popular enough to chart". We treat
  `count / sum(top200)` as the probability a randomly-sampled-from-top-200 dog
  has that name, and are honest about that framing in the UI.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SITE_DATA = ROOT / "site" / "data"

CANON_YEAR = 2023


def build_names() -> list[dict]:
    df = pd.read_csv(RAW / "pet_names.csv")
    dogs = df[(df["Year"] == CANON_YEAR) & (df["ANIMAL_TYPE"] == "DOG")].copy()
    total = int(dogs["AnimalCnt"].sum())
    dogs["freq"] = dogs["AnimalCnt"] / total
    dogs = dogs.sort_values("Rank")
    return [
        {
            "rank": int(r["Rank"]),
            "name": str(r["ANIMAL_NAME"]).title(),
            "count": int(r["AnimalCnt"]),
            "freq": float(r["freq"]),
        }
        for _, r in dogs.iterrows()
    ]


def park_capacity(area_sqm: float | None) -> int:
    """Rough estimate of dogs present at a given moment on a busy afternoon.
    Piecewise by park area; calibrated for whimsy, not precision."""
    if area_sqm is None:
        return 8
    if area_sqm < 500:
        return 3
    if area_sqm < 2000:
        return 8
    if area_sqm < 5000:
        return 15
    if area_sqm < 15000:
        return 25
    return 40


def build_parks() -> list[dict]:
    gj = json.loads((RAW / "off_leash_areas.geojson").read_text())
    out = []
    for f in gj["features"]:
        p = f["properties"]
        geom = f["geometry"]
        # MultiPoint -> take first (and only) point
        coords = geom["coordinates"][0] if geom["type"] == "MultiPoint" else geom["coordinates"]
        area = p.get("area_sqm")
        try:
            area_f = float(area) if area is not None else None
        except (TypeError, ValueError):
            area_f = None
        out.append({
            "id": int(p["locationid"]),
            "name": p["location_name"],
            "address": p["address"],
            "lon": coords[0],
            "lat": coords[1],
            "area_sqm": area_f,
            "dogs_present": park_capacity(area_f),
            "fenced": p.get("fenced_perimeter"),
            "lit": (p.get("lit_area") or "").strip(),
            "small_dog_area": p.get("small_dog_area"),
            "surface": p.get("surface_material"),
            "hours": p.get("hours_of_operation"),
            "url": p.get("url"),
        })
    out.sort(key=lambda x: x["name"])
    return out


def main() -> None:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    names = build_names()
    parks = build_parks()
    total = sum(n["count"] for n in names)

    payload = {
        "year": CANON_YEAR,
        "total_dogs_in_distribution": total,
        "note": (
            f"Frequencies are drawn from the top-200 licensed dog names in "
            f"Toronto, {CANON_YEAR}. Names outside the top 200 are not in the "
            f"dataset. Park occupancy is a piecewise estimate based on area."
        ),
        "names": names,
        "parks": parks,
    }
    (SITE_DATA / "shouttest.json").write_text(json.dumps(payload, indent=2))

    # Console summary
    print(f"names: {len(names)} (canonical year {CANON_YEAR}, n={total:,})")
    top = names[:10]
    print("top 10:")
    for n in top:
        print(f"  {n['rank']:>3}. {n['name']:<12} {n['count']:>4}  ({n['freq']*100:.2f}%)")
    print(f"parks: {len(parks)}")
    # Example shout
    luna = next((n for n in names if n["name"].lower() == "luna"), None)
    if luna:
        hp = next((p for p in parks if "High Park" in p["name"]), None)
        if hp:
            d = hp["dogs_present"]
            p_hit = luna["freq"]
            expected = d * p_hit
            at_least_one = 1 - (1 - p_hit) ** d
            print(f"\nExample: yell 'LUNA' at {hp['name']} "
                  f"(~{d} dogs): expected {expected:.2f} heads turn, "
                  f"P(at least one) = {at_least_one*100:.0f}%")


if __name__ == "__main__":
    main()
