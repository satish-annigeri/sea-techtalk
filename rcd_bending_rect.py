from fractions import Fraction as F
import math
from enum import Enum
from collections import OrderedDict
from typing import ClassVar
from typing_extensions import Annotated
from dataclasses import dataclass
from abc import ABC, abstractmethod

import numpy as np

# import matplotlib.pyplot as plt
from numpy.typing import NDArray

from brent import find_bracket, brent_root, bisection

Array2D = Annotated[NDArray[np.float64], ("n", "m")]


def interpolate_xy(xy: Array2D, x: float) -> float:
    if x < xy[0, 0] or x > xy[-1, 0]:
        return 0.0
    for i in range(len(xy)):
        if math.isclose(x, xy[i, 0]):
            return xy[i, 1]
        elif x < xy[i, 0]:
            x1 = xy[i - 1, 0]
            y1 = xy[i - 1, 1]
            x2 = xy[i, 0]
            y2 = xy[i, 1]
            y = y1 + (y2 - y1) / (x2 - x1) * (x - x1)
            return y
    return 0.0


class FlexuralMemberType(Enum):
    BEAM = 1
    SLAB = 2


class ShearReinforcementType(Enum):
    VERTICAL_STIRRUP = 1
    INCLINED_STIRRUP = 2
    SERIES_BENTUP_BARS = 3
    BENTUP_BARS = 4


@dataclass
class Concrete:
    fck: float
    ecy: ClassVar[float] = 0.002
    ecu: ClassVar[float] = 0.0035

    def __post_init__(self):
        self.label = f"M{self.fck}"

    @property
    def fd(self):
        return F(4, 9) * self.fck

    def fc(self, ec: float) -> float:
        if (ec <= 0) or (ec > self.ecu):
            return 0.0
        elif self.ecy <= ec <= self.ecu:
            return self.fd
        else:
            ec_ecy = ec / self.ecy
            return self.fd * (2 * ec_ecy - ec_ecy**2)

    def tau_cmax(self) -> float:
        table20 = np.array(
            [[15, 20, 25, 30, 35, 40], [2.5, 2.8, 3.1, 3.5, 3.7, 4.0]], dtype=float
        ).T

        if self.fck >= table20[-1, 0]:
            return table20[-1, 1]
        elif self.fck <= table20[0, 0]:
            return table20[0, 1]

        for i in range(len(table20)):
            if self.fck == table20[i, 0]:
                return table20[i, 1]
        return 0.0

    def tau_c(self, pt: float) -> float:
        beta = max(1.0, 0.8 * self.fck / (6.89 * pt))
        tau_c = (
            0.85 * (0.8 * self.fck) ** 0.5 * ((1 + 5 * beta) ** 0.5 - 1) / (6 * beta)
        )
        return tau_c


class RebarType(Enum):
    UNDEFINED = 0
    MS = 1
    HYSD = 2


ep: Array2D = np.array(
    [[0, 0, 0.0001, 0.0003, 0.0007, 0.001, 0.002], [0, 0.8, 0.85, 0.9, 0.95, 0.975, 1]]
).T


@dataclass
class Rebar(ABC):
    fy: float
    rebar_type: RebarType = RebarType.UNDEFINED
    label: str = ""
    Es: ClassVar[float] = 2e5

    @abstractmethod
    def fs(self, es: float) -> float: ...

    @property
    def fd(self) -> float:
        return 100 / 115 * self.fy


@dataclass
class RebarMS(Rebar):
    def __post_init__(self):
        self.reabr_type: RebarType = RebarType.MS
        if not self.label:
            self.label = f"{self.rebar_type} {self.fy}"

        self.es_fs = np.array([[0.0, self.fd / self.Es], [0.0, self.fd]]).T

    def fs(self, es: float) -> float:
        _es = abs(es)
        fsy = self.es_fs[1, 1]
        if _es < fsy / self.Es:
            return es * self.Es
        else:
            return math.copysign(fsy, es)


