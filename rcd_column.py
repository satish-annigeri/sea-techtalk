import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import rcd_bending_rect as rcd
    return (rcd,)


@app.cell
def _(rcd):
    M20 = rcd.Concrete(fck=20)
    MS = rcd.RebarMS(fy=250, label="MS")
    print(M20)
    print(MS)
    return M20, MS


@app.cell
def _(M20, MS, rcd):
    b = 300
    D = 500
    total_As = b * D * 4 / 100
    dc = 0.1 * D
    sec = rcd.RectColumnSection(b=b, D=D, dc=dc, conc=M20, steel=MS, total_As=total_As)
    print(sec)
    Pu, Mu = sec.Pu_Mu(xu=1.1*D)
    print(f"{Pu / (M20.fck * b * D):.3f}, {Mu / (M20.fck * b * D**2):.3f}")
    return


if __name__ == "__main__":
    app.run()
