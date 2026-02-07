import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from fractions import Fraction as F
    import numpy as np
    import matplotlib.pyplot as plt

    from pprint import pprint
    from collections import OrderedDict

    from rcd_bending_rect import Concrete, RebarMS, RebarHYSD, RectBeamSection, FlangedSection, RectColumnSection
    return (
        Concrete,
        F,
        FlangedSection,
        RebarHYSD,
        RebarMS,
        RectBeamSection,
        RectColumnSection,
        mo,
        np,
        plt,
        pprint,
    )


@app.cell
def _(Concrete, np, plt):
    M20 = Concrete(fck=20)

    _x = np.concatenate([np.linspace(0, 0.002, 51), np.array([0.003, 0.0035])])
    _y = np.array([M20.fc(_xx) for _xx in _x])

    _fig, _ax = plt.subplots(figsize=(8,4))
    _ax.plot(_x, _y)
    _ax.grid()
    _ax.set_xlabel("$\epsilon_c$")
    _ax.set_ylabel("$f_c$ (N/mm$^2$)")
    _ax.set_title("Stress-strain relation for M20 concrete")


    plt.show()
    return (M20,)


@app.cell
def _(F, RebarMS, np, plt):
    _fy = 250.0
    Es = 2e5

    MS250 = RebarMS(fy=_fy)
    _fsy = F(100, 115) * _fy / Es
    _x = np.array([0.0, 0.5 * _fsy, _fsy, 1.5 * _fsy, 2.5 * _fsy])
    _y = np.array([MS250.fs(_xx) for _xx in _x])

    _fig, _ax = plt.subplots(figsize=(8,4))
    _ax.plot(_x, _y)
    _ax.grid()
    _ax.set_xlabel("$\epsilon_s$")
    _ax.set_ylabel("$f_s$ (N/mm$^2$)")
    _ax.set_title("Stress-strain relation for Mild Steel Rebars $f_y = 250$ N/mm$^2$")

    plt.show()
    return (Es,)


@app.cell
def _(Es, F, RebarHYSD, np, plt):
    _fy = 500.0
    Fe500 = RebarHYSD(fy=_fy)

    _ep_fs = np.array([
        [0.0, 0.0, 0.0001, 0.0003, 0.0007, 0.001, 0.002],
        [0.0, 0.8, 0.85, 0.9, 0.95, 0.975, 1.0]
    ]).T

    _fsy = F(100, 115) * _fy
    _y = _ep_fs[:, 1] * _fsy
    _x = _y / Es + _ep_fs[:, 0]
    _x1 = np.array([_x[-1] + 0.001, _x[-1] + 0.002, _x[-1] + 0.003])
    _x = np.concatenate([_x, _x1])
    _y = np.array([Fe500.fs(_xx) for _xx in _x])

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_x, _y)
    _ax.grid()
    _ax.set_xlabel("$\epsilon_s$")
    _ax.set_ylabel("$f_s$ (N/mm$^2$)")
    _ax.set_title("Stress-strain relation for HYSD Rebars $f_y = 500$ N/mm$^2$")

    plt.show()
    return (Fe500,)


@app.cell
def _(Fe500, M20, RectBeamSection):
    _rsec = RectBeamSection(230, 450, conc=M20, clear_cover=25, tbars=Fe500, cbars=Fe500, vbars=Fe500)
    _Asc, _Ast = _rsec.Asc_Ast(Mu=100e6)
    print(f"Asc={_Asc:.2f} mm^2, Ast={_Ast:.2f} mm^2")

    _Asc, _Ast = _rsec.Asc_Ast(Mu=150e6)
    print(f"Asc={_Asc:.2f} mm^2, Ast={_Ast:.2f} mm^2")
    return


@app.cell
def _(Fe500, FlangedSection, M20):
    tsec = FlangedSection(230, 450, clear_cover=25, conc=M20, tbars=Fe500, cbars=Fe500, vbars=Fe500, bf=1000, df=150)

    _reqd_xu = tsec.reqd_xu(Mu=140e6)
    print(f"Required x_u={_reqd_xu:.2f}")

    _reqd_xu = tsec.reqd_xu(Mu=340e6)
    print(f"Required x_u={_reqd_xu:.2f}")
    return


@app.cell
def _(col, pprint):
    _b = 230.0
    _D = 450.0

    # col = RectColumnSection(_b, _D, dc=30, conc=M20, steel=Fe500, total_As=0.5 / 100 * _b * _D)
    _Pu, _Mu, _report = col.Pu_Mu(xu=1.2 * _D, report=True)
    print(f"Pu={_Pu/1e3:.2f}, Mu={_Mu/1e6:.2f}")
    pprint(_report, indent=4, width=120)
    return


