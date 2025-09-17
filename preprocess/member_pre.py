import pandas as pd

df = pd.read_excel("./data/info1516.xlsx")
df.to_json("info1516.json", orient="records", force_ascii=False, indent=2)