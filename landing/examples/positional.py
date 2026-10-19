import pandas as pd

from mlschema import infer_schema

# A NumPy-style matrix: no column names, only input positions.
df = pd.DataFrame([[0.2, 1.4, True], [0.3, 1.1, False], [0.1, 1.7, True]])

schema = infer_schema(df)
