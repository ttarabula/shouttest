"""Quick look at both datasets before building features."""
from pathlib import Path
import json
import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def names_eda() -> None:
    df = pd.read_csv(RAW / "pet_names.csv")
    print("=== pet_names.csv ===")
    print(f"rows: {len(df):,}")
    print(f"cols: {list(df.columns)}")
    print()

    # How many ranks per (year, type)?
    coverage = df.groupby(["Year", "ANIMAL_TYPE"]).agg(
        distinct_names=("ANIMAL_NAME", "nunique"),
        total_pets=("AnimalCnt", "sum"),
        max_rank=("Rank", "max"),
    ).reset_index()
    print(coverage.to_string(index=False))
    print()

    # Focus on 2025 (last full year)
    for kind in ("DOG", "CAT"):
        sub = df[(df["Year"] == 2025) & (df["ANIMAL_TYPE"] == kind)]
        total = sub["AnimalCnt"].sum()
        top = sub.nlargest(15, "AnimalCnt")[["Rank", "ANIMAL_NAME", "AnimalCnt"]]
        print(f"--- {kind} 2025 — {len(sub):,} names, {total:,} registered ---")
        print(top.to_string(index=False))
        print(f"  tail count (rank {sub['Rank'].max()}): {sub.nsmallest(1, 'Rank', keep='last')['AnimalCnt'].values}")
        print()


def offleash_eda() -> None:
    gj = json.loads((RAW / "off_leash_areas.geojson").read_text())
    feats = gj["features"]
    print(f"=== off_leash_areas.geojson — {len(feats)} parks ===")

    props = pd.DataFrame([f["properties"] for f in feats])
    print(f"cols: {list(props.columns)}")
    print()
    print("--- area_sqm ---")
    a = pd.to_numeric(props["area_sqm"], errors="coerce").dropna()
    print(f"n={len(a)} min={a.min():.0f} p25={a.quantile(.25):.0f} "
          f"median={a.median():.0f} p75={a.quantile(.75):.0f} max={a.max():.0f}")
    print(f"total sqm: {a.sum():,.0f}  mean: {a.mean():.0f}")
    print()
    print("--- amenity flags ---")
    for col in ("fenced_perimeter", "lit_area", "small_dog_area",
                "comm_dog_walkers_allowed", "surface_material"):
        print(f"  {col}:")
        print(props[col].value_counts(dropna=False).head(8).to_string())
        print()

    print("--- 5 biggest parks ---")
    props["area_sqm_num"] = pd.to_numeric(props["area_sqm"], errors="coerce")
    big = props.nlargest(5, "area_sqm_num")[
        ["location_name", "address", "area_sqm_num", "fenced_perimeter"]
    ]
    print(big.to_string(index=False))
    print()
    print("--- 5 smallest parks ---")
    small = props.nsmallest(5, "area_sqm_num")[
        ["location_name", "address", "area_sqm_num", "fenced_perimeter"]
    ]
    print(small.to_string(index=False))


if __name__ == "__main__":
    names_eda()
    print()
    offleash_eda()
