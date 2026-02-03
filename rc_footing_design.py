import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import math
    import pandas as pd

    from footing import RectFooting
    return RectFooting, math, mo, pd


@app.cell
def _(math):
    def ceil_mof(x: float, z: float) -> float:
        return math.ceil(x / z) * z

    def floor_mof(x: float, z: float) -> float:
        return math.floor(x / z) * z
    return (ceil_mof,)


@app.cell
def _(RectFooting):
    footing = RectFooting(Lx=3.0, Ly=3.0, D=0.5, bx=0.4, by=0.4, P=1000.0, Mx=20.0, My=15.0)

    sbc = 150.0
    required_area = footing.required_area(sbc=sbc)
    print(f"Required area = {required_area:.2f} m^2")
    return (sbc,)


@app.cell
def _(pd):
    df = pd.read_excel("reactions.xlsx")
    col_names = df.iloc[0]
    col_names = col_names.str.replace(" kNm", "")
    col_names = col_names.str.replace(" kN", "")
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = col_names
    df.columns = df.columns.map(str)

    cols = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]
    df[cols] = df[cols].astype("float64")
    df
    return (df,)


@app.cell
def _(RectFooting, ceil_mof, math, pd):
    def design_footing(r, sbc, mof=0.15):
        P = r["Fy"]
        Mx = r["Mx"]
        My = r["Mz"]
        footing = RectFooting(Lx=0, Ly=0, D=0, bx=0.23, by=0.45, P=P, Mx=Mx, My=My)
        reqd_area = footing.required_area(sbc=sbc)
        # print(f'P={P:10.2f}, Mx={Mx:10.2f}, My={My:10.2f}, A = {reqd_area:.2f}, L = {ceil_mof(math.sqrt(reqd_area), 0.15):.2f}')
        L = ceil_mof(math.sqrt(reqd_area), mof)
        footing.Lx = L
        footing.Ly = L
        max_p = footing.max_pressure()
        return pd.Series({
            "Lx": L, "Ly": L, "max_p": ceil_mof(max_p, 0.01), "Safe": max_p <= sbc
        })

    def revise_footing(r, sbc, inc=0.15):
        # print(r.to_dict())
        if r["Safe"]:
            return pd.Series({
                "Lx": r["Lx"], "Ly": r["Ly"], "max_p": r["max_p"], "Safe": r["Safe"]
            })
        else:
            Lx = r["Lx"] + inc
            Ly = r["Ly"] + inc
            P = r["Fy"]
            Mx = r["Mx"]
            My = r["Mz"]

            max_p = r["max_p"]
            footing = RectFooting(Lx=Lx, Ly=Ly, D=0, bx=0, by=0, P=P, Mx=Mx, My=My)
            max_p = footing.max_pressure()
            return pd.Series({
                "Lx": Lx, "Ly": Ly, "max_p": ceil_mof(max_p, 0.01), "Safe": max_p <= sbc
            })
    return design_footing, revise_footing


@app.cell
def _(design_footing, df, mo):
    df[["Lx", "Ly", "max_p", "Safe"]] = df.apply(design_footing, sbc=150, axis=1)
    mo.ui.table(df, format_mapping={"Lx": "{:.2f}", "Ly": "{:.2f}", "max_p": "{:.2f}"})
    return


@app.cell
def _(df, mo, revise_footing, sbc):
    _df = df.copy()
    _df[["Lx", "Ly", "max_p", "Safe"]] = _df.apply(revise_footing, sbc=sbc, inc=0.15, axis=1)
    mo.ui.table(_df, format_mapping={"Lx": "{:.2f}", "Ly": "{:.2f}", "max_p": "{:.2f}"})
    return


if __name__ == "__main__":
    app.run()