@dataclass
class RebarHYSD(Rebar):
    def __post_init__(self):
        self.rebar_type = RebarType.HYSD
        if not self.label:
            self.label = f"{self.rebar_type} {self.fy}"

        _ep: Array2D = np.array(
            [
                [0.0, 0.0, 0.0001, 0.0003, 0.0007, 0.001, 0.002],
                [0.0, 0.8, 0.85, 0.9, 0.95, 0.975, 1.0],
            ]
        ).T
        self.es_fs = np.zeros(_ep.shape)
        self.es_fs = self.HYSD_es_fs(_ep)

    def HYSD_es_fs(self, ep: Array2D):
        es_fs = np.zeros(ep.shape)
        es_fs[:, 1] = self.fd * ep[:, 1]
        es_fs[:, 0] = es_fs[:, 1] / self.Es + ep[:, 0]
        return es_fs

    def fs(self, es: float) -> float:
        _es = abs(es)
        if _es <= self.es_fs[1, 0]:
            return es * self.Es
        elif _es >= self.es_fs[-1, 0]:
            return math.copysign(self.es_fs[-1, 1], es)
        else:
            # _es lies between FSD * 0.8 fy and FSD * fy
            i = 2
            numrows = self.es_fs.shape[0]
            while (_es > self.es_fs[i, 0]) and (i < numrows):
                i += 1
            if i > numrows:
                raise ValueError(f"Invalid strain value {es}")
            # print(i, es_fs[i, :])
            if math.isclose(_es, self.es_fs[i, 0]):
                return math.copysign(self.es_fs[i, 1], es)
            else:
                x1 = self.es_fs[i - 1, 0]
                y1 = self.es_fs[i - 1, 1]
                x2 = self.es_fs[i, 0]
                y2 = self.es_fs[i, 1]
                fs = y1 + (y2 - y1) / (x2 - x1) * (_es - x1)
                return math.copysign(fs, es)


@dataclass
class ShearReinforcement(ABC):
    rebar: Rebar
    dia: float
    nlegs: int
    alpha: float = 90.0

    @property
    def nbars(self) -> int:
        return self.nlegs

    @nbars.setter
    def nbars(self, value: int):
        self.nlegs = value

    @property
    def Asv(self) -> float:
        return self.nlegs * (math.pi * self.dia**2 / 4)

    def sv_max(self, b: float, d: float) -> float:
        if self.alpha == 45:
            sv1 = d
        elif self.alpha == 90:
            sv1 = 0.75 * d
        else:
            sv1 = 0.75 * d

        return min(sv1, self.rebar.fd * self.Asv / (0.4 * b), 300.0)

    @abstractmethod
    def sv(self, Vus: float, b: float, d: float) -> float:
        pass


@dataclass
class Stirrups(ShearReinforcement):
    def __post_init__(self):
        if self.alpha == 90:
            self._type = ShearReinforcementType.VERTICAL_STIRRUP
        else:
            self._type = ShearReinforcementType.INCLINED_STIRRUP

    def sv(self, Vus: float, b: float, d: float) -> float:
        sv1 = self.rebar.fd * self.Asv * d / Vus
        if self.alpha != 90:  # Inclined stirrups
            alpha_rad = self.alpha * math.pi / 180.0
            sv1 *= math.sin(alpha_rad) + math.cos(alpha_rad)
        return sv1


@dataclass
class SeriesBentupBars(Stirrups):
    def __post_init__(self):
        self._type = ShearReinforcementType.SERIES_BENTUP_BARS
        self.alpha = 45.0


class StressBlock(ABC):
    @abstractmethod
    def area(self, z1: float, z2: float) -> float: ...

    @abstractmethod
    def moment(self, z1: float, z2: float) -> float: ...

    @abstractmethod
    def centroid(self, z1: float, z2: float) -> float: ...


