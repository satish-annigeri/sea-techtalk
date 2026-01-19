import marimo

__generated_with = "0.19.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from fractions import Fraction as F
    from dataclasses import dataclass
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import brentq, root_scalar
    return F, brentq, dataclass, mo, np, plt, root_scalar


@app.cell
def _(mo):
    mo.md(r"""
    ## Creating Arrays and Plotting Graphs

    1. `linspace()` creates an array of equally spaced points between two given points
    2. `subplots()` creates the specified number of subplots in the figure
    3. `plot()` plots a line plot of `x` v/s `y` values
    4. `set_xlim()` and `set_ylim()` define the minimum and maximum values of the `x` and `y` axes, respectively
    5. `set_title()` sets the title for all the subplots in the figure
    6. `set_xlabel()` and `set_ylabel()` set the labels on the `x` and `y` axes respectively
    7. `legend()` sets the legend of the subplot
    8. `grid()` draws the grid line
    9. `plt.show()` displays the figure
    """)
    return


@app.cell
def _(np, plt):
    x = np.linspace(0, 4*np.pi, 401)
    y1 = np.sin(x)
    y2 = np.cos(x)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y1)
    ax.plot(x, y2)
    ax.set_xlim(0, 4*np.pi)
    ax.set_ylim(-1.5, 1.5)
    ax.set_title("Harmonic functions")
    ax.set_xlabel("x (radians)")
    ax.set_ylabel("Sine and Cosine")
    ax.legend()
    ax.grid(True, alpha=0.5)

    plt.show()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Solve Linear Simultaneous Equations
    """)
    return


@app.cell
def _(np):
    A = np.array([
        [10.0, 2.5, -1.0], [4.6, 8.2, 1.6], [3.5, -1.6, 5.4]
    ])
    b = np.array([37.2, 10.9, 2.5])
    _x = np.linalg.solve(A, b)
    print(_x)
    print(A @ _x - b)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Find Roots of Polynomials

    The roots of a polynomial such as $a x^3 + b x^2 + c x + d$ can be determine using `numpy.roots([a, b, c, d])` where `a`, `b`, `c` and `d` are the coefficients of the polynomial in decreasing order of the power of `x`.
    """)
    return


@app.cell
def _(np):
    print(np.roots([2.5, -3, -6, 2]))
    return


@app.cell
def _(brentq):
    def f(x: float, a: float, b: float, c: float, d: float) -> float:
        return a * x**3 + b * x**2 + c * x + d

    print(f(0, 2.5, -3, -6, 2), f(1, 2.5,-3, -6, 2))
    print(brentq(f, 0, 1, args=(2.5, -3, -6, 2)))
    print(f(brentq(f, 0, 1, args=(2.5,-3, -6, 2)),  2.5,-3, -6, 2))
    print(brentq(f, 1, 3, args=(2.5, -3, -6, 2)))
    print(f(brentq(f, 1, 3, args=(2.5,-3, -6, 2)),  2.5,-3, -6, 2))
    print(brentq(f, -2, -1, args=(2.5, -3, -6, 2)))
    print(f(brentq(f, -2, -1, args=(2.5,-3, -6, 2)),  2.5,-3, -6, 2))
    return (f,)


@app.cell
def _(f, root_scalar):
    print(root_scalar(f=lambda x: f(x, 2.5,-3, -6, 2), x0=1, method="secant"))
    print(root_scalar(f=lambda x: f(x, 2.5,-3, -6, 2), x0=2, method="secant"))
    print(root_scalar(f=lambda x: f(x, 2.5,-3, -6, 2), x0=-2, method="secant"))
    return


@app.cell
def _(np, plt):
    def stress_conc(ec: float, ecy: float=0.002, ecu: float=0.0035):
        ec_ecy = ec / ecy
        return 2 * ec_ecy - ec_ecy**2 if ec_ecy <= 1 else 1

    _x = np.concat([np.linspace(0, 0.002, 101), np.array([0.0025, 0.003, 0.0035])])
    _y = np.array([stress_conc(_xx) for _xx in _x])

    _fig, _ax = plt.subplots(figsize=(6, 4))
    _ax.plot(_x, _y)
    _ax.grid()
    _ax.set_xlabel("$\epsilon_c$")
    _ax.set_ylabel("$f_c$")
    _ax.set_title("Concrete")

    plt.show()
    return


@app.cell
def _(F):
    def conc_area_p(alpha: float, z1: float, z2: float) -> float:
        return (z2**2 - z1**2) / alpha - (z2**3 - z1**3) / (3 * alpha**2)

    def conc_area_r(z1: float, z2: float) -> float:
        return z2 - z1

    def conc_area(k: float, z1: float, z2: float) -> float:
        if z1 > z2:
            z1, z2 = z2, z1
        alpha = F(4, 7) * k if k <= 1 else k - F(3, 7)
        if k <= 1:
            zmin = 0
        else:
            zmin = k - 1
        zmax = k
        if z1 < zmin and z2 > zmax:
            raise ValueError(f"Unacceptable values of {z1=} and/or {z2=}")

        if z2 <= alpha:  # Entirely parabolic
            Ap = conc_area_p(alpha, z1, z2)
            Ar = 0.0
        elif z1 >= alpha:  # Entirely rectangular
            Ap = 0.0
            Ar = conc_area_r(z1, z2)
        else:  # Partly parabolic and partly rectangulae
            Ap = conc_area_p(alpha, z1, alpha)
            Ar = conc_area_r(alpha, z2)
        return Ap + Ar

    k = 1.0
    print(conc_area(k, 0.0, k * F(4, 7)), 2 / 3 * F(4, 7) * k)
    print(conc_area(k, 0.0, k))
    return


