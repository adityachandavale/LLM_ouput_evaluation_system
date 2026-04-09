import pandas as pd

def compare_models(results):
    df = pd.DataFrame(results)
    return df.groupby("model").mean(numeric_only=True)