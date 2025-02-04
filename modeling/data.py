#delete common line
import pandas as pd
if __name__ == "__main__":
    df = pd.read_csv("ratings.csv")
    print(df.shape)
    df.drop_duplicates(subset=["user_id"], keep="first", inplace=True)
    df.drop_duplicates(subset=["movie"], keep="first", inplace=True)
    print(df.shape)
    df.to_csv("ratings_clean.csv")


        