@dataclass
class CSB(StressBlock):
    k: float

    def __post_init__(self):
        if self.k < 0:
            raise ValueError(f"k = {self.k} must not be negative")
        if self.k <= 1:
            self.alpha_k = F(4, 7) * self.k
        else:
            self.alpha_k = self.k - F(3, 7)

    def z_values(
        self, z1: float, z2: float
    ) -> tuple[tuple[float | None, float | None], tuple[float | None, float | None]]:
        if z1 > z2:  # Interchange z1 and z2 if z1 > z2
            z1, z2 = z2, z1

        if self.k >= 0:  # NA not negative
            if z2 <= self.alpha_k:  # Parabolic only
                return (z1, z2), (None, None)
            elif z1 >= self.alpha_k:  # Constant only
                return (None, None), (z1, z2)
            else:  # Partly parabolic and partly constant
                return (z1, self.alpha_k), (self.alpha_k, z2)
        else:  # self.k cannot be less than zero
            raise ValueError(f"k = {self.k} must not be less than zero")

    def area_p(self, z1: float, z2: float) -> float:
        """Area of parabolic portion of stress block assuming both z1 and z2
        lie within parabolic portion. No checks are made"""
        return (z2**2 - z1**2) / self.alpha_k - (z2**3 - z1**3) / (3 * self.alpha_k**2)

    def area_r(self, z1: float, z2: float) -> float:
        """Area of constant portion of stress block assuming both z1 and z2
        lie within constant portion. No checks are made"""
        return z2 - z1

    def moment_p(self, z1: float, z2: float) -> float:
        """Moment of parabolic portion of stress block assuming both z1 and z2
        lie within parabolic portion. No checks are made"""
        return 2 * (z2**3 - z1**3) / (3 * self.alpha_k) - (z2**4 - z1**4) / (
            4 * self.alpha_k**2
        )

    def moment_r(self, z1: float, z2: float) -> float:
        """Moment of constant portion of stress block assuming both z1 and z2
        lie within constant portion. No checks are made"""
        return (z2**2 - z1**2) / 2

    def area(self, _z1: float, _z2: float) -> float:
        """z1 znd z1 are measured from the NA towards the highly compressed edge.
        0 <= z1 <= z2 <= infinity"""
        if _z1 > _z2:
            _z1, _z2 = _z2, _z1
        zp, zc = self.z_values(_z1, _z2)
        z1, z2 = zp
        z3, z4 = zc
        # print(f"{z1=} {z2=} {z3=} {z4=}")
        if z1 is None and z2 is None:  # Parabolic
            Ap = 0.0
        else:
            Ap = (z2**2 - z1**2) / self.alpha_k - (z2**3 - z1**3) / (
                3 * self.alpha_k**2
            )
        if z3 is None and z4 is None:  # Constant
            Ac = 0.0
        else:
            Ac = z4 - z3
        # print(f"{Ap=}, {Ac=}")
        return Ap + Ac

    def moment(self, _z1: float, _z2: float) -> float:
        """z1 znd z1 are measured from the NA towards the highly compressed edge. 0 <= z1 <= z2 <= infinity"""
        zp, zc = self.z_values(_z1, _z2)
        z1, z2 = zp
        z3, z4 = zc
        # print(f"{z1=} {z2=} {z3=} {z4=}")
        if z1 is None and z2 is None:  # Parabolic
            Mp = 0.0
        else:
            Mp = 2 * (z2**3 - z1**3) / (3 * self.alpha_k) - (z2**4 - z1**4) / (
                4 * self.alpha_k**2
            )
        if z3 is None and z4 is None:  # Constant
            Mc = 0.0
        else:
            Mc = (z4**2 - z3**2) / 2
        # print(f"{Mp=} {Mc=}")
        return Mp + Mc

    def centroid(self, z1: float, z2: float) -> float:
        """z1 znd z1 are measured from the NA towards the highly compressed edge. 0 <= z1 <= z2 <= infinity"""
        return self.k - self.moment(z1, z2) / self.area(z1, z2)


