import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import math
    from dataclasses import dataclass, field
    import pandas as pd
    from sectionproperties.pre import Geometry
    from sectionproperties.analysis import Section
    from sectionproperties.pre.library import tapered_flange_i_section
    return Section, dataclass, field, math, pd, tapered_flange_i_section


@app.cell
def _(pd):
    sec_db = pd.read_excel("sp6_1.xlsx")
    sec_db["alpha"] = sec_db["alpha"] - 90
    sec_db
    return (sec_db,)


@app.cell
def _(Section, dataclass, field, math, pd, tapered_flange_i_section):
    @dataclass
    class ISection:
        desig: str
        fy: float = 250.0
        E: float = 2e5
        n_r: int = 32
        mesh_sizes: list[int] = field(default_factory=lambda: [100])
        section: Section | None = None

        def get_sec_prop(self, sec_db: pd.DataFrame):
            sec_list = sec_db[sec_db["desig"] == self.desig]
            if len(sec_list) == 0:
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

        def buckling_class(self) -> dict[str, str]:
            h_bf = self.props["d"] / self.props["b"]
            tf = self.props["t_f"]
            if h_bf > 1.2:
                if tf <= 40:
                    return {"zz": "a", "yy": "b"}
                elif 40 < tf <= 100:
                    return {"zz": "b", "yy": "c"}
                else:
                    raise ValueError(f"Invalid value for t_f={tf}")
            elif 0 < h_bf <= 1.2:
                if 0 < tf <= 100:
                    return {"zz": "b", "yy": "c"}
                elif tf > 100:
                    return {"zz": "d", "yy": "d"}
                else:
                    raise ValueError(f"Invalid value for t_f={tf}")

        @property
        def alpha(self) -> float:
            buckling_class = self.buckling_class()["zz"]
            match buckling_class:
                case "a": return 0.21
                case "b": return 0.34
                case "c": return 0.49
                case "d": return 0.76
                case _: raise ValueError(f"Invalid buckling class '{buckling_class}'")

        @property
        def class_of_section(self) -> str:
            epsilon = math.sqrt(250.0 / self.fy)
            b_tf = self.props["b"] / self.props["t_f"]
            if b_tf < 9.4 * epsilon:
                return "plastic"
            elif b_tf < 10.5 * epsilon:
                return "compact"
            elif b_tf < 15.7 * epsilon:
                return "semi-compact"
            else:
                return "slender"

        @property
        def beta_b(self) -> float:
            class_of_section = self.class_of_section
            if class_of_section in ["plastic", "compact"]:
                return 1.0
            elif class_of_section == "semi-compact":
                return self.Zxx / self.Sxx
            else:
                return 0.0

        @property
        def alpha_LT(self) -> float:
            return 0.21

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

        def Md(self, Leff: float, gamma_mo: float = 1.1, laterally_supported: bool=True, beam_type: str="simply supported") -> float:
            Zp = self.Sxx
            fbd = self.f_bd(Leff, gamma_mo, laterally_supported)
            Md = self.beta_b * Zp * fbd
    
            if laterally_supported:
                max_Md = section.Zxx * fbd
                if beam_type == "simply supported":
                    return min(1.2 * max_Md, Md)
                elif beam_type == "cantilever":
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
    Leff = 6e3
    try:
        sec = ISection("ISMB500")
        sec.get_sec_prop(sec_db)
        print(f"Area={sec.area:.2f}, Ixx={sec.Ixx:.2f}, Iyy={sec.Iyy:.2f}, Sxx={sec.Sxx:.2f}, Syy={sec.Syy:.2f}")
        print(f"rx={sec.rx:.2f}, ry={sec.ry:.2f}")
        print(f"Buckling class={sec.buckling_class()}, alpha={sec.alpha}, class={sec.class_of_section}, beta_b={sec.beta_b}")
        print(f"chi_LT={sec.chi_LT(Leff):.2f}")
        print(f"Md={sec.Md(Leff, gamma_mo=1.1, laterally_supported=False)/1e6:.2f} kNm")
    except Exception as e:
        print(f"Error: {e}")
    return Leff, sec


@app.cell
def _(Leff, sec):
    print(f"f_crb={sec.f_crb(Leff):.2f}")
    print(f"f_bd={sec.f_bd(Leff, laterally_supported=False):.2f}")
    return


if __name__ == "__main__":
    app.run()
