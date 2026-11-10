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
from get_data import clean, load_stars

stars = clean(load_stars())

# Shuffle the stars (with a fixed seed, so the file is the same every run). The app
# shows at most 25,000 stars in 3D, and taking the first ones of a shuffled list
# gives a fair random sample.
stars = stars.sample(frac=1, random_state=24).reset_index(drop=True)

# Store numbers as whole numbers to keep the page small (the app divides them back).
data = {
    "c": (stars["bp_rp"] * 100).round().astype(int).tolist(),
    "g": (stars["abs_g"] * 100).round().astype(int).tolist(),
    "x": (stars["x"] * 10).round().astype(int).tolist(),
    "y": (stars["y"] * 10).round().astype(int).tolist(),
    "z": (stars["z"] * 10).round().astype(int).tolist(),
}

template = (HERE / "app_template.html").read_text()
page = template.replace("__STAR_DATA__", json.dumps(data, separators=(",", ":")))
out = HERE / "neighborhood_app.html"
out.write_text(page)
print(f"wrote {out} with {len(stars):,} stars ({out.stat().st_size / 1e6:.1f} MB)")
