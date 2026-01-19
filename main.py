import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    import rcd_bending_rect as rcd
    return np, plt, rcd


@app.cell
def _(np, plt, rcd):
    M20 = rcd.Concrete(fck=20)
    x = np.concatenate((np.linspace(0, 0.002, 21), np.linspace(0.0025, 0.0035, 6)))
    y = np.array([M20.fc(ec) for ec in x])
    plt.plot(x, y)
    plt.grid()
    plt.show()
    return (M20,)


@app.cell
def _(np, plt, rcd):
    Fe500 = rcd.RebarHYSD(fy=500, label="Fe 500")

    xx = np.concatenate(
        (
            Fe500.es_fs[0:2, 0],
            np.linspace(Fe500.es_fs[2, 0], Fe500.es_fs[3, 0], 11),
            np.linspace(Fe500.es_fs[3, 0], Fe500.es_fs[4, 0], 11),
            np.linspace(Fe500.es_fs[4, 0], Fe500.es_fs[5, 0], 11),
            np.linspace(Fe500.es_fs[5, 0], Fe500.es_fs[6, 0], 11),
            np.array([Fe500.es_fs[6, 0], Fe500.es_fs[6, 0] + 0.01]),
        )
    )
    yy = np.array([Fe500.fs(es) for es in xx])
    print(xx.shape, yy.shape)
    plt.plot(xx, yy)
    plt.scatter(Fe500.es_fs[:, 0], Fe500.es_fs[:, 1], marker="x", color="red")
    plt.grid()
    plt.show()
    return (Fe500,)


@app.cell
def _(Fe500, M20, rcd):
    tsec = rcd.FlangedSection(
        230.0, 450.0, 25.0, M20, Fe500, Fe500, Fe500, bf=900, df=150.0
    )
    for Mu in [290.0, 340.0, 343.0, 370.0, 380.0, tsec.Mulim / 1e6 + 1]:
        xu = tsec.reqd_xu(Mu * 1e6)
        if xu:
            print(f"xu={xu:.2f}, Mu={tsec.Mu(xu) / 1e6:.2f} kNm")
    return


if __name__ == "__main__":
    app.run()
