import math
from dataclasses import dataclass


@dataclass
class RectFooting:
    Lx: float
    Ly: float
    D: float
    bx: float  # dimension of column along x-axis
    by: float  # dimension of column along y-axis
    P: float  # axial load (Unfactored)
    Mx: float  # moment about x-axis (Unfactored)
    My: float  # moment about y-axis (Unfactored)
    gamma_c: float = 25.0  # unit weight of concrete (kN/m³)

    @property
    def area(self) -> float:
        """Calculate the area of the footing."""
        return self.Lx * self.Ly

    @property
    def volume(self) -> float:
        """Calculate the volume of the footing."""
        return self.area * self.D

    @property
    def weight(self) -> float:
        """Calculate the weight of the footing."""
        return self.volume * self.gamma_c

    @property
    def ex(self) -> float:
        """Calculate the eccentricity about x-axis."""
        return self.My / self.P if self.P != 0 else 0.0

    @property
    def ey(self) -> float:
        """Calculate the eccentricity about y-axis."""
        return self.Mx / self.P if self.P != 0 else 0.0

    @property
    def Sx(self) -> float:
        return self.Lx * self.Ly**2 / 6

    @property
    def Sy(self) -> float:
        return self.Ly * self.Lx**2 / 6

    def pressure_at(self, x: float, y: float) -> float:
        """Calculate the pressure at a given point (x, y) on the footing."""
        if -self.Lx / 2 <= x <= self.Lx / 2 and -self.Ly / 2 <= y <= self.Ly / 2:
            term1 = (self.P + self.weight) / self.area
            term2 = (self.Mx * y) / self.Sx
            term3 = (self.My * x) / self.Sy
            return term1 + term2 + term3
        else:
            raise ValueError("Point (x, y) is outside the footing area.")

    def max_pressure(self) -> float:
        """Calculate the maximum pressure on the footing."""
        corners = [
            (self.Lx / 2, self.Ly / 2),
            (self.Lx / 2, -self.Ly / 2),
            (-self.Lx / 2, self.Ly / 2),
            (-self.Lx / 2, -self.Ly / 2),
        ]
        return max(self.pressure_at(x, y) for x, y in corners)

    def required_area(self, sbc: float, self_wt_factor: float = 10) -> float:
        """Calculate the required footing area based on soil bearing capacity, ignoring eccentricity."""
        total_load = self.P * (1 + self_wt_factor / 100)
        return total_load / sbc


# Example usage:
if __name__ == "__main__":
    footing = RectFooting(
        Lx=3.0, Ly=3.0, D=0.5, bx=0.4, by=0.4, P=1000.0, Mx=20.0, My=15.0
    )

    sbc = 150.0
    required_area = footing.required_area(sbc=sbc)
    print(f"Required Footing Area (ignoring eccentricity): {required_area:.2f} m²")
    reqd_L = math.sqrt(required_area)
    print(f"Side of square footing: {reqd_L:.2f} m")

    Lx = math.ceil(reqd_L / 0.15) * 0.15
    Ly = Lx
    footing.Lx = Lx
    footing.Ly = Ly
    # footing.Mx = 0.0
    # footing.My = 0.0
    print(f"Footing Area: {footing.area:.2f} m²")
    print(f"Footing Volume: {footing.volume:.2f} m³")
    print(f"Footing Weight: {footing.weight:.2f} kN")
    print(f"Eccentricity ex: {footing.ex:.4f} m")
    print(f"Eccentricity ey: {footing.ey:.4f} m")
    max_p = footing.max_pressure()
    print(f"Maximum Pressure: {max_p:.2f} kN/m², SBC={sbc:.2f} kN/m²", end=", ")
    print(f"{'Safe' if max_p <= sbc else 'Unsafe'}")
