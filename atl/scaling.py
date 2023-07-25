from astropy.constants import sigma_sb
import numpy as np
import astropy.units as u

from .constants import *


def get_luminosity(radius, teff):
    return (
        (
            sigma_sb
            * 4
            * np.pi
            * ((radius * u.R_sun).to(u.m) ** 2)
            * (teff * u.Kelvin) ** 4
        )
        .to(u.L_sun)
        .value
    )


def get_numax(logg, teff):
    return NUMAX_SOLAR * (10 ** (logg) / (10**4.44)) * (teff / TEFF_SOLAR) ** (-0.5)


def get_dnu(radius, teff):
    #  from (14) eqn 21
    return DNU_SOLAR * (radius**-1.42) * ((teff / TEFF_SOLAR) ** 0.71)


# # calculate seismic parameters
# def calc_seis_params(teff, lum, logg):

#     teffred = TEFFREF_SOLAR*(lum**-0.093) # from (6) eqn 8. red-edge temp
#     rad = lum**0.5 * ((teff/TEFF_SOLAR)**-2) # Steffan-Boltzmann law
#     # numax = NUMAX_SOLAR*(rad**-1.85)*((teff/TEFF_SOLAR)**0.92) # from (14)
#     numax = NUMAX_SOLAR * (10**(logg) / 10**4.44) * (teff / TEFF_SOLAR)**(-0.5)
#     dnu = DNU_SOLAR*(rad**-1.42)*((teff/TEFF_SOLAR)**0.71) # from (14) eqn 21