@dataclass
class RectBeamSection:
    b: float
    D: float
    clear_cover: float
    conc: Concrete
    tbars: Rebar
    cbars: Rebar
    vbars: Rebar
    tbar_dia: float = 20
    cbar_dia: float = 20
    vbar_dia: float = 6
    member_type: FlexuralMemberType = FlexuralMemberType.BEAM

    @property
    def d(self) -> float:
        return self.D - self.dc  # assuming a single layer of tension bars

    @property
    def dc(self) -> float:
        return (
            self.clear_cover + self.cbar_dia / 2
        )  # assuming a single layer of tension bars

    @property
    def Mulim(self) -> float:
        # xumax = self.xumax_d() * self.d
        return self.Mu(self.xumax)

    def ptlim_fy_fck(self) -> float | F:
        return F(115, 1) * self.Ac() * self.xumax_d()

    def xumax_d(self) -> float:
        return self.conc.ecu / (
            self.conc.ecy + self.conc.ecu + self.tbars.fd / self.tbars.Es
        )

    @property
    def xumax(self) -> float:
        return self.xumax_d() * self.d

    def Ac(self) -> F:
        A1 = F(2, 3) * F(4, 7)
        A2 = F(3, 7)
        return F(4, 9) * (A1 + A2)

    def Mc(self) -> F:
        A1 = F(2, 3) * F(4, 7)
        x1 = F(5, 8) * F(4, 7)
        A2 = F(3, 7)
        x2 = F(4, 7) + F(1, 2) * F(3, 7)
        Mc = A1 * x1 + A2 * x2
        return F(4, 9) * Mc

    def xbar(self) -> float | F:
        A = self.Ac()
        M = self.Mc()
        xx = M / A
        return F(1, 1) - xx

    def Mu(self, xu: float) -> float:
        xumax = self.xumax
        if xu > xumax:
            raise ValueError(f"xu = {xu} cannot exceed {xumax}")
        if xu > self.D:
            raise ValueError(f"xu = {xu} must lie within the section for bending")
        k = xu / self.D
        csb = CSB(k)
        A = csb.area(0, k) * self.conc.fd * self.D
        # M = csb.moment(0, k)
        xbar = csb.centroid(0, k) * self.D
        Mu = A * self.b * (self.d - xbar)
        # print(f"{k=}, {csb.area(0, k)} {A=}, {xbar=}, {Mu=}")
        return Mu

    def reqd_xu_d(self, Mu: float) -> float | F:
        """Required x_u can be calculated explicitly for an under-reinforced rectangular section"""
        return F(238, 198) - math.sqrt(
            F(238, 198) ** 2 - F(147, 22) * Mu / (self.conc.fck * self.b * self.d**2)
        )

    def reqd_Ast(self, Mu: float) -> float | F:
        xu = self.reqd_xu_d(Mu) * self.d
        Ast = Mu / (self.tbars.fd * (self.d - self.xbar() * xu))
        return Ast

    def get_Asc(self, Mu: float) -> tuple[float, float]:
        # Mulim = get_Mulim_fck_bd2(self.tbars.fy) * self.conc.fck * self.b * self.d**2
        if Mu > self.Mulim:  # Doubly reinforced section
            xumax = self.xumax
            Ast1 = (
                self.ptlim_fy_fck()
                * self.conc.fck
                / self.tbars.fy
                * self.b
                * self.d
                / 100
            )
            esc = self.conc.ecu / xumax * (xumax - self.dc)
            fcc = self.conc.fc(esc)
            fsc = self.cbars.fs(esc)
            Mu2 = Mu - self.Mulim
            Asc = Mu2 / ((fsc - fcc) * (self.d - self.dc))
            Ast2 = Asc * (fsc - fcc) / (self.tbars.fd)
            return Asc, Ast1 + Ast2
        else:  # Singly reinforced section
            return 0.0, 0.0, 0.0

    def Asc_Ast(self, Mu: float, factor: float = 1.0) -> tuple[float, float]:
        if Mu <= factor * self.Mulim:  # Singly reinforced section
            Asc = 0.0
            Ast = self.reqd_Ast(Mu)
        else:  # Doubly reinforced section
            Asc, Ast = self.get_Asc(Mu)
        return Asc, Ast

    def __str__(self) -> str:
        return f"Rectangular Section: {self.b}x{self.D} Concrete: {self.conc.label} Tension bars: {self.tbars.label}"

    def tau_cmax(self) -> float:
        tau_c = self.conc.tau_cmax()
        match self.member_type:
            case FlexuralMemberType.BEAM:
                return tau_c
            case FlexuralMemberType.SLAB:
                return tau_c / 2.0
            case _:
                raise ValueError(f"Error: Invalid member type {self.member_type}")

    def tau_c(self, Ast: float) -> float:
        pt = Ast * 100 / (self.b * self.d)
        tauc = self.conc.tau_c(pt)

        if self.member_type == FlexuralMemberType.BEAM:
            return tauc
        elif self.member_type == FlexuralMemberType.SLAB:
            if self.D <= 150:
                k = 1.3
            elif self.D >= 300:
                k = 1.0
            else:
                xy = np.array(
                    [
                        [150, 175, 200, 225, 250, 275, 300],
                        [1.3, 1.25, 1.2, 1.15, 1.1, 1.05, 1.0],
                    ]
                ).T
                k = interpolate_xy(xy, self.D)
            return k * tauc
        else:
            raise ValueError(f"Invalid member type {self.member_type}")

    def Asv_sv(self, Ast: float, Vu: float, Tu: float, alpha: float = 90) -> float:
        alpha_rad = math.radians(alpha)
        tau_v = Vu / (self.b * self.d)
        tau_c = self.tau_c(Ast)
        tau_cmax = self.tau_cmax()
        if tau_v > tau_cmax:
            raise ValueError(
                f"Shear stress tau_v = {tau_v:.2f} N/mm^2 exceeds maximum shear stress tau_cmax = {tau_cmax:.2f} N/mm^2"
            )
        elif tau_v < tau_c:
            return 0.4 * self.b / self.vbars.fd
        else:
            Vus = Vu - tau_c * self.b * self.d
            return Vus / (
                self.vbars.fd * self.d * (math.sin(alpha_rad) + math.cos(alpha_rad))
            )

    def design_section(
        self, Mu: float, Vu: float, Tu: float = 0.0
    ) -> tuple[float, float]:
        Mt = Tu * (1 + self.D / self.b) / 1.7
        Asc, Ast = self.Asc_Ast(Mu + Mt)
        nlegs = 2
        Asv = nlegs * self.vbar_dia**2 * math.pi / 4
        Asv_sv = self.Asv_sv(Ast, Vu, Tu)
        sv = min(Asv / Asv_sv, self.d)
        return Asc, Ast, sv


