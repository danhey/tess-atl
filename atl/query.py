from astroquery.mast import Catalogs
import pandas as pd
from astroquery.gaia import Gaia
import numpy as np


def query_tic(target: list, ids=["Gaia", "TIC", "KIC"]) -> pd.DataFrame:
    if ids == "Gaia":
        res = Catalogs.query_criteria(catalog="Tic", GAIA=target).to_pandas()[
            ["ID", "KIC", "GAIA", "Tmag", "ra", "dec", "Teff", "logg", "rad"]
        ]
    elif ids == "TIC":
        res = Catalogs.query_criteria(catalog="Tic", ID=target).to_pandas()[
            ["ID", "KIC", "GAIA", "Tmag", "ra", "dec", "Teff", "logg", "rad"]
        ]
    elif ids == "KIC":
        res = Catalogs.query_criteria(catalog="Tic", KIC=target).to_pandas()[
            ["ID", "KIC", "GAIA", "Tmag", "ra", "dec", "Teff", "logg", "rad"]
        ]
    else:
        raise ValueError("ids must be one of ..")
    return res


def query_gaia_multiple(dr2_ids):
    QUERY = f"""
            SELECT xmatch.*, dr3.radius_gspphot, dr3.teff_gspspec, dr3.teff_gspphot, dr3.logg_gspphot, dr3.logg_gspspec, dr3.radius_flame
            FROM gaiadr3.astrophysical_parameters as dr3
            JOIN (
                SELECT dr2toedr3.*
                FROM gaiaedr3.dr2_neighbourhood AS dr2toedr3
                    WHERE dr2toedr3.dr2_source_id IN {tuple(dr2_ids)}
                ) AS xmatch
            ON xmatch.dr3_source_id = dr3.source_id
        """
    job = Gaia.launch_job(QUERY)
    return job.get_results().to_pandas()


def query_gaia(dr2_id):
    QUERY = f"""
            SELECT xmatch.*, dr3.radius_gspphot, dr3.teff_gspspec, dr3.teff_gspphot, dr3.logg_gspphot, dr3.logg_gspspec, dr3.radius_flame
            FROM gaiadr3.astrophysical_parameters as dr3
            JOIN (
                SELECT dr2toedr3.*
                FROM gaiaedr3.dr2_neighbourhood AS dr2toedr3
                    WHERE dr2toedr3.dr2_source_id = {dr2_id}
                ) AS xmatch
            ON xmatch.dr3_source_id = dr3.source_id
        """
    job = Gaia.launch_job(QUERY)
    return job.get_results().to_pandas()
