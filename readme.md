## TESS-ATL

Compute the asteroseismic detection probability for a given target.

- [TESS-ATL](#tess-atl)
  - [Installation](#installation)
  - [Citing](#citing)
  - [Usage](#usage)
    - [Command line](#command-line)
    - [Python](#python)
    - [Bulk queries](#bulk-queries)
  - [Full catalog](#full-catalog)
  - [Target lists](#target-lists)

### Installation

From the terminal;
```bash
pip install tess-atl
```


### Citing

If you use either the ATL catalog or this software tool in your work, please cite https://arxiv.org/abs/2403.02489
```tex
@preprint{hey2024precise,
      title={Precise Time-Domain Asteroseismology and a Revised Target List for TESS Solar-Like Oscillators}, 
      author={Daniel Hey and Daniel Huber and Joel Ong and Dennis Stello and Daniel Foreman-Mackey},
      year={2024},
      eprint={2403.02489},
      archivePrefix={arXiv},
      primaryClass={astro-ph.SR}
}
```
### Usage

#### Command line

`tess-atl` will query the relevant catalogs to calculate probabilities. Input target stars from the command line can take the form of a TIC ID, a Gaia DR2 ID, or a target name.

```bash
atl --target 'alf Men' 
```

By default, the sectors of targeted observation will be automatically calculated by tess-point. If you would like to specify the sectors, you can do so with the `--sectors` flag. Noise for cadence is interpolated from prior work, so this only works for 20 and 120 second cadences.

```bash
atl --target 'pi Men' --cadence 20
```
will give the following
```bash
ID                                                                   261136679
sectors                                                                     19
KIC                                                                       <NA>
GAIA                                                       4623036865373793408
Tmag                                                                    5.1054
ra                                                                   84.291188
dec                                                                  -80.46912
Teff                                                                    5992.1
logg                                                                    4.3589
rad                                                                    1.14889
magnitude_difference                                                  0.020912
dr3_source_id                                              4623036865373793408
proper_motion_propagation                                                 True
angular_distance                                                      0.122789
dr2_source_id                                              4623036865373793408
radius_gspphot                                                          1.2031
teff_gspspec                                                            6014.0
teff_gspphot                                                       5855.533203
logg_gspphot                                                            4.2235
logg_gspspec                                                              4.22
radius_flame                                                          1.204053
atl_teff                                                           5855.533203
atl_logg                                                                4.2235
atl_radius                                                              1.2031
Probability: 1.000, numax: 1864.345 uHz, dnu: 104.904 uHz, SNR: 0.066
```

If the target ID is already known, this can be supplied by specifying either `--tic` `--kic` or `--gaia` (DR2 only). Cross-matches will be performed automatically.

#### Python

Functions can be exposed for more direct access, if desired.

```python
from atl.atl import calc_detection_probability
calc_detection_probability(
    tess_magnitude,
    temperature, # in Kelvin
    radius, # in solar radii
    logg, # in dex
    sectors, # The number of sectors the target is observed in
    cadence # The cadence of the observations (20, 120)
)
```

#### Bulk queries

For users wishing to query more than a handful of stars and don't want to download the [full catalog](#full-catalog), you must use the appropriate Python functions. We have included functions for querying multiple Gaia IDs simultaneously (query.py). See the cli.py for additional details.

### Full catalog

The full catalog, calculated for every TESS star brighter than 12th magnitude is available in `catalog/`. Note that this catalog has the requirement that the predicted numax _must_ be greater than 240 microhertz. We leave in stars where the probability is NaN. In these scenarios, there is insufficient Gaia data to predict the probability.

To read in the table, download each separate chunk of the ATL and run the following Python code;
```python
import pandas as pd
atl = pd.concat([pd.read_csv(f'ATL_{i}.csv' for i in range(0, 5))])
```

The table schema is as follows;
| Column name   | Description                                                         |
| ------------- | ------------------------------------------------------------------- |
| ID            | TESS Input Catalog ID                                               |
| ra            | Right ascension (J2000)                                             |
| dec           | Declination (J2000)                                                 |
| dr3_source_id | Gaia DR3 source ID                                                  |
| Tmag          | TIC magnitude                                                       |
| atl_radius    | Radius used for calculation (Rsun)                                  |
| atl_teff      | Temperature used for calculation (K)                                |
| atl_logg      | Surface gravity used for calculation (dex)                          |
| numax         | Predicted numax (uHz)                                               |
| p_120         | Probability in 2 minute cadence at available sectors                |
| p_20          | Probability in 20 second cadence at available sectors               |
| p_120_1s      | Probability in 2 minute cadence assuming single-sector observation  |
| p_20_1s       | Probability in 20 second cadence assuming single-sector observation |
| Sectors       | Number of sectors target has fallen on TESS detectors               |

### Target lists

For convenience, we additionally provide target lists for the 20s and 2min cadence data for stars which have been targeted for observation. These are merged versions of the tables available [here](https://tess.mit.edu/public/target_lists/target_lists.html). 

These lists are available in the `catalog/` directory:

1. targets_120s.csv: 2 minute targets complete up to sector 77
2. targets_20s.csv: 20 second cadence targets complete up to sector 77. Note that these targets begin at Sector 27.
3. targets_120s_count.csv: Count of number of sectors each 2min target has been observed in.
4. targets_20s_count.csv: Count of number of sectors each 20s target has been observed in.

The scripts for producing these target lists can be found in `scripts/make_target_list.py`.