@dataclass
class FlangedSection(RectBeamSection):
    bf: float = 0.0
    df: float = 0.0

    @property
    def bw(self) -> float:
        return self.b

    @property
    def Mulim(self):
        """Limiting moment of resistance of flanged sections"""
        xumax = self.xumax
        return self.Mu(xumax)

    def Mu(self, xu: float) -> float:
        xumax = self.xumax
        # print(f"{xumax=}", end=" ")
        if xu > xumax:
            raise ValueError(f"xu ({xu}) > xumax={xumax}")

        if 0 <= xu <= self.D:  # NA lies within the section for bending
            k = xu / self.D
            # print(f"*** {xu=} {self.df=} {k=} {xu * float(F(3, 7))}")
            csb = CSB(k)
            if xu <= self.df:  # NA within the flange
                z1 = 0
                z2 = k
                A = csb.area(z1, z2)
                x_bar = csb.centroid(z1, z2) * self.D
                Mu = self.conc.fd * self.D * A * self.bf * (self.d - x_bar)
                # print(f"{z1=} {z2=} {A=} {Mu=}")
            else:  # NA outside the flange
                Mw = super().Mu(xu)
                if self.df <= xu * F(
                    3, 7
                ):  # Flange very thin flange and stress in flange is constant
                    z1 = (xu - self.df) / self.D
                    z2 = k
                    Af = self.conc.fd * self.D * csb.area(z1, z2) * (self.bf - self.bw)
                    x_bar = csb.centroid(z1, z2) * self.D
                    Mf = Af * (self.d - x_bar)
                    Mu = Mw + Mf
                    # print(f"Thin flange: CSB Area = {csb.area(z1, z2)} centroid = {x_bar} {Af=} {Mw=} {Mf=} {Mu=}")
                    # print(f"Thick flange: {Mw=} {Mf=} {Mu=}")
                else:  # Flange thick, stress in flange is parabolic + constant
                    z1 = (xu - self.df) / self.D
                    z2 = k
                    Af = self.conc.fd * self.D * csb.area(z1, z2) * (self.bf - self.bw)
                    x_bar = csb.centroid(z1, z2) * self.D
                    Mf = Af * (self.d - x_bar)
                    Mu = Mw + Mf
                    # print(f"Thick flange: {Mw=} {Mf=} {Mu=}")
            return Mu
        else:
            raise ValueError(f"Distance of NA x_u = {xu} > {self.D}")

    def reqd_xu(self, Mu: float) -> float:
        def find_xu(xu: float, reqd_Mu: float) -> float:
            return reqd_Mu - self.Mu(xu)

        xumax = self.xumax
        Mulim = self.Mulim
        # print(f"{xumax=} {Mulim=}")
        if xumax <= self.df:  # NA lies within the flange
            reqd_xu = F(238, 198) - math.sqrt(
                F(238, 198) ** 2
                - F(147, 22) * Mu / (self.conc.fck * self.bf * self.d**2)
            )
            # print(f"1: Rectangular section {self.bf} x {self.d} {reqd_xu * self.d}")
            return reqd_xu * self.d
        else:  # NA lies below the flange
            Mu1 = self.Mu(self.df)
            if Mu <= Mu1:  # Required NA lies within the flange
                reqd_xu = F(238, 198) - math.sqrt(
                    F(238, 198) ** 2
                    - F(147, 22) * Mu / (self.conc.fck * self.bf * self.d**2)
                )
                # print(f"2: Rectangular section {self.bf} x {self.d} {reqd_xu * self.d}")
                return reqd_xu * self.d
            else:  # Required NA lies below flange
                Mulim = self.Mulim
                if Mu <= Mulim:  # Singly reinforced flanged section
                    # print(f"3: NA below flange Singly reinforced: {Mu=} {Mulim=}")
                    try:
                        bracket = find_bracket(
                            find_xu, self.df, self.xumax, 10, reqd_Mu=Mu
                        )
                        reqd_xu = brent_root(
                            find_xu, bracket[0], bracket[1], reqd_Mu=Mu
                        )
                        return reqd_xu
                    except Exception as e:
                        raise ValueError("Error: FlangedSection.reqd_xu() failed")
                else:  # Doubly reinforced flanged section
                    print(f"4: NA below flange Doubly reinforced: {Mu=} {Mulim=}")
                    return 0.0

    def __str__(self) -> str:
        s = f"Flanged Section: {self.bw}x{self.D} "
        if self.bf and self.df:
            s += f"bf={self.bf} df={self.df}"
        return s


