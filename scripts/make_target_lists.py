import tqdm
import pandas as pd
import numpy as np

if __name__ == "__main__":
    targets_2m = []
    for i in tqdm.tqdm(range(1, 78)):
        t = pd.read_csv(
            f"https://tess.mit.edu/public/target_lists/2m/all_targets_S{str(i).zfill(3)}_v1.csv",
            skiprows=5,
        )
        t["sector"] = np.ones(len(t), dtype=int) * i
        targets_2m.append(t)

    targets_2m = pd.concat(targets_2m)
    targets_2m.to_csv("../catalog/targets_120s.csv", index=False)

    targets_2m_count = (
        targets_2m[["TICID", "sector"]].groupby("TICID").count().reset_index()
    )
    targets_2m_count.to_csv("../catalog/targets_120s_count.csv", index=False)

    # Now for 20s:
    targets_20s = []
    for i in tqdm.tqdm(range(27, 78)):
        t = pd.read_csv(
            f"https://tess.mit.edu/public/target_lists/20s/all_targets_20s_S{str(i).zfill(3)}_v1.csv",
            skiprows=5,
        )
        t["sector"] = np.ones(len(t), dtype=int) * i
        targets_20s.append(t)

    targets_20s = pd.concat(targets_20s)
    targets_20s.to_csv("../catalog/targets_20s.csv", index=False)
    targets_20s_count = (
        targets_20s[["TICID", "sector"]].groupby("TICID").count().reset_index()
    )
    targets_20s_count.to_csv("../catalog/targets_20s_count.csv", index=False)
