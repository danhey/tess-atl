import numpy as np
import pandas as pd
from scipy import stats
import argparse

from .constants import *
from .tess_stars2px import tess_stars2px_function_entry
from .scaling import *
from .query import *
from .noise import *


def granulation(nu0, DILUTION, VNYQ):
    # calculate the granulation at a set of frequencies from (7) eqn 2 model F
    # Divide by DILUTION squared as it affects stars in the time series.
    # The units of DILUTION change from ppm to ppm^2 microHz^-1 when going from the
    # time series to frequency. p6: c=4 and zeta = 2*sqrt(2)/pi

    a_nomass = 0.85 * 3382 * nu0**-0.609
    b1 = 0.317 * nu0**0.970
    b2 = 0.948 * nu0**0.992
    Pgran = (
        ((2 * np.sqrt(2)) / np.pi) * (a_nomass**2 / b1) / (1 + ((nu0 / b1) ** 4))
        + ((2 * np.sqrt(2)) / np.pi) * (a_nomass**2 / b2) / (1 + ((nu0 / b2) ** 4))
    ) / (DILUTION**2)

    # From (9). the amplitude suppression factor. Normalised sinc with pi (area=1)
    eta = np.sinc((nu0 / (2 * VNYQ)))
    # the granulation after attenuation
    Pgran = Pgran * eta**2

    return Pgran, eta


def subfreq(freq, fnyq=None):
    """Return sub-Nyquist frequencies given super-Nyquist frequencies

    Args:
        freq: super-Nyq frequencies (fraction of fnyq)
        fnyq: Nyquist frequency (default 1.0)

    Returns:
        sub-Nyquist frequency measured for intrinsic freq relative to
            optionally specified fnyq
    """
    # check whether freq is iterable or single value
    freq = np.asarray(freq, dtype=np.float64)
    scalar_input = False
    if freq.ndim == 0:
        freq = freq[None]  # newaxis
        scalar_input = True

    # for iterable, apply to each element
    if not scalar_input:
        return np.fromiter((subfreq(f, fnyq) for f in freq), freq.dtype)
    else:  # return subNyquist alias for scalar input
        freq = freq / fnyq
        rem = freq % 1.0
        if np.floor(freq) % 2 == 0:  # even bounces
            return rem * fnyq
        else:  # odd bounces
            return (1.0 - rem) * fnyq


def calc_detection_probability(
    magnitude, teff, radius, logg, sectors, cadence, vary_beta=True, fap=0.05
):
    CADENCE = cadence
    VNYQ = (1.0 / (2.0 * CADENCE)) * 10**6  # in micro Hz

    numax = get_numax(logg, teff)
    lum = get_luminosity(radius, teff)
    teffred = TEFFREF_SOLAR * (lum**-0.093)  # from (6) eqn 8. red-edge temp

    if np.isnan(numax) | np.isnan(sectors):
        return np.nan, np.nan

    dnu = (
        DNU_SOLAR * (radius**-1.42) * ((teff / TEFF_SOLAR) ** 0.71)
    )  # from (14) eqn 21
    beta = 1.0 - np.exp(
        -(teffred - teff) / 1550.0
    )  # beta correction for hot solar-like stars from (6) eqn 9.
    if teff >= teffred:
        beta = 0.0

    # to remove the beta correction, set Beta=1
    if vary_beta == False:
        beta = 1.0

    # modified from (6) eqn 11. Now consistent with dnu proportional to numax^0.77 in (14)
    amp = 0.85 * 2.5 * beta * (radius**1.85) * ((teff / TEFF_SOLAR) ** 0.57)

    # From (5) table 2 values for delta nu_{env}. env_width is defined as +/- some value.
    env_width = 0.66 * numax**0.88

    # noise = calc_noise(
    #     imag,
    #     teff=teff,
    #     exptime=CADENCE,
    #     e_lng=e_lng,
    #     e_lat=e_lat,
    #     g_lng=g_lng,
    #     g_lat=g_lat,
    #     npix_aper=npix_aper,
    # )
    # noise = noise * 10.0**6  # total noise in units of ppm
    # noise = 10 ** (huber_noise(imag))

    if cadence == 20:
        noise = 10 ** (inter_20(magnitude))
    elif cadence == 120:
        noise = 10 ** (inter_120(magnitude))
    else:
        raise ValueError("Invalid cadence for calculating noise")

    # call the function for the real and aliased components (above and below VNYQ) of the granulation
    # the order of the stars is different for the aliases so fun the function in a loop
    Pgran, eta = granulation(numax, DILUTION, VNYQ)

    if numax > VNYQ:
        subf = subfreq(numax, VNYQ)[0]
        Pgranalias, _ = granulation(subf, DILUTION, VNYQ)

    elif numax < VNYQ:
        Pgranalias, _ = granulation((VNYQ + (VNYQ - numax)), DILUTION, VNYQ)

    Pgrantotal = Pgran + Pgranalias
    ptot = (0.5 * 2.94 * amp**2.0 * ((2.0 * env_width) / dnu) * eta**2.0) / (
        DILUTION**2.0
    )
    Binstr = 2.0 * (noise) ** 2.0 * CADENCE * 10**-6.0  # from (6) eqn 18
    bgtot = (Binstr + Pgrantotal) * 2.0 * env_width  # units are ppm**2

    snr = ptot / bgtot  # global signal to noise ratio from (11)
    # false alarm probability
    pdet = 1.0 - fap
    tlen = sectors * 27.4 * 86400.0  # the length of the TESS observations in seconds

    bw = 1.0 * (10.0**6.0) / tlen
    nbins = int((2.0 * env_width / bw))  # from (11)
    snrthresh = stats.chi2.ppf(pdet, 2.0 * nbins) / (2.0 * nbins) - 1.0

    pfinal = stats.chi2.sf((snrthresh + 1.0) / (snr + 1.0) * 2.0 * nbins, 2.0 * nbins)
    return pfinal, snr, numax, dnu  # , snrthresh # snr is needed in TESS_telecon2.py


