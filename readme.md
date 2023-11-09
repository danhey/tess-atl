## TESS-ATL

Compute the asteroseismic detection probability for a given target.

### Installation

```bash
pip install tess-atl
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