@app.cell
def _(Fe500, M20, RectColumnSection, pprint):
    _b = 230.0
    _D = 450.0

    col = RectColumnSection(_b, _D, dc=30, conc=M20, steel=Fe500, total_As=0.5 / 100 * _b * _D)
    _Pu, _Mu, _report = col.Pu_Mu(xu=0.7 * _D, report=True)
    print(f"Pu={_Pu/1e3:.2f}, Mu={_Mu/1e6:.2f}")
    pprint(_report, indent=4, width=120)
    return (col,)


@app.cell
def _(mo):
    conc = mo.ui.dropdown(options=["M20", "M25", "M30", "M35", "M40"], value="M20", label="Concrete grade:")
    main_steel = mo.ui.dropdown(options=["Mild Steel", "Fe415", "Fe500", "Fe550"], value="Fe500", label="Main rebars")
    sec_steel = mo.ui.dropdown(options=["Mild Steel", "Fe415", "Fe500", "Fe550"], value="Fe500", label="Secondary rebars")
    sec_b = mo.ui.number(label="Width (mm):")
    sec_D = mo.ui.number(label="Overall depth (mm):")
    sec_cover = mo.ui.number(label="Clear cover (mm):")
    rebar_t = mo.ui.multiselect(options=["12", "16", "20", "25"], label="Tension rebar dia (mm):")
    rebar_c = mo.ui.multiselect(options=["12", "16", "20", "25"], label="Compression rebar dia (mm):")
    rebar_v = mo.ui.multiselect(options=["6", "8", "10", "12"], label="Stirrup dia (mm):")
    design_Mu = mo.ui.number(label="Mu (kNm):")
    design_Vu = mo.ui.number(label="Vu (kNm):")

    mo.vstack([
        mo.hstack([conc, main_steel, sec_steel], widths="equal"),
        mo.hstack([sec_b, sec_D, sec_cover], justify="start"),
        mo.hstack([rebar_t, rebar_c, rebar_v], justify="start"),
        mo.hstack([design_Mu, design_Vu], justify="start"),
    ])
    return (
        conc,
        design_Mu,
        design_Vu,
        main_steel,
        sec_D,
        sec_b,
        sec_cover,
        sec_steel,
    )


@app.cell
def _(Concrete, Rebar, RebarHYSD, RebarMS):
    def get_conc(grade: str) -> Concrete:
        if grade.upper() in ["M20", "M25", "M30", "M35", "M40"]:
            conc = Concrete(fck=float(grade[1:]))
            return conc

    def get_steel(grade: str) -> Rebar:
        grade = grade.upper()
        if grade == "MS":
            return RebarMS(fy=250)
        elif grade in ["MS", "FE415", "FE500", "FE550"]:
            return RebarHYSD(fy=float(grade[2:]))
    return get_conc, get_steel


@app.cell
def _(
    RectBeamSection,
    conc,
    design_Mu,
    design_Vu,
    get_conc,
    get_steel,
    main_steel,
    sec_D,
    sec_b,
    sec_cover,
    sec_steel,
):
    b = sec_b.value
    D = sec_D.value
    dc = sec_cover.value

    if b and D and dc:
        print(f"Rectangular section: {b} x {D} mm Clear cover={dc}")
    if conc.value:
        _conc = get_conc(conc.value)
        print(f"Concrete: {_conc.fck}")
    if main_steel.value:
        _main_steel = get_steel(main_steel.value)
        print(f"Main steel: {_main_steel.fy}")

    if sec_steel.value:
        _sec_steel = get_steel(sec_steel.value)
        print(f"Secondary steel: {_sec_steel.fy}")

    if design_Mu.value and design_Vu.value:
        _Mu = design_Mu.value * 1e6
        _Vu = design_Vu.value * 1e3
        print(f"Mu={_Mu/1e6} kNm, Vu={_Vu/1e3} kN")

    rsec = RectBeamSection(b=b, D=D,clear_cover=dc, conc=_conc, tbars=_main_steel, cbars=_main_steel, vbars=_sec_steel)
    _Mulim = rsec.Mulim
    _Asc, _Ast, _sv = rsec.design_section(Mu=_Mu, Vu=_Vu)
    print(f"Mu_lim={_Mulim/1e6:.2f} kNm, Asc={_Asc:.2f} mm^2, Ast={_Ast:.2f} mm^2")
    return


if __name__ == "__main__":
    app.run()
