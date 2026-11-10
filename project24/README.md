# Project 24: Our neighborhood in 3D

**Question:** What does every star within 100 parsecs (~326 light-years) of the Sun look like, and where are the white dwarfs?

## The app

`neighborhood_app.html` is the Thursday prototype: an HR diagram linked to a 3D map.
Drag a box or lasso on the HR diagram and the 3D map shows where those stars are.
Buttons give quick selections (white dwarfs, giants, Sun-like stars, red dwarfs, and the Hyades star cluster).
To use it, download the file and open it in a web browser (it needs internet access to load the Plotly library).

## How to rebuild everything (run from the repo root)

```bash
python3 project24/get_data.py      # downloads ~300,000 stars once (about 2 minutes), cached in data/
python3 project24/static_plots.py  # makes the PNG plots in plots/
python3 project24/make_app.py      # builds project24/neighborhood_app.html
```

## What the code does

1. **get_data.py** asks the Gaia Archive for every star with parallax > 10 milliarcseconds (closer than 100 pc).
   The archive returns at most 50,000 rows per query, so it asks in 12 slices of parallax.
   It then turns each star's sky position and distance into x, y, z coordinates with the Sun at the centre.
2. **Quality checks** (`clean()` in get_data.py): 306,517 stars come back, but about 91,000 have unreliable
   measurements. Most are faint, distant stars in crowded parts of the sky whose parallax was mis-measured,
   so they *look* close and faint. We keep stars with RUWE < 1.4 and a good BP/RP colour-excess factor
   (Riello et al. 2021), leaving 215,317 stars. See `plots/24_quality_cuts_before_after.png`.
3. **White dwarfs** are picked with a simple line on the HR diagram: absolute G > 10 + 2.5 × (BP − RP).
   That gives 15,373 candidates, in line with the known white-dwarf density near the Sun.

## Findings so far

- White dwarfs are spread evenly through the whole 100 pc bubble. They are old, so they have had billions of years to mix.
- The nearest white dwarf in our clean sample is 4.3 pc away (van Maanen's Star). Sirius B, at 2.6 pc, is missing because it sits right next to very bright Sirius.
- The Hyades cluster (47 pc away in Taurus) shows up as a clump of bright stars in the 3D map.

## Data source

ESA Gaia mission, Gaia Data Release 3: Gaia Collaboration, Vallenari et al. (2023), *Astronomy & Astrophysics* 674, A1.
Queried anonymously from the Gaia Archive, https://gea.esac.esa.int/archive/.
Quality cut for the colour-excess factor: Riello et al. (2021), *A&A* 649, A3.
