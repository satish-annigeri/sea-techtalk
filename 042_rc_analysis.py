import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analysis of RC Rectangular Sections

    This package calculates the capacity of a section with given dimensions, garde of concrete, grade of steel and location of reinforcement bars, as per IS456:2000. The package can be installed using `uv` with the following command
    ```bash
    > uv add rcdesign
    ```

    If you are using `pip`, the command, after activating the virtual environment is
    ```bash
    > pip install rcdesign
    ```
    """)
    return


@app.cell
def _():
    import marimo as mo

    import numpy as np

    from rcdesign.is456.concrete import Concrete
    from rcdesign.is456.stressblock import LSMStressBlock
    from rcdesign.is456.rebar import (
        RebarHYSD,
        RebarLayer,
        RebarGroup,
        Stirrups,
        ShearRebarGroup,
        LateralTie
    )
    from rcdesign.is456.section import RectBeamSection, FlangedBeamSection, RectColumnSection

    return (
        Concrete,
        FlangedBeamSection,
        LSMStressBlock,
        LateralTie,
        RebarGroup,
        RebarHYSD,
        RebarLayer,
        RectBeamSection,
        RectColumnSection,
        ShearRebarGroup,
        Stirrups,
        mo,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analysis of Rectangular Sections under Flexure

    ### Singly Reinforced Section

    1. Rectangular section of overall dimensions $230 \times 450$ mm
    2. `sb` represents the concrete stress-strain relation for concrete for Limit State of Design as per IS456:2000
    3. `m20` represents M20 grade of concrete
    4. `fe415` represents Fe415 grade of rebars
    5. `_t1` is a layer of 3 bars [20, 16, 20] mm diameter of grade Fe415, placed with the centre of the rebars 35 mm above the tension edge
    6. `_steel` is a layer of rebars at a specific location within the cross section
    7. `_sh_steel` is a shear reinforcement arrangement in the form of 2 legged 8 mm dia vertical stirrups at 150 mm c/c of grade De415
    8. `_xu` is the calculated distance of the neutral axis from the compression edge
    9. The analysis of the section is presented in the report
    """)
    return


@app.cell
def _(
    Concrete,
    LSMStressBlock,
    RebarGroup,
    RebarHYSD,
    RebarLayer,
    RectBeamSection,
    ShearRebarGroup,
    Stirrups,
):
    sb = LSMStressBlock("LSM Flexure")
    m20 = Concrete("M20", 20)
    fe415 = RebarHYSD("Fe 415", 415)

    _t1 = RebarLayer(fe415, [20, 16, 20], -35)
    _steel = RebarGroup([_t1])
    _sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

    _sec = RectBeamSection(230, 450, sb, m20, _steel, _sh_st, 25)
    _xu = _sec.xu(0.0035)
    print(_sec.report(_xu, 0.0035))
    return fe415, m20, sb


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Doubly Reinforced Rectangular Section

    1. Rectangular section of overall dimensions $230 \times 450$ mm
    2. Concrete used is grade M20
    3. `_t1` is a layer of 2 bars [16, 16] mm diameter of grade Fe415, placed with the centre of the rebars 35 mm **below** the compression edge
    4. `_t2` is a layer of 3 bars [16, 16, 16] mm diameter of grade Fe415, placed with the centre of the rebars 35 mm **above** the tension edge
    5. `_steel` is the group of rebars on the compression and tension sides
    6. `_sh_steel` is a shear reinforcement arrangement in the form of 2 legged 8 mm dia vertical stirrups at 150 mm c/c of grade Fe415
    7. `_xu` is the calculated distance of the neutral axis from the compression edge
    8. The analysis of the section is presented in the report
    """)
    return


@app.cell
def _(
    RebarGroup,
    RebarLayer,
    RectBeamSection,
    ShearRebarGroup,
    Stirrups,
    fe415,
    m20,
    sb,
):
    _t1 = RebarLayer(fe415, [16, 16], 35)
    _t2 = RebarLayer(fe415, [16, 16, 16], -35)
    _steel = RebarGroup([_t1, _t2])
    _sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

    _sec = RectBeamSection(230, 450, sb, m20, _steel, _sh_st, 25)
    _xu = _sec.xu(0.0035)
    print(_sec.report(_xu, 0.0035))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Flanged Section under Flexure

    1. Section dimensions: $300 \times 475$ mm, $b_f = 800$ mm, $d_f = 150$ mm
    2. `m25` represents M25 grade concrete
    3. `_t1` is a layer of 2 bars [16, 16] mm diameter of grade Fe415, placed with the centre of the rebars 35 mm **above** the tension edge
    4. `_t2` is a layer of 2 bars [18, 18] mm diameter of grade Fe415, placed with the centre of the rebars 70 mm **above** the tension edge
    5. `_steel` is the group of rebars on the compression and tension sides
    6. `_sh_steel` is a shear reinforcement arrangement in the form of 2 legged 8 mm dia vertical stirrups at 150 mm c/c of grade Fe415
    7. `_xu` is the calculated distance of the neutral axis from the compression edge
    8. The analysis of the section is presented in the report
    """)
    return


@app.cell
def _(
    Concrete,
    FlangedBeamSection,
    RebarGroup,
    RebarLayer,
    ShearRebarGroup,
    Stirrups,
    fe415,
    sb,
):
    m25 = Concrete("M25", 25)

    _t1 = RebarLayer(fe415, [20, 20, 20], -35)
    _t2 = RebarLayer(fe415, [18, 18], -70)
    _main_steel = RebarGroup([_t1, _t2])
    _shear_steel = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])
    _tsec = FlangedBeamSection(300, 475, 800, 150, sb, m25, _main_steel, _shear_steel, 25)
    _xu = _tsec.xu(0.0035)
    print(_tsec.report(_xu, 0.0035))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rectangular Section under Axial Compression and Uniaxial Flexure

    1. Column dimensions: $230 \times 450$ mm
    2. Rebars in three layers
       * Fe415 3 - [16, 16, 16] at distance 50 mm from compression edge
       * Fe415 2 - [16, 16] at distance $\frac{D}{2}$ from compression edge
       * Fe415 3 - [16, 16, 16] at distance 50 mm from tension edge
    3. `_long_st` represents the three lyers of rebars
    4. `_lat_ties` repesents the lateral ties - Fe415 8 mm diameter at 150 mm c/c
    5. `_xu` is the assumed distance of neutral axis from the chighly compressed edge, taken as 900 mm
    6. `_k` is the normalized value of `_xu`
    7. The report of the analysis for the assumed `_xu` is printed
    """)
    return


@app.cell
def _(
    LSMStressBlock,
    LateralTie,
    RebarGroup,
    RebarLayer,
    RectColumnSection,
    fe415,
    m20,
):
    _b = 230
    _D = 450
    csb = LSMStressBlock("LSM Compression")

    _L1 = RebarLayer(fe415, [16, 16, 16], 50)
    _L2 = RebarLayer(fe415, [16, 16], _D / 2)
    _L3 = RebarLayer(fe415, [16, 16, 16], -50)
    _long_st = RebarGroup([_L1, _L2, _L3])
    _lat_ties = LateralTie(fe415, 8, 150)
    _colsec = RectColumnSection(_b, _D, csb, m20, _long_st, _lat_ties, 35)
    _xu = 900
    print(_colsec.report(_xu))
    return


if __name__ == "__main__":
    app.run()
