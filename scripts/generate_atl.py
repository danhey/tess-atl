if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    df = pd.read_csv("arb/TIC_clean.csv", dtype={"GAIA": str})
    gaia_files = sorted(glob.glob("crossmatch_results/*.csv")[:])
    start_at = 0
    for i in range(start_at, len(gaia_files))[:]:  #### HERE!!!!!!!
        logging.info(f"Starting {i}")
        gaia_file = gaia_files[i]
        gaia = pd.read_csv(gaia_file, dtype={"dr2_source_id": str})[:]
        gaia = pd.merge(df, gaia, left_on="GAIA", right_on="dr2_source_id")

        # Get the observed sectors
        logging.info(f"Getting sectors, eta: {(len(gaia) / 5000) * 17 / 60} minutes")
        vals = np.array([gaia.ra.values, gaia.dec.values, gaia.ID.values]).T
        vals = np.array_split(vals, 100)
        # r = get_sectors(vals)
        with multiprocess.get_context("spawn").Pool(NCPU) as p:
            r = list(tqdm.tqdm(p.imap(get_sectors, vals), total=len(vals)))
        sector_info = pd.concat(r)
        gaia = pd.merge(pd.DataFrame(sector_info.value_counts("ID")), gaia, on="ID")
        gaia.rename(columns={"count": "Sectors"}, inplace=True)

        # Set up values
        logging.info("Calculating values")
        gaia["atl_radius"] = gaia.radius_gspphot.combine_first(gaia.rad).combine_first(
            gaia.radius_flame
        )
        gaia["atl_teff"] = gaia.teff_gspphot.combine_first(gaia.Teff).combine_first(
            gaia.teff_gspspec
        )
        gaia["atl_logg"] = gaia.logg_gspphot.combine_first(gaia.logg).combine_first(
            gaia.logg_gspspec
        )

        # Coordinates:
        from astropy.coordinates import SkyCoord
        import astropy.units as u

        gaia["coordinate"] = SkyCoord(
            gaia.ra * u.degree, gaia.dec * u.degree, unit="deg"
        )

        logging.info("Calculating probabilities")
        with multiprocess.get_context("spawn").Pool(NCPU) as p:
            r = list(
                tqdm.tqdm(p.imap(calculate_star, gaia.iterrows()), total=len(gaia))
            )
        gaia["pfinal"] = np.array(r)[:, 0]
        gaia["snr"] = np.array(r)[:, 1]
        gaia["noise"] = np.array(r)[:, 2]
        gaia["amp"] = np.array(r)[:, 3]
        gaia["ptot"] = np.array(r)[:, 4]
        gaia["bgtot"] = np.array(r)[:, 5]

        gaia.to_csv(f"ATL_20s/ATL_{i}.csv")
