"""Step 2: static plots of the full 100-parsec sample.

Data source: ESA Gaia DR3 (Gaia Collaboration 2023), https://gea.esac.esa.int/archive/
Run from the repo root:   python3 project24/static_plots.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from get_data import clean, is_white_dwarf, load_stars


raw = load_stars()
stars = clean(raw)
wd = is_white_dwarf(stars)

# --- Plot 0: why we need quality cuts (before vs after) ---
fig, axes = plt.subplots(1, 2, figsize=(12, 7), sharex=True, sharey=True)
for ax, table, title in [(axes[0], raw, "Everything with parallax > 10 mas"),
                         (axes[1], stars, "After Gaia quality checks")]:
    ax.hexbin(table["bp_rp"], table["abs_g"], gridsize=250, bins="log", cmap="viridis", mincnt=1)
    ax.set_title(f"{title}\n({len(table):,} stars)")
    ax.set_xlabel("Colour BP - RP  (blue -> red)")
axes[0].invert_yaxis(); axes[0].set_ylabel("Absolute G magnitude  (bright -> up)")
axes[0].annotate("fake 'nearby' stars:\nfaint, distant stars with\nmis-measured parallaxes", xy=(1.8, 15.5),
                 xytext=(-1.5, 19.3), color="crimson", arrowprops=dict(color="crimson", arrowstyle="->"))
fig.text(0.01, 0.005, "Data: ESA Gaia DR3", fontsize=7, color="gray")
fig.savefig("plots/24_quality_cuts_before_after.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"{len(raw)} stars downloaded, {len(stars)} pass quality checks, {wd.sum()} white-dwarf candidates")

# --- Plot 1: HR diagram of every star, white dwarfs outlined by the cut line ---
fig, ax = plt.subplots(figsize=(7, 8))
hb = ax.hexbin(stars["bp_rp"], stars["abs_g"], gridsize=300, bins="log", cmap="viridis", mincnt=1)
fig.colorbar(hb, ax=ax, label="Number of stars per cell")
xs = [-0.6, 1.9]
ax.plot(xs, [10 + 2.5 * x for x in xs], "r--", lw=1.2, label=f"White-dwarf cut ({wd.sum():,} stars below)")
ax.text(1.75, 1.2, "giants", color="gray"); ax.text(2.6, 8.5, "main sequence", color="gray", rotation=-38)
ax.text(-0.7, 17.2, "white dwarfs", color="gray")
ax.invert_yaxis()
ax.set_xlabel("Colour BP - RP  (blue -> red)"); ax.set_ylabel("Absolute G magnitude  (bright -> up)")
ax.set_title(f"{len(stars):,} Gaia DR3 stars within 100 pc (quality-checked)")
ax.legend(loc="upper right")
fig.text(0.01, 0.005, "Data: ESA Gaia DR3", fontsize=7, color="gray")
fig.savefig("plots/24_hr_diagram_full_100pc.png", dpi=150, bbox_inches="tight")

# --- Plot 2: where are the white dwarfs? Two flat views of the 3D bubble ---
fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
views = [("x", "y", "x (pc, toward Galactic Centre)", "y (pc, direction of rotation)", "Seen from above the Galaxy"),
         ("x", "z", "x (pc, toward Galactic Centre)", "z (pc, toward Galactic north)", "Seen edge-on")]
for ax, (h, v, hl, vl, title) in zip(axes, views):
    ax.scatter(stars.loc[~wd, h], stars.loc[~wd, v], s=0.2, c="lightgray", alpha=0.3, rasterized=True, label="other stars")
    ax.scatter(stars.loc[wd, h], stars.loc[wd, v], s=1.5, c="tab:blue", rasterized=True, label="white dwarfs")
    ax.plot(0, 0, marker="*", ms=14, c="gold", mec="k", label="Sun")
    ax.set_aspect("equal"); ax.set_xlabel(hl); ax.set_ylabel(vl); ax.set_title(title)
legend = axes[0].legend(loc="upper right", fontsize=8)
for handle, size in zip(legend.legend_handles, [20, 20, 60]):
    handle.set_sizes([size]) if hasattr(handle, "set_sizes") else handle.set_markersize(8)
fig.suptitle(f"Where the {wd.sum():,} white dwarfs within 100 pc are")
fig.text(0.01, 0.01, "Data: ESA Gaia DR3", fontsize=7, color="gray")
fig.savefig("plots/24_white_dwarf_map.png", dpi=150, bbox_inches="tight")
print("saved 3 plots in plots/")
