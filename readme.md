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
```bash
atl --target 'alf Men' 
```

By default, the sectors of targeted observation will be automatically calculated by tess-point. If you would like to specify the sectors, you can do so with the `--sectors` flag. Noise for cadence is interpolated from prior work, so this only works for 20 and 120 second cadences.

```bash
atl --target 'pi Men' --cadence 20
```
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