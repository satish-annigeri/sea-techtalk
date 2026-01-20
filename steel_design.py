import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import math
    from enum import Enum
    from dataclasses import dataclass, field
    import pandas as pd
    from sectionproperties.pre import Geometry
    from sectionproperties.analysis import Section
    from sectionproperties.pre.library import tapered_flange_i_section
    return Enum, Section, dataclass, field, math, pd, tapered_flange_i_section


@app.cell
def _(Enum):
    class MemberType(Enum):
        BEAM = 1
        COLUMN = 2
        TRUSS_COMPRESSION = 3
        TRUSS_TENSION = 4

    class BeamType(Enum):
        SIMPLY_SUPPORTED = 1
        CANTILEVER = 2

    class SectionClass(Enum):
        PLASTIC = 1
        COMPACT = 2
        SEMI_COMPACT = 3
        SLENDER = 4

        def __str__(self) -> str:
            return f"{self.name.capitalize()}"

    class SectionBucklingClass(Enum):
        a = 1
        b = 2
        c = 3
        d = 4

        def __str__(self) -> str:
            return f"Buckling Class {self.name}"
    return BeamType, SectionBucklingClass, SectionClass


@app.cell
def _(pd):
    sec_db = pd.read_excel("sp6_1.xlsx")
    sec_db["alpha"] = sec_db["alpha"] - 90
    sec_db
    return (sec_db,)


@app.cell
def _(
    BeamType,
    Section,
    SectionBucklingClass,
    SectionClass,
    dataclass,
    field,
    math,
    pd,
    tapered_flange_i_section,
):
    @dataclass
    class ISection:
        desig: str
        fy: float = 250.0
        E: float = 2e5
        n_r: int = 32
        mesh_sizes: list[int] = field(default_factory=lambda: [100])
        section: Section | None = None

        def get_sec_prop(self, sec_db: pd.DataFrame, w: float=0.0):
            sec_list = sec_db[sec_db["desig"] == self.desig]
            if len(sec_list) > 1 and w > 0:
                sec_list = sec_list[sec_list["w"] == w]
            elif len(sec_list) == 0:
                raise ValueError(f"Invalid section designation '{self.desig}'")

            props = sec_list.iloc[0].to_dict()
            geom = tapered_flange_i_section(b=props["b"], d=props["d"], t_f=props["t_f"], t_w=props["t_w"], r_r=props["r_r"], r_f=props["r_f"], alpha=props["alpha"], n_r=self.n_r)
            self.props = props
            geom.create_mesh(mesh_sizes=self.mesh_sizes)
            self.section = Section(geometry=geom)
            self.section.calculate_geometric_properties()
            self.section.calculate_plastic_properties()

        @property
        def area(self) -> float:
            return self.section.get_area()

        @property
        def Ixx(self) -> float:
            return self.section.get_ic()[0]

        @property
        def Iyy(self) -> float:
            return self.section.get_ic()[1]

        @property
        def Zxx(self) -> float:
            return self.section.get_zp()[0]

        @property
        def Zyy(self) -> float:
            return self.section.get_zp()[1]

        @property
        def Sxx(self) -> float:
            return self.section.get_sp()[0]

        @property
        def Syy(self) -> float:
            return self.section.get_sp()[1]

        @property
        def rx(self) -> float:
            return self.section.get_rc()[0]

        @property
        def ry(self) -> float:
            return self.section.get_rc()[1]

        def buckling_class(self) -> dict[str, SectionBucklingClass]:
            h_bf = self.props["d"] / self.props["b"]
            tf = self.props["t_f"]
            if h_bf > 1.2:
                if tf <= 40:
                    return {"zz": SectionBucklingClass.a, "yy": SectionBucklingClass.b}
                elif 40 < tf <= 100:
                    return {"zz": SectionBucklingClass.b, "yy": SectionBucklingClass.c}
                else:
                    raise ValueError(f"Invalid value for t_f={tf}")
            elif 0 < h_bf <= 1.2:
                if 0 < tf <= 100:
                    return {"zz": SectionBucklingClass.b, "yy": SectionBucklingClass.c}
                elif tf > 100:
                    return {"zz": SectionBucklingClass.d, "yy": SectionBucklingClass.d}
                else:
                    raise ValueError(f"Invalid value for t_f={tf}")

        def alpha_(self, axis: str) -> float:
            buckling_class = self.buckling_class()[axis]
            match buckling_class:
                case SectionBucklingClass.a: return 0.21
                case SectionBucklingClass.b: return 0.34
                case SectionBucklingClass.c: return 0.49
                case SectionBucklingClass.d: return 0.76
                case _: raise ValueError(f"Invalid buckling class '{buckling_class}'")

        def fcc(self, Leff: float, r: float) -> float:
            return math.pi**2 * self.E / (Leff / r)**2

        def lambda_(self, Leff: float, r: float) -> float:
            return math.sqrt(self.fy / self.fcc(Leff, r))

        def phi_(self, Leff: float, r: float, axis: str) -> float:
            alpha_ = self.alpha_(axis)
            lambda_ = self.lambda_(Leff, r)
            return 0.5 * (1 + alpha_ * (lambda_ - 0.2) + lambda_**2)

        def chi_(self, Leff: float, r: float, axis) -> float:
            phi_ = self.phi_(Leff, r, axis)
            lambda_ = self.lambda_(Leff, r)
            return 1.0 / (phi_ + math.sqrt(phi_**2 - lambda_**2))

        def f_cd(self, Leff: float, r: float, gamma_mo: float, axis: str) -> float:
            return min(1.0, self.chi_(Leff, r, axis)) * self.fy / gamma_mo

        def Pd(self, Leff: float, r: float, gamma_mo: float, axis: str) -> float:
            fcd = self.f_cd(Leff, r, gamma_mo, axis)
            area = self.area
            return area * fcd
        
        @property
        def class_of_section(self) -> SectionClass:
            epsilon = math.sqrt(250.0 / self.fy)
            b_tf = self.props["b"] / self.props["t_f"]
            if b_tf < 9.4 * epsilon:
                return SectionClass.PLASTIC
            elif b_tf < 10.5 * epsilon:
                return SectionClass.COMPACT
            elif b_tf < 15.7 * epsilon:
                return SectionClass.SEMI_COMPACT
            else:
                return SectionClass.SLENDER

        @property
        def beta_b(self) -> float:
            class_of_section = self.class_of_section
            if class_of_section in [SectionClass.PLASTIC, SectionClass.COMPACT]:
                return 1.0
            elif class_of_section == SectionClass.SEMI_COMPACT:
                return self.Zxx / self.Sxx
            else:
                return 0.0

        @property
        def alpha_LT(self) -> float:
            return 0.21

        def lambda_LT(self, Leff: float) -> float:
            return math.sqrt(self.fy / self.f_crb(Leff))

        def phi_LT(self, Leff: float) -> float:
            lambda_LT = self.lambda_LT(Leff)
            alpha_LT = self.alpha_LT
            return 0.5 * (1 + alpha_LT * (lambda_LT - 0.2) + lambda_LT**2)

        def chi_LT(self, Leff: float) -> float:
            phi_LT = self.phi_LT(Leff)
            lambda_LT = self.lambda_LT(Leff)
            return min(1.0, 1 / (phi_LT + math.sqrt(phi_LT**2 - lambda_LT**2)))

        def f_crb(self, Leff: float) -> float:
            ry = self.ry
            tf = self.props["t_f"]
            hf = self.props["d"] - tf
            Leff_ry = Leff / ry
            return 1.1 * math.pi**2 *  self.E / Leff_ry**2 * math.sqrt(1 + (Leff_ry / (hf / tf))**2 / 20)

        def f_bd(self, Leff: float, gamma_mo: float=1.1, laterally_supported: bool = True) -> float:
            if laterally_supported:
                return self.fy / gamma_mo
            else:
                return self.chi_LT(Leff) * self.fy / gamma_mo

        def Md(self, Leff: float, gamma_mo: float = 1.1, laterally_supported: bool=True, beam_type: BeamType=BeamType.SIMPLY_SUPPORTED) -> float:
            Zp = self.Sxx
            fbd = self.f_bd(Leff, gamma_mo, laterally_supported)
            Md = self.beta_b * Zp * fbd

            if laterally_supported:
                max_Md = section.Zxx * fbd
                if beam_type == BeamType.SIMPLY_SUPPORTED:
                    return min(1.2 * max_Md, Md)
                elif beam_type == BeamType.CANTILEVER:
                    return min(1.5 * max_Md, Md)
                else:
                    raise ValueError(f"Invalid bame_type='{beam_type}'")
            else:
                return Md

        @property
        def Av(self) -> float:
            return self.props["d"] * self.props["t_w"]

        def Vp(self) -> float:
            return self.Av * self.fy / math.sqrt(3.0)
    return (ISection,)


