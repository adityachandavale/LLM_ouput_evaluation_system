import pandas as pd
import os

def save_results(results, path="data/outputs.csv"):
    df = pd.DataFrame(results)

    file_exists = os.path.exists(path)

    df.to_csv(
        path,
        mode='a',
        header=not file_exists,
        index=False
    )