def get_sectors(vals):  #
    (
        outID,
        outEclipLong,
        outEclipLat,
        outSec,
        outCam,
        outCcd,
        outColPix,
        outRowPix,
        scinfo,
    ) = tess_stars2px_function_entry(vals[:, 2], vals[:, 0], vals[:, 1])
    return pd.DataFrame({"ID": outID, "Sector": outSec})


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)

#     df = pd.read_csv("arb/TIC_clean.csv", dtype={"GAIA": str})
#     gaia_files = sorted(glob.glob("crossmatch_results/*.csv")[:])

#     for i in range(len(gaia_files)):
#         logging.info(f"Starting {i}")
#         gaia_file = gaia_files[i]
#         gaia = pd.read_csv(gaia_file, dtype={"dr2_source_id": str})[:]
#         gaia = pd.merge(df, gaia, left_on="GAIA", right_on="dr2_source_id")

#         # Get the observed sectors
#         logging.info(f"Getting sectors, eta: {(len(gaia) / 5000) * 17 / 60} minutes")
#         vals = np.array([gaia.ra.values, gaia.dec.values, gaia.ID.values]).T
#         vals = np.array_split(vals, 100)
#         # r = get_sectors(vals)
#         with multiprocess.get_context("spawn").Pool(NCPU) as p:
#             r = list(tqdm.tqdm(p.imap(get_sectors, vals), total=len(vals)))
#         sector_info = pd.concat(r)
#         gaia = pd.merge(pd.DataFrame(sector_info.value_counts("ID")), gaia, on="ID")
#         gaia.rename(columns={0: "sectors"}, inplace=True)

#         # Set up values
#         logging.info("Calculating values")
#         gaia["dr3_teff"] = gaia["teff_gspspec"].combine_first(gaia["teff_gspphot"])
#         gaia["dr3_logg"] = gaia["logg_gspphot"].combine_first(gaia["logg_gspspec"])
#         gaia["dr3_radius"] = gaia["radius_gspphot"]

#         logging.info("Calculating probabilities")
#         # idxs = list(range(len(gaia)))[:]
#         with multiprocess.get_context("spawn").Pool(NCPU) as p:
#             r = list(
#                 tqdm.tqdm(p.imap(calculate_star, gaia.iterrows()), total=len(gaia))
#             )
#         gaia["pfinal"] = np.array(r)[:, 0]
#         gaia["snr"] = np.array(r)[:, 1]
#         gaia.to_csv(f"ATL_2min/ATL_{i}.csv")
