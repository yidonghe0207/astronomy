"""Step 3: build the interactive app (an HR diagram linked to a 3D map).

It reads the cached Gaia data, puts it into app_template.html, and writes
project24/neighborhood_app.html: a single web page you can open in any browser.

Data source: ESA Gaia DR3 (Gaia Collaboration 2023), https://gea.esac.esa.int/archive/
Run from the repo root:   python3 project24/make_app.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from get_data import clean, load_catalogue_ids, load_stars

stars = clean(load_stars())

# Add catalogue names: Hipparcos (HIP) if the star has one, otherwise Tycho-2 (TYC)
ids = load_catalogue_ids()
stars = stars.merge(ids, on="source_id", how="left")
stars["name"] = None
has_tyc, has_hip = stars["tyc"].notna(), stars["hip"].notna()
stars.loc[has_tyc, "name"] = "TYC " + stars.loc[has_tyc, "tyc"].astype(str)
stars.loc[has_hip, "name"] = "HIP " + stars.loc[has_hip, "hip"].astype(str)



def base36(n):
    """Write a whole number in base 36 (digits 0-9 then a-z): the same number, in fewer characters."""
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while n:
        n, r = divmod(n, 36)
        out = digits[r] + out
    return out or "0"


# Mix the stars into a random but repeatable order (fixed seed), so the page never
# depends on how the archive happened to sort them.
stars = stars.sample(frac=1, random_state=24).reset_index(drop=True)

# Store numbers as whole numbers to keep the page small (the app divides them back).
data = {
    "c": (stars["bp_rp"] * 100).round().astype(int).tolist(),
    "g": (stars["abs_g"] * 100).round().astype(int).tolist(),
    "x": (stars["x"] * 10).round().astype(int).tolist(),
    "y": (stars["y"] * 10).round().astype(int).tolist(),
    "z": (stars["z"] * 10).round().astype(int).tolist(),
    # Gaia DR3 source_id in base 36 (shorter text); the app turns it back into the usual number
    "id": [base36(int(sid)) for sid in stars["source_id"]],
    "names": {i: n for i, n in enumerate(stars["name"]) if isinstance(n, str)},
}

template = (HERE / "app_template.html").read_text()
page = template.replace("__STAR_DATA__", json.dumps(data, separators=(",", ":")))
out = HERE / "neighborhood_app.html"
out.write_text(page)
print(f"{len(data['names']):,} stars have a HIP or TYC name")
print(f"wrote {out} with {len(stars):,} stars ({out.stat().st_size / 1e6:.1f} MB)")