@app.cell
def _(ISection, sec_db):
    _Leff = 6e3
    try:
        sec = ISection("ISMB500")
        sec.get_sec_prop(sec_db)
        print(f"Area={sec.area:,.2f}, Ixx={sec.Ixx:,.2f}, Iyy={sec.Iyy:,.2f}, Sxx={sec.Sxx:,.2f}, Syy={sec.Syy:,.2f}")
        print(f"rx={sec.rx:,.2f}, ry={sec.ry:,.2f}")
        print(f"zz: {sec.buckling_class()['zz']} yy: {sec.buckling_class()['yy']}, alpha={sec.alpha_("zz")}, class={sec.class_of_section}, beta_b={sec.beta_b}")
        print(f"chi_LT={sec.chi_LT(_Leff):,.2f}")
        print(f"Md={sec.Md(_Leff, gamma_mo=1.1, laterally_supported=False)/1e6:,.2f} kNm")
        print(f"f_crb={sec.f_crb(_Leff):,.2f}")
        print(f"f_bd={sec.f_bd(_Leff, laterally_supported=False):,.2f}")
    except Exception as e:
        print(f"Error: {e}")
    return


@app.cell
def _(ISection, sec_db):
    ishb300 = ISection("ISHB300")
    ishb300.get_sec_prop(sec_db)
    _Leff = 3e3
    _r = min(ishb300.rx, ishb300.ry)
    lambda_ = ishb300.lambda_(_Leff, _r)
    phi_ = ishb300.phi_(_Leff, _r, axis="yy")
    _fcc = ishb300.fcc(_Leff, _r)
    _chi = ishb300.chi_(_Leff, _r, "yy")
    _fcd = ishb300.f_cd(_Leff, _r, 1.1, "yy")
    print(f"{ishb300.buckling_class()['zz']}, {ishb300.buckling_class()['yy']}, r_min={_r:,.6f}, alpha={ishb300.alpha_(axis="yy"):,.2f}, lambda={lambda_:.6f}, phi={phi_:.6f}, fcc={_fcc:.2f}, chi={_chi:.6f}, fcd={_fcd:.2f}")
    print(f"Pd={ishb300.Pd(_Leff, _r, 1.1, "yy")/1e3:.2f} kN")
    return


if __name__ == "__main__":
    app.run()