@app.cell
def _(np, plt):
    def stress_MS(es: float, fy: float=250.0, Es: float=2e5) -> float:
        _es = abs(es)
        fsy = 100 / 115 * fy
        esy = fsy / Es
        if _es < esy:
            return es * Es
        else:
            return fsy * np.sign(es)
    _fy = 250.0
    _x = np.array([0.0, 100 / 115 * _fy / 2, 100 / 115 * _fy, 2.5 * 100 / 115 * _fy])
    _y = np.array([stress_MS(_es) for _es in _x])

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_x, _y)
    _ax.grid()
    _ax.set_xlabel("$\epsilon_s$")
    _ax.set_ylabel("$f_s$")
    _ax.set_title("Mild Steel")
    return (stress_MS,)


@app.cell
def _(F, np, plt):
    ep = np.array([
        [0.8, 0.85, 0.9, 0.95, 0.975, 1.0],
        [0.0, 0.0001, 0.0003, 0.0007, 0.001, 0.002]
    ]).T

    def stress_HYSD(es: float, fy: float, Es: float=2e5) -> float:
        _es = abs(es)
        y = ep[:, 0] * 100 / 115 * fy
        x = y / Es + ep[:, 1]
        if _es >= x[-1]:
            return y[-1] * np.sign(es)
        elif _es <= x[0]:
            return es * Es

        i = 1
        while _es >= x[i]:
            i += 1
        slope = (y[i] - y[i-1]) / (x[i] - x[i-1])
        return float(np.sign(es) * (y[i-1] + slope * (_es - x[i-1])))

    _fy = 500.0
    _x = np.concatenate([np.array([0]), ep[:, 0] * F(100, 115) * _fy / 2e5 + ep[:, 1], np.array([1.5, 2.5, 3.5]) * F(100, 115) * _fy / 2e5 + 0.002])
    _y = np.array([stress_HYSD(_es, _fy) for _es in _x])

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_x, _y)
    _ax.grid()
    _ax.set_xlabel("$\epsilon_s$")
    _ax.set_ylabel("$f_s$")
    _ax.set_title("HYSD Steel")
    plt.show()
    return (stress_HYSD,)


@app.cell
def _(F, stress_HYSD, stress_MS):
    def stress_steel(es: float, fy: float=500, rebar_type: str = "HYSD"):
        if rebar_type.upper() == "HYSD":
            return stress_HYSD(es, fy)
        elif rebar_type.upper() == "MS":
            return stress_MS(es, fy)
        else:
            raise ValueError(f"{rebar_type=} must be one of 'MS' or 'HYSD'")

    stress_steel(F(100, 115) * 500 / 2e5 + 0.001, fy=415, rebar_type='hysd')
    return


@app.cell
def _(F, dataclass):
    @dataclass
    class CSB:
        k: float

        @property
        def alpha(self):
            return F(4, 7) * self.k if self.k <= 1 else self.k - F(3, 7)

        def z_limits(self) -> tuple[float, float]:
            if self.k <= 1:
                return 0, self.k
            else:
                return self.k - 1, self.k
            
        def stress(self, z: float) -> float:
            alpha = self.alpha
            z_alpha = z / alpha
            return 2 * z_alpha - z_alpha**2 if z <= alpha else 1
        
        def area_p(self, alpha, z1, z2):
            return (z2**2 - z1**2) / alpha - (z2**3 - z1**3) / (3 * alpha**2)

        def area_r(self, z1, z2):
            return z2 - z1

        def area(self, z1: float, z2: float) -> float:
            if z1 > z2:
                z1, z2 = z2, z1
            zmin, zmax = self.z_limits()
            if z1 < zmin or z2 > zmax:
                raise ValueError(f"Invalide value(s) for {z1=} and/or {z2=}")

            alpha = self.alpha
            if z2 <= alpha:
                Ap = self.area_p(alpha, z1, z2)
                Ar = 0.0
            elif z1 >= alpha:
                Ap = 0.0
                Ar = self.area_r(z1, z2)
            else:
                Ap = self.area_p(alpha, z1, alpha)
                Ar = self.area_r(alpha, z2)
            return Ap + Ar

        def moment_p(self, alpha, z1, z2):
            return 2 * (z2**3 - z1**3) / (3 * alpha) - (z2**4 - z1**4) / (4 * alpha**2)

        def moment_r(self, z1, z2):
            return (z2**2 - z1**2) / 2

        def moment(self, z1: float, z2: float) -> float:
            if z1 > z2:
                z1, z2 = z2, z1
            zmin, zmax = self.z_limits()
            if z1 < zmin or z2 > zmax:
                raise ValueError(f"Invalide value(s) for {z1=} and/or {z2=}")

            alpha = self.alpha
            if z2 <= alpha:
                Mp = self.moment_p(alpha, z1, z2)
                Mr = 0.0
            elif z1 >= alpha:
                Mp = 0.0
                Mr = self.moment_r(z1, z2)
            else:
                Mp = self.moment_p(alpha, z1, alpha)
                Mr = self.moment_r(alpha, z2)
            return Mp + Mr
    return (CSB,)


@app.cell
def _(CSB):
    _csb = CSB(1)
    print(_csb.area(0, 1))
    return


@app.cell
def _(CSB):
    _k = 1.5
    _csb = CSB(_k)
    print(_csb.area(_k-1, _k))
    return


if __name__ == "__main__":
    app.run()
