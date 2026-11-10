"""Step 1: download every Gaia DR3 star within 100 parsecs and cache it in data/.

Data source: ESA Gaia mission, Gaia Data Release 3 (Gaia Collaboration 2023),
queried anonymously from the Gaia Archive, https://gea.esac.esa.int/archive/

Run from the repo root:   python3 project24/get_data.py
"""
from pathlib import Path

import numpy as np
from astroquery.gaia import Gaia

CACHE = Path("data/gaia_100pc.csv")


def load_stars():
    """Return a pandas table of nearby stars, downloading only the first time."""
    import pandas as pd

    if CACHE.exists():
        return pd.read_csv(CACHE)

    # The archive returns at most 50,000 rows per query, but ~300,000 stars match.
    # So we ask in slices of parallax, each small enough to stay under that cap.
    edges = [10, 10.4, 10.8, 11.3, 11.8, 12.4, 13.1, 14.0, 15.2, 17.0, 20.0, 27.0, 1e6]
    pieces = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        query = f"""
        SELECT source_id, l, b, parallax, bp_rp, phot_g_mean_mag, ruwe, phot_bp_rp_excess_factor,
               phot_g_mean_mag + 5*LOG10(parallax) - 10 AS abs_g
        FROM gaiadr3.gaia_source
        WHERE parallax > {lo} AND parallax <= {hi} AND parallax_over_error > 10
          AND phot_bp_mean_flux_over_error > 10 AND phot_rp_mean_flux_over_error > 10
        """  # same quality cuts as the starter; parallax > 10 mas <=> closer than 100 pc
        piece = Gaia.launch_job_async(query).get_results().to_pandas()
        print(f"parallax {lo}-{hi} mas: {len(piece)} stars")
        if len(piece) >= 50000:
            raise RuntimeError("A slice hit the 50,000-row cap; add more edges.")
        pieces.append(piece)
    stars = pd.concat(pieces, ignore_index=True)

    # Turn (galactic longitude l, galactic latitude b, distance) into x, y, z in parsecs.
    # The Sun sits at (0, 0, 0); +x points to the Galactic Centre, +z to the Galactic north pole.
    dist = 1000.0 / stars["parallax"]  # parallax in milliarcseconds -> distance in parsecs
    l, b = np.radians(stars["l"]), np.radians(stars["b"])
    stars["dist_pc"] = dist
    stars["x"] = dist * np.cos(b) * np.cos(l)
    stars["y"] = dist * np.cos(b) * np.sin(l)
    stars["z"] = dist * np.sin(b)

    CACHE.parent.mkdir(exist_ok=True)
    stars.to_csv(CACHE, index=False)
    return stars


def clean(stars):
    """Keep only stars with trustworthy measurements (Gaia's standard quality checks).

    - ruwe < 1.4: Gaia's fit of the star's motion across the sky is good. Large values
      mean a blended or double source, whose parallax (and so distance) can be wrong.
    - colour-excess check (Riello et al. 2021): the blue (BP) and red (RP) brightness
      add up to the total (G) brightness, as they should for a single, isolated star.
    Without these cuts, a blob of faint, distant stars with bad parallaxes pretends to be
    nearby and fills the gap between the main sequence and the white dwarfs.
    """
    c = stars["bp_rp"]
    expected = np.where(
        c < 0.5, 1.154360 + 0.033772 * c + 0.032277 * c**2,
        np.where(c < 4.0, 1.162004 + 0.011464 * c + 0.049255 * c**2 - 0.005879 * c**3,
                 1.057572 + 0.140537 * c))
    excess = stars["phot_bp_rp_excess_factor"] - expected
    scatter = 0.0059898 + 8.817481e-12 * stars["phot_g_mean_mag"] ** 7.618399
    good = (stars["ruwe"] < 1.4) & (np.abs(excess) < 3 * scatter)
    return stars[good].reset_index(drop=True)


def is_white_dwarf(stars):
    """Rough cut: white dwarfs are much fainter than main-sequence stars of the same colour.
    Everything below the line  abs_g = 10 + 2.5 * bp_rp  counts as a white dwarf."""
    return stars["abs_g"] > 10 + 2.5 * stars["bp_rp"]


if __name__ == "__main__":
    stars = load_stars()
    print(len(stars), "stars within 100 pc, saved to", CACHE)
    print(len(clean(stars)), "pass the quality checks")
