## TESS-ATL

Compute the asteroseismic detection probability for a given target.

### Installation

```bash
pip install tess-atl
```

### Usage

#### Command line

`tess-atl` will query the relevant catalogues to calculate probabilities. Inputs from the command line 
```bash
atl --target <target> 
```

#### Python

```python
from tess_atl import calc_detection_probability
calc_detection_probability(
    tess_magnitude,
    temperature,
    radius,
    logg,
    sectors, # The number of sectors the target is observed in
    cadence # The cadence of the observations (20, 120)
)
```