@dataclass
class RectColumnSection:
    b: float
    D: float
    dc: float
    conc: Concrete
    steel: Rebar
    total_As: float
    xu: float = 0.0

    def __str__(self) -> str:
        s = f"Rectangular Column Section: {self.b}x{self.D} dc = {self.dc} "
        s += f"Concrete: {self.conc.label} Steel: {self.steel.label} Ast={self.total_As:.2f} mm^2"
        return s

    def Pu_Mu(
        self, xu: float, report: bool = False
    ) -> tuple[float, float, OrderedDict]:
        self.xu = xu
        # print(xu, self.xu)
        k = self.xu / self.D
        data = OrderedDict()
        if report:
            data["size"] = (self.b, self.D)
            data["concrete"] = self.conc
            data["steel"] = self.steel
            data["total_As"] = self.total_As
            data["xu"] = self.xu
            data["k"] = k

        # Concrete stress block
        if k <= 1:
            z1 = 0.0
            es_max = self.conc.ecu
        else:
            z1 = k - 1
            es_max = self.conc.ecy * k / (k - F(3, 7))
        z2 = k
        if report:
            data["es_max"] = es_max

        csb = CSB(k)
        Ac = csb.area(z1, z2)
        Pc = Ac * self.conc.fd * self.D * self.b
        Mc = csb.moment(z1, z2) * self.conc.fd * self.D**2 * self.b

        if report:
            data["Pc"] = Pc
            data["Mc"] = Mc

        # Steel reinforcement bars
        # Least compressed or tension bars
        As1 = self.total_As / 2
        x1 = xu - self.D + self.dc
        As2 = As1
        x2 = xu - self.dc
        xy = xu - self.D * 3 / 7
        es1 = self.conc.ecy * x1 / xy
        es2 = self.conc.ecy * x2 / xy

        # Highly compressed bars
        fs1 = self.steel.fs(es1)
        fs2 = self.steel.fs(es2)
        fc1 = self.conc.fc(es1)
        fc2 = float(self.conc.fc(es2))

        if report:
            data["es1"] = es1
            data["es2"] = es2
            data["fs1"] = fs1
            data["fs2"] = fs2
            data["fc1"] = fc1
            data["fc2"] = fc2

        Ps1 = As1 * (fs1 - fc1) if es1 > 0.0 else As1 * fs1
        Ps2 = As2 * (fs2 - fc2) if es2 > 0.0 else As2 * fs2

        P = Pc + Ps1 + Ps2
        M = Mc + Ps1 * x1 + Ps2 * x2

        if report:
            data["P"] = P
            data["M"] = M

        e = xu - self.D / 2 - (M / P)  # With reference to mid-depth of section
        Pu = P
        # Highly compressed edge is interchangeable due to symmetry of As
        Mu = P * abs(e)

        if report:
            data["Pu"] = Pu
            data["Mu"] = Mu

        return Pu, Mu, data

    def design_column_xu(self, Pu: float, Mu: float, ps: float | None = None) -> float:
        def find_e(xu: float, **kwargs) -> float:
            e_reqd = kwargs["e_reqd"]
            Pu_calc, Mu_calc, _ = self.Pu_Mu(xu)
            e_calc = Mu_calc / Pu_calc
            return e_reqd - e_calc

        if ps:
            self.total_As = ps / 100 * self.b * self.D

        e_reqd = Mu / Pu
        xu1 = self.D - self.dc  # NA at the centroid of bars at least compressed edge
        Pu1, Mu1, _ = self.Pu_Mu(xu1)
        e1 = Mu1 / Pu1
        print(
            f"{Pu1 / 1e3:.2f} kN, {Mu1 / 1e6:.2f} kNm, e={e1:.3f} e_reqd={e_reqd:.3f}"
        )
        if e_reqd < e1:  # Increase xu
            xu2 = self.D * 6
        else:  # Decrease xu
            xu2 = xu1
            xu1 = self.dc
        n = int((xu2 - xu1) / 5)
        xu1, xu2 = find_bracket(find_e, xu1, xu2, n, e_reqd=e_reqd)
        print(f"Bracket: {xu1=} {xu2=}")
        # xu_reqd = brent_root(find_e, xu1, xu2, max_iter=30, tol=1e-3, e_reqd=e_reqd)
        xu_reqd = bisection(find_e, xu1, xu2, max_iter=50, tol=1e-3, e_reqd=e_reqd)
        self.xu = xu_reqd
        return xu_reqd

    def design_column_ps(
        self, Pu: float, Mu: float, xu_reqd: float | None = None
    ) -> float:
        def find_ps(ps: float, **kwargs) -> float:
            Pu_target = kwargs["Pu"]
            Mu_target = kwargs["Mu"]

            self.total_As = ps / 100 * self.b * self.D
            Pu_calc, Mu_calc, _ = self.Pu_Mu(self.xu)
            return Pu_target - Pu_calc

        if xu_reqd:
            self.xu = xu_reqd

        Pu_calc, Mu_calc, _ = self.Pu_Mu(self.xu)
        if Pu_calc < Pu:  # ps must be increased
            p1 = self.total_As / (self.b * self.D) * 100
            p2 = 6 / 100 * self.b * self.D
        elif Pu_calc > Pu:  # ps must be decreased
            p1 = 0.25
            p2 = self.total_As / (self.b * self.D) * 100
        else:
            return xu_reqd

        n = int((p2 - p1) / 0.25)
        p1, p2 = find_bracket(find_ps, p1, p2, n, Pu=Pu, Mu=Mu, xu_reqd=xu_reqd)
        print(f"ps Bracket: {p1=} {p2=}")
        ps_reqd = bisection(find_ps, p1, p2, max_iter=50, tol=1e-3, Pu=Pu, Mu=Mu)
        return ps_reqd

    def design_column(self, Pu: float, Mu: float) -> float:
        ps = 2.0
        xu_reqd = self.design_column_xu(Pu, Mu, ps)
        ps_reqd = self.design_column_ps(Pu, Mu, xu_reqd)
        Pu_calc, Mu_calc, _ = self.Pu_Mu(xu_reqd)
        print(
            f"xu={xu_reqd:.2f}, ps={ps_reqd:.2f}, {Pu_calc / 1e3:.2f}, {Mu_calc / 1e6:.2f} e_reqd={Mu / Pu:.2f} e_calc={Mu_calc / Pu_calc:.2f}"
        )
        print(
            f"{Pu / 1e3:.2f}, {Mu / 1e6:.2f}, {(Pu_calc - Pu) / Pu}, {(Mu_calc - Mu) / Mu}"
        )
        while abs(Pu_calc - Pu) / Pu > 1e-2 or abs(Mu_calc - Mu) / Mu > 1e-4:
            print("---")
            xu_reqd = self.design_column_xu(Pu, Mu, ps_reqd)
            ps_reqd = self.design_column_ps(Pu, Mu, xu_reqd)
            Pu_calc, Mu_calc, _ = self.Pu_Mu(xu_reqd)
            print(
                f"xu={xu_reqd:.2f}, ps={ps_reqd:.2f}, {Pu_calc / 1e3:.2f}, {Mu_calc / 1e6:.2f} e_reqd={Mu / Pu:.2f} e_calc={Mu_calc / Pu_calc:.2f}"
            )


