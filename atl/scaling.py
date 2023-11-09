from astropy.constants import sigma_sb, G
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


def get_mass(logg, radius):
    mass = (
        (
            ((10**logg) * u.cm / u.s**2)
            * (((radius * u.R_sun).to(u.cm)) ** 2)
            / (G.cgs)
        )
        .to(u.M_sun)
        .value
    )
    return mass
