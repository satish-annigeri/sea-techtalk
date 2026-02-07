import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import math
    import pandas as pd
    from shapely import Polygon
    from sectionproperties.pre import Geometry
    from sectionproperties.analysis import Section
    from sectionproperties.analysis.plastic_section import PlasticSection

    from sectionproperties.pre.library import tapered_flange_channel, rectangular_hollow_section, tapered_flange_i_section
    return (
        Geometry,
        Polygon,
        Section,
        math,
        mo,
        pd,
        rectangular_hollow_section,
        tapered_flange_channel,
        tapered_flange_i_section,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Calculation of geometric properties of sections

    ## User defined polygonal shapes
    """)
    return


@app.cell
def _(Geometry, Polygon, Section):
    poly = Polygon([(0, 0), (5, 2), (3, 7), (1, 6)])
    _geom = Geometry(geom=poly)
    _geom.plot_geometry()
    _geom.create_mesh(5)
    _sec= Section(_geom)
    _sec.calculate_geometric_properties()
    _sec.display_results()
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Properties of standard rolled steel sections

    ## Channel section

    The properties of ISMC 150 taken from SP 6 (1) - 1964 are as follows:

    1. Dimensions: Depth of section $h=150$ mm, Width of flange $b = 75$ mm, Thickness of flange $t_f = 9.0$ mm, Thickness of web $t_w = 5.4$ mm, Radius at root $r_1= 10$ mm, Radius at toe $r_2 = 5$ mm, Slope of flange $D = 96$ degrees
    2. Geometric properties: Sectional area $a = 20.88$ cm$^2$, Moments of inertia $I_{xx} = 779.4$ cm$^4$, $I_{yy} = 102.3$ cm$^4$, Radii of gyration $r_{xx} = 6.11$ cm, $r_{2.21} = $ cm, Modulii of section $Z_{xx} = 103.9$ cm$^3$, $Z_{yy} = 19.4$ cm$^3$
    """)
    return


@app.cell
def _(Section, tapered_flange_channel):
    _geom = tapered_flange_channel(
        d=15,
        b=7.5,
        t_f=0.9,
        t_w=0.54,
        r_r=1.0,
        r_f=0.5,
        alpha=6,
        n_r=16,
    )
    _geom.create_mesh(mesh_sizes=0.05)
    _geom.plot_geometry()
    _sec = Section(geometry=_geom)
    _sec.calculate_geometric_properties()
    _area = _sec.get_area()
    _ixx, _iyy, _ = _sec.get_ic()
    _rxx, _ryy = _sec.get_rc()
    _zpx, _, _zpy, _ = _sec.get_zp()
    _res = f"Area={_area:.2f} cm^2, Ixx={_ixx:.2f} cm^4, Iyy={_iyy:.2f} cm^4, rxx={_rxx:.2f} cm, ryy={_ryy:.2f} cm\n"
    _res += f"Zpx={_zpx:.2f} cm^3, Zpy={_zpy:.2f} cm^3\n"
    _sec.display_results(fmt=".2f")
    _res
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Square hollow section
    """)
    return


@app.cell
def _(Section, rectangular_hollow_section):
    _geom = rectangular_hollow_section(b=100, d=100, t=1.6, r_in=1.6, r_out=3.2, n_r=8)
    _geom.plot_geometry()
    _geom.create_mesh(mesh_sizes=[100])
    _sec = Section(geometry=_geom)
    _sec.calculate_geometric_properties()
    _sec.display_results()
    return


@app.cell
def _(Section, tapered_flange_i_section):
    ismb300_geom = tapered_flange_i_section(d=300, b=140, t_f=12.4, t_w=7.5, r_r=14, r_f=7, alpha=8, n_r=8)
    ismb300_geom.plot_geometry()
    ismb300_geom.create_mesh(mesh_sizes=[100])
    ismb300_sec = Section(geometry=ismb300_geom)
    ismb300_sec.calculate_geometric_properties()
    ismb300_sec.calculate_plastic_properties()
    ismb300_sec.display_results(fmt=".2f")
    return (ismb300_geom,)


@app.cell
def _(Section, ismb300_geom, math):
    ismb300_r18 = ismb300_geom.rotate_section(angle=math.atan(1/3) * 180 / math.pi)
    # ismb300_r18 = ismb300_geom.rotate_section(angle=90)
    ismb300_r18.plot_geometry()
    ismb300_r18.create_mesh(mesh_sizes=[100])
    _sec = Section(geometry=ismb300_r18)
    _sec.calculate_geometric_properties()
    _sec.display_results(fmt=".2f")
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Calculate properties of section data read from Excel or CSV files
    """)
    return


@app.cell
def _(Section, mo, pd, tapered_flange_i_section):
    def calc_prop_isec(row):
        desig, d, b, t_f, t_w, r_r, r_f, alpha = row[['desig', 'd', 'b', 't_f', 't_w', 'r_r', 'r_f', 'alpha']]
        # print('===', d, b, t_f, t_w, r_r, r_f, alpha)
        geom = tapered_flange_i_section(d=d, b=b, t_f=t_f, t_w=t_w, r_r=r_r, r_f=r_f, alpha=alpha, n_r=8)
        # geom = tapered_flange_i_section(d=300, b=140, t_f=12.4, t_w=7.5, r_r=14, r_f=7, alpha=8, n_r=8)
        geom.create_mesh(mesh_sizes=[100])
        sec = Section(geometry=geom)
        sec.calculate_geometric_properties()
        sec.calculate_plastic_properties()
        a = sec.get_area()
        Ixx, Iyy, _ = sec.get_ic()
        Zxx, _, Zyy, _ = sec.get_z()
        Zpx, _, Zpy, _ = sec.get_z()
        # return desig, float(a), float(Ixx), float(Iyy), float(Zxx), float(Zyy)
        return pd.Series({"a": a, "Ixx": Ixx, "Iyy": Iyy, "Zxx": Zxx, "Zyy": Zyy, "Zpx": Zpx, "Zpy": Zpy})

    _isec = pd.read_excel("sp6_1.xlsx")
    _isec = _isec.astype({"desig": str, "d": float, "b": float, "t_f": float, "t_w": float, "r_r": float, "r_f": float, "alpha": float})
    _isec['alpha'] = _isec['alpha'] - 90.0
    # print(_isec.dtypes)
    # print(type(_isec))
    # _isec[["a", "Ixx", "Iyy", "rxx", "ryy", "Zpx", "Zpy"]] = None
    _isec[["a", "Ixx", "Iyy", "Zxx", "Zyy", "Zpx", "Zpy"]] = _isec.apply(calc_prop_isec, axis=1)
    _table = mo.ui.dataframe(
        df=_isec,
        format_mapping = {
            "a": "{:.2f}".format, "Ixx": "{:.2f}".format, "Iyy": "{:.2f}".format, "Zxx": "{:.2f}".format, "Zyy": "{:.2f}".format,
            "Zpx": "{:.2f}".format, "Zpy": "{:.2f}".format,
        }
    )
    _table
    return


if __name__ == "__main__":
    app.run()
