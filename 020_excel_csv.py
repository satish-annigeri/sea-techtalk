import marimo

__generated_with = "0.19.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import numpy as np
    import polars as pl
    import pandas as pd
    return np, pd


@app.cell
def _(pd):
    fname = "reactions.xlsx"

    df = pd.read_excel(fname)
    col_names = df.iloc[0]
    col_names = col_names.str.replace(" kNm", "")
    col_names = col_names.str.replace(" kN", "")
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = col_names

    cols = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]
    df[cols] = df[cols].astype("float64")
    df
    return cols, df


@app.cell
def _(cols, df, pd):
    summary = pd.DataFrame(
        [
            df[cols].min(),                 # row 1: min
            df[cols].max(),                 # row 2: max
            df[cols].abs().min(),           # row 3: min absolute
            df[cols].abs().max(),           # row 4: max absolute
            df[cols].sum(),                 # row 5: sum
            df[cols].abs().sum(),           # row 6: sum of absolute values
        ],
        index=["min", "max", "min_abs", "max_abs", "sum", "sum_abs"]
    )

    print(summary)
    return


@app.cell
def _(df, np, pd):
    mult_of = 50.0
    vmin = np.floor(df['Fy'].min() / mult_of) * mult_of
    vmax = np.ceil(df['Fy'].max() / mult_of) * mult_of
    print(vmin, vmax, (vmax - vmin) / 10)
    bins = np.linspace(vmin, vmax, 6)
    labels = [f"F{_i}" for _i in range(1, 6)]
    df["class_intervals"] = pd.cut(df["Fy"], bins=bins, labels=labels, include_lowest=True)
    df.sort_values("class_intervals")
    return


@app.cell
def _(df):
    def stripe_groups(df, group_col):
        # Assign a group number for each block of identical values
        group_ids = df[group_col].ne(df[group_col].shift()).cumsum()

        def row_style(row):
            gid = group_ids.loc[row.name]
            color = "white" if gid % 2 == 0 else "#f0f0f0"   # light grey
            return [f"background-color: {color}"] * len(df.columns)

        return df.style.apply(row_style, axis=1)

    df_striped = df.sort_values("class_intervals")
    stripe_groups(df_striped, "class_intervals")
    return


if __name__ == "__main__":
    app.run()
