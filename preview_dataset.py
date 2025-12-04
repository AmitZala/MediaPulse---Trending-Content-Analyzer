# scripts/preview_dataset.py
import pandas as pd
p = "data/Viral_Social_Media_Trends_with_DateTime.csv"
df = pd.read_csv(p)
print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print(df.head(10))
print(df.dtypes)
print("Null counts:\n", df.isnull().sum())
print("Description:\n", df.describe(include='all'))