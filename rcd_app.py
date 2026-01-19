import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    import rcd_bending_rect as rcd
    return mo, np, plt, rcd


@app.cell
def _(mo):
    concrete=mo.ui.dropdown({"M20": 20, "M25": 25, "M30": 30, "M35": 35, "M40": 40}, value="M20")
    rebar_primary = mo.ui.dropdown({"Mild Steel": 200, "Fe415": 415, "Fe500": 500, "Fe550": 550}, value="Fe500")
    mo.hstack([concrete, rebar_primary], justify="start")
    return concrete, rebar_primary


@app.cell
def _(concrete, np, plt, rcd, rebar_primary):
    def _csb(fck, np, plt, rcd):
        concrete = rcd.Concrete(fck=fck)
        x = np.concatenate((np.linspace(0, 0.002, 21), np.linspace(0.0025, 0.0035, 6)))
        y = np.array([concrete.fc(ec) for ec in x])
        plt.figure(figsize=(5, 3))
        plt.plot(x, y)
        plt.grid()
        plt.show()
        return

    def _steel_stress_strain(fy, np, plt, rcd):
        if fy >= 415:
            steel = rcd.RebarHYSD(fy=fy,)
            xx = np.concatenate(
                (
                    steel.es_fs[0:2, 0],
                    np.linspace(steel.es_fs[2, 0], steel.es_fs[3, 0], 11),
                    np.linspace(steel.es_fs[3, 0], steel.es_fs[4, 0], 11),
                    np.linspace(steel.es_fs[4, 0], steel.es_fs[5, 0], 11),
                    np.linspace(steel.es_fs[5, 0], steel.es_fs[6, 0], 11),
                    np.array([steel.es_fs[6, 0], steel.es_fs[6, 0] + 0.01]),
                )
            )
            yy = np.array([steel.fs(es) for es in xx])
        else:
            steel = rcd.RebarMS(fy=fy,)
            xx = np.array([0.0, 100/115*fy/2e5, 2*100/115*fy/2e5])
            yy = np.array([0.0, 100/115*fy, 100/115*fy])
    
        print(xx.shape, yy.shape)
        plt.figure(figsize=(5, 3))
        plt.plot(xx, yy)
        plt.scatter(steel.es_fs[:, 0], steel.es_fs[:, 1], marker="x", color="red")
        plt.grid()
        plt.show()
        return

    _csb(float(concrete.value), np, plt, rcd)
    _steel_stress_strain(float(rebar_primary.value), np, plt, rcd)
    return


if __name__ == "__main__":
    app.run()
