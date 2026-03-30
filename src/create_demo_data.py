import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect("akshat_expenses.db")

df = pd.read_sql_query("SELECT * FROM Transactions", conn)

demo_df = df.copy()

np.random.seed(42)

demo_df['amount'] = (demo_df['amount'] * np.random.uniform(0.65, 1.35, size=len(df))).astype(int)

demo_df.to_excel("demo_expenses.xlsx", index=False)

print("Demo dataset created successfully!")
