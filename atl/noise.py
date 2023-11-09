import numpy as np
from scipy.interpolate import interp1d

# noise_2min = np.array(
#     [
#         [2.0, 8],
#         [2.5, 2.5],
#         [3.0, 2.05277856],
#         [3.5, 3.47917351],
#         [4.0, 1.94596472],
#         [4.5, 2.34231592],
#         [5.0, 2.47882901],
#         [5.5, 2.23313323],
#         [6.0, 2.48892844],
#         [6.5, 2.3607032],
#         [7.0, 2.44991334],
#         [7.5, 2.54823579],
#         [8.0, 2.63382584],
#         [8.5, 2.70824579],
#         [9.0, 2.81058899],
#         [9.5, 2.90655696],
#         [10.0, 3.01670582],
#         [10.5, 3.1112884],
#         [11.0, 3.28990876],
#         [11.5, 3.47129083],
#         [12.0, 3.4671964],
#         [12.5, 3.64029884],
#         [13.0, 3.79639558],
#         [13.5, 3.94228705],
#         [14.0, 4.09139554],
#         [14.5, 4.2802665],
#         [15.0, 4.42689697],
#         [15.5, 4.59669897],
#         [16.0, 4.80027499],
#         [16.5, 5.07377083],
#         [17.0, 5.26317175],
#         [17.5, 5.57369966],
#         [18.0, 5.65307057],
#         [18.5, 7.36701138],
#         [19.0, 6.29444334],
#         [19.5, 8],
#     ]
# )

# noise_20s = np.array(
#     [
#         [2.0, np.nan],
#         [2.5, 3],
#         [3.0, 3.18534295],
#         [3.5, 3.47818556],
#         [4.0, 2.21050205],
#         [4.5, 2.46704628],
#         [5.0, 2.65006456],
#         [5.5, 2.43340177],
#         [6.0, 2.6374527],
#         [6.5, 2.63340179],
#         [7.0, 2.77491449],
#         [7.5, 2.86336028],
#         [8.0, 2.96692229],
#         [8.5, 3.03211851],
#         [9.0, 3.17133233],
#         [9.5, 3.28242652],
#         [10.0, 3.39074263],
#         [10.5, 3.48816589],
#         [11.0, 3.62056628],
#         [11.5, 3.75311834],
#         [12.0, 3.82961513],
#         [12.5, 4.00888884],
#         [13.0, 4.13423715],
#         [13.5, 4.29844452],
#         [14.0, 4.459285],
#         [14.5, 4.64575912],
#         [15.0, 4.80873334],
#         [15.5, 4.97310657],
#         [16.0, 5.19578062],
#         [16.5, 5.44527216],
#         [17.0, 5.64813449],
#         [17.5, 5.95727467],
#         [18.0, 6.03058939],
#         [18.5, 8.12001196],
#         [19.0, 9.69392245],
#         [19.5, np.nan],
#     ]
# )

# inter_20 = interp1d(noise_20s[:, 0], noise_20s[:, 1], fill_value=100)
# inter_120 = interp1d(noise_2min[:, 0], noise_2min[:, 1], fill_value=100)


noise_ratio = np.array(
    [
        [6.0, 0.749],
        [7.0, 0.810],
        [8.0, 0.894],
        [9.0, 0.923],
        [10.0, 0.942],
        [11.0, 0.974],
        [12.0, 0.984],
        [13.0, 0.998],
        [14.0, 1.009],
        [15.0, 1.013],
        [16.0, 1.018],
    ]
)

inter = interp1d(
    noise_ratio[:, 0],
    (noise_ratio[:, 1]),
    kind="quadratic",
    bounds_error=False,
    fill_value=(0.75, 1.02),
)


def calc_noise(
    imag,
    exptime,
    teff,
    e_lng=0,
    e_lat=30,
    g_lng=96,
    g_lat=-30,
    subexptime=2.0,
    npix_aper=4,
    frac_aper=0.76,
    e_pix_ro=10,
    geom_area=60.0,
    pix_scale=21.1,
    sys_limit=0,
):
    omega_pix = pix_scale**2.0
    n_exposures = exptime / subexptime

    # electrons from the star
    megaph_s_cm2_0mag = 1.6301336 + 0.14733937 * (teff - 5000.0) / 5000.0
    e_star = (
        10.0 ** (-0.4 * imag)
        * 10.0**6
        * megaph_s_cm2_0mag
        * geom_area
        * exptime
        * frac_aper
    )
    e_star_sub = e_star * subexptime / exptime
    dlat = (abs(e_lat) - 90.0) / 90.0
    vmag_zodi = 23.345 - (1.148 * dlat**2.0)
    e_pix_zodi = (
        10.0 ** (-0.4 * (vmag_zodi - 22.8))
        * (2.39 * 10.0**-3)
        * geom_area
        * omega_pix
        * exptime
    )

    # e/pix from background stars
    dlat = abs(g_lat) / 40.0 * 10.0**0

    dlon = g_lng
    q = np.where(dlon > 180.0)
    if len(q) > 0:
        dlon = 360.0 - dlon

    dlon = abs(dlon) / 180.0 * 10.0**0
    p = [18.97338 * 10.0**0, 8.833 * 10.0**0, 4.007 * 10.0**0, 0.805 * 10.0**0]
    imag_bgstars = p[0] + p[1] * dlat + p[2] * dlon ** (p[3])
    e_pix_bgstars = (
        10.0 ** (-0.4 * imag_bgstars)
        * 1.7
        * 10.0**6
        * geom_area
        * omega_pix
        * exptime
    )

    # compute noise sources
    noise_star = np.sqrt(e_star) / e_star
    noise_sky = np.sqrt(npix_aper * (e_pix_zodi + e_pix_bgstars)) / e_star
    noise_ro = np.sqrt(npix_aper * n_exposures) * e_pix_ro / e_star
    noise_sys = 0.0 * noise_star + sys_limit / (1 * 10.0**6) / np.sqrt(
        exptime / 3600.0
    )
    noise2 = np.sqrt(
        noise_star**2.0 + noise_sky**2.0 + noise_ro**2.0 + noise_sys**2.0
    )
    # noise1 = np.sqrt(noise_star**2.0 + noise_sky**2.0 + noise_ro**2.0)

    return noise2
