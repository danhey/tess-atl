import argparse
import pandas as pd
import numpy as np
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

from .query import query_tic, query_gaia
from .atl import get_sectors
from .atl import calc_detection_probability


def main():
    parser = argparse.ArgumentParser(
        prog="ATL",
        description="tess-atl: automated asteroseismic detection probabilities",
    )
    parser.add_argument("--kic", type=str, required=False)
    parser.add_argument("--tic", type=str, required=False)
    parser.add_argument("--gaia", type=str, required=False)
    parser.add_argument("--target", type=str, required=False)
    parser.add_argument(
        "--sectors",
        type=int,
        required=False,
        help="The number of sectors for which to calculate. If left blank, tess-point will be queried instead.",
    )
    parser.add_argument(
        "--fap",
        type=float,
        required=False,
        default=0.05,
        help="The false alarm probability level above which the probability of detection is measured.",
    )
    parser.add_argument(
        "--cadence",
        type=int,
        required=False,
        default=120,
        help="The observational cadence, either 20 or 120. Default is 20.",
    )

    args = parser.parse_args()

    # Query the TIC first for magnitudes, positions.
    if args.target is not None:
        ticid = None  # this is awful but i can't be bothered.
        q = Simbad.query_objectids(args.target)
        for ids in q["ID"]:
            if ids.startswith("TIC"):
                ticid = ids.lstrip("TIC ")
        if ticid is None:
            raise ValueError("Could not resolve name.")
        r = query_tic([ticid], ids="TIC")
    elif args.kic is not None:
        r = query_tic([args.kic], ids="KIC")
    elif args.tic is not None:
        r = query_tic([args.tic], ids="TIC")
    elif args.gaia is not None:
        r = query_tic([args.gaia], ids="GAIA")

    # Now query Gaia for DR3 parameters:
    gaia = query_gaia(int(r.iloc[0]["GAIA"]))
    gaia["dr2_source_id"] = gaia["dr2_source_id"].astype(str)
    r = pd.merge(r, gaia, left_on="GAIA", right_on="dr2_source_id")

    # Setup values
    r["atl_teff"] = (
        r["teff_gspphot"].combine_first(r["Teff"]).combine_first(r["teff_gspspec"])
    )
    r["atl_logg"] = (
        r["logg_gspphot"].combine_first(r["logg"]).combine_first(r["logg_gspspec"])
    )
    r["atl_radius"] = r["radius_gspphot"].combine_first(r["rad"])

    # OK, now where do these stars lie in TESS?
    if args.sectors is None:
        vals = np.array([r.ra.values, r.dec.values, r.ID.values]).T
        sector_info = pd.DataFrame(get_sectors(vals).value_counts("ID")).reset_index()
        sector_info["ID"] = sector_info["ID"].astype(str)
        r = pd.merge(sector_info, r, on="ID")
        r.rename(columns={0: "sectors"}, inplace=True)
    else:
        r["sectors"] = args.sectors

    # We need the position to calculate noise;
    r["coordinate"] = SkyCoord(r.ra * u.degree, r.dec * u.degree, unit="deg")
    # Now calculate the detection probability:
    row = r.iloc[0]
    print(repr(row))
    pfinal, snr, numax, dnu = calc_detection_probability(
        row.Tmag,
        row.atl_teff,
        row.atl_radius,
        row.atl_logg,
        row.sectors,
        args.cadence,
        row.coordinate,
        fap=args.fap,
    )
    print(
        f"Probability: {pfinal:.3f}, numax: {numax:.3f} uHz, dnu: {dnu:.3f} uHz, SNR: {snr:.3f}"
    )