if __name__ == "__main__":
    # from pprint import pprint

    M20 = Concrete(20)
    print(f"tau_c={M20.tau_c(0.5):.2f}")
    # x = np.concatenate((np.linspace(0, 0.002, 21), np.linspace(0.0025, 0.0035, 6)))
    # y = np.array([M20.fc(ec) for ec in x])
    # plt.plot(x, y)
    # plt.grid()
    # plt.show()

    # for rebar in RebarType:
    #     print(rebar)

    # MS250 = RebarMS(250)
    # x = np.concatenate(
    #     (
    #         np.linspace(MS250.es_fs[0, 0], MS250.es_fs[1, 0], 6),
    #         np.linspace(MS250.es_fs[1, 0], 2.5 * MS250.es_fs[1, 0], 6),
    #     )
    # )
    # y = np.array([MS250.fs(es) for es in x])

    # plt.plot(x, y)
    # plt.scatter(MS250.es_fs[:, 0], MS250.es_fs[:, 1], marker="x", color="red")
    # plt.grid()
    # plt.show()

    Fe415 = RebarHYSD(415, label="Fe 415")
    Fe500 = RebarHYSD(500, label="Fe 500")

    # x = np.concatenate(
    #     (
    #         Fe415.es_fs[0:2, 0],
    #         np.linspace(Fe415.es_fs[2, 0], Fe415.es_fs[3, 0], 11),
    #         np.linspace(Fe415.es_fs[3, 0], Fe415.es_fs[4, 0], 11),
    #         np.linspace(Fe415.es_fs[4, 0], Fe415.es_fs[5, 0], 11),
    #         np.linspace(Fe415.es_fs[5, 0], Fe415.es_fs[6, 0], 11),
    #         np.array([Fe415.es_fs[6, 0], Fe415.es_fs[6, 0] + 0.01]),
    #     )
    # )
    # y = np.array([Fe415.fs(es) for es in x])

    # plt.plot(x, y)
    # plt.scatter(Fe415.es_fs[:, 0], Fe415.es_fs[:, 1], marker="x", color="red")
    # plt.grid()
    # plt.show()

    # k = 0.3
    # z1 = 0
    # z2 = F(4, 7) * k / 2
    # # z2 = k
    # csb = CSB(k)

    # print(csb.k, csb.alpha_k)
    # print(csb.z_values(z1, z2))
    # print(f"A = {csb.area(z1, z2)}")
    # print(f"M = {csb.moment(z1, z2)}")
    # print(f"x_bar = {csb.centroid(z1, z2)}")

    sec1 = RectBeamSection(230, 450, 25, M20, Fe415, Fe415, Fe415)
    print(sec1)
    print(f"Mu_lim = {sec1.Mulim / 1e6:.2f} kNm")
    print(f"A_st = {sec1.Asc_Ast(105e6)} mm^2")
    print(f"A_st = {sec1.Asc_Ast(140e6)} mm^2")
    print(f"A_st = {sec1.Asc_Ast(90e6)} mm^2")
    Asc, Ast, sv = sec1.design_section(120e6, 90e3)
    print(
        f"Asc={Asc:.2f} mm^2, Ast={Ast:.2f} mm^2, sv={sv:.2f}, pt={Ast * 100 / (sec1.b * sec1.d):.2f}%"
    )
    print(sec1.tau_cmax())
    print(f"tau_c={sec1.tau_c(Ast):.2f}")
    sec2 = RectBeamSection(
        1000, 150, 15, M20, Fe415, Fe415, Fe415, member_type=FlexuralMemberType.SLAB
    )
    print(f"tau_c={sec2.tau_c(Ast):.2f}")
    vstirrups = Stirrups(Fe415, 8, 2)
    istirrups = Stirrups(Fe415, 8, 2, alpha=45)
    bupbars = SeriesBentupBars(Fe415, 16, 2, 45)
    print(f"{vstirrups.Asv:.2f}, {istirrups.Asv:.2f}, {bupbars.Asv:.2f}")
    print(
        f"{vstirrups.sv(100e3, 230, 415)}, {istirrups.sv(100e3, 230, 415)}, {bupbars.sv(100e3, 230, 415)}"
    )
    # tsec = FlangedSection(
    #     230.0, 450.0, 25.0, M20, Fe500, Fe500, Fe415, bf=900, df=150.0
    # )
    # for xu in [125.0, 150.0, 175.0]:
    #     print(f"{xu=} Mu={tsec.Mu(xu) / 1e6:.2f} N mm")

    # tsec = FlangedSection(
    #     230.0, 450.0, 25.0, M20, Fe500, Fe500, Fe415, bf=900, df=150.0
    # )
    # for Mu in [290.0, 340.0, 343.0, 370.0, 380.0, tsec.Mulim / 1e6 + 1]:
    #     xu = tsec.reqd_xu(Mu * 1e6)
    #     if xu:
    #         print(f"xu={xu:.2f}, Mu={tsec.Mu(xu) / 1e6:.2f} kNm")

    # column = RectColumnSection(230, 450, 40, M20, Fe500, 6 * np.pi * 16**2 / 4)
    # MS = RebarMS(250, label="MS 250")
    # column = RectColumnSection(300, 500, 0.1 * 500, M20, MS, 300 * 500 * 4 / 100)
    # print(column)

    # xu1, xu2 = column.design_column(800e3, 75e6)
    # print(f"{xu1=:.2f}, {xu2=:.2f}")
    # Pu1, Mu1 = column.Pu_Mu(xu1)
    # Pu2, Mu2 = column.Pu_Mu(xu2)
    # print(
    #     f"{xu1=}: Pu={Pu1 / 1e3:.2f} kN, Mu={abs(Mu1) / 1e6:.2f} kNm e={Mu1 / Pu1:.2f} mm"
    # )
    # print(
    #     f"{xu2=}: Pu={Pu2 / 1e3 / (column.conc.fk * column.b * column.D):.2f} kN, Mu={abs(Mu2) / 1e6 / (column.conc.fk * column.b * column.D**2):.2f} kNm e={Mu2 / Pu2:.2f} mm"
    # )

    # x = np.arange(column.dc, column.D * 6, 50)
    # x = [3.0, 1.1, 0.9, 0.8, 0.686, 0.478, 0.25]
    # for xu in x:
    #     Pu, Mu, data = column.Pu_Mu(xu * column.D, False)
    #     e = Mu / Pu
    #     print(
    #         f"Ac at xu={xu:.3f}, Pu={Pu / (column.conc.fck * column.b * column.D):.3f}, Mu={Mu / (column.conc.fck * column.b * column.D**2):.3f}, e={e:.3f} mm"
    #     )
    #     if data:
    #         pprint(data)
    # Pu = 1200e3
    # Mu = 100e6
    # column.design_column(Pu, Mu)

    # col2 = RectColumnSection(300, 500, 50, M20, Fe500, 300 * 500 * 4 / 100)
    # col2.design_column(Pu, Mu)
