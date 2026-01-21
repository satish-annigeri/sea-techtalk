from typing import Callable


def find_bracket(f: Callable, x_start: float, x_end: float, n: int = 10, **kwargs):
    """
    Find x1, x2 that bracket a root of f(x) in [x_start, x_end] by dividing
    the interval into n equal parts and scanning for a sign change.

    Parameters
    ----------
    f : callable
        Function f(x, **kwargs) whose root is sought.
    x_start, x_end : float
        Interval endpoints with x_start < x_end.
    n : int
        Number of equal divisions of the interval.
    **kwargs :
        Additional keyword arguments passed to f.

    Returns
    -------
    (x1, x2) : tuple of floats
        A pair such that f(x1) and f(x2) have opposite signs.
        Returns (None, None) if no such pair is found.
    """

    if n <= 0:
        raise ValueError("n must be a positive integer")

    dx = (x_end - x_start) / n

    x_prev = x_start
    f_prev = f(x_prev, **kwargs)

    if f_prev == 0:
        return x_prev, x_prev

    for i in range(1, n + 1):
        x_curr = x_start + i * dx
        f_curr = f(x_curr, **kwargs)

        if f_prev * f_curr < 0:
            return x_prev, x_curr

        if f_curr == 0:
            return x_curr, x_curr

        x_prev, f_prev = x_curr, f_curr

    raise ValueError(
        f"Error: find_bracket() could not determine brackets between [{x_start}, {x_end}] with {n} intervals"
    )


def brent_root(
    f: Callable, x1: float, x2: float, max_iter: int = 30, tol: float = 1e-12, **kwargs
) -> float:
    """
    Find a root of f(x) in the bracket [x1, x2] using Brent's method.

    Parameters
    ----------
    f : callable
        Function f(x, **kwargs) whose root is sought.
    x1, x2 : float
        Initial bracket such that f(x1) and f(x2) have opposite signs.
    max_iter : int, optional
        Maximum number of iterations (default: 30).
    tol : float, optional
        Convergence tolerance (default: 1e-12).
    **kwargs :
        Additional keyword arguments passed to f.

    Returns
    -------
    float or None
        The root if found, otherwise None.
    """

    f1 = f(x1, **kwargs)
    f2 = f(x2, **kwargs)

    if f1 == 0:
        return x1
    if f2 == 0:
        return x2

    if f1 * f2 > 0:
        # No bracket
        raise ValueError(
            f"Error: bisection() interval {x1} and {x2} does not bracket the roots"
        )

    # Rename variables to match Brent's notation
    a, b = x1, x2
    fa, fb = f1, f2
    c, fc = a, fa
    d = e = b - a

    # print(f"Initial: a={a}, b={b}, fa={fa}, fb={fb}")
    for _ in range(max_iter):
        # print(f"=== {_}")
        if fb == 0:
            return b

        # Ensure |fb| <= |fa|
        if abs(fc) < abs(fb):
            a, b, c = b, c, a
            fa, fb, fc = fb, fc, fa

        tol_act = 2 * tol * max(abs(b), 1.0)
        m = 0.5 * (c - b)
        # print("+++", a, b, c, fa, fb, fc, m, tol_act)

        # Convergence check
        if abs(m) <= tol_act:
            # print("111", m, b)
            return b

        # Decide whether to use interpolation or bisection
        if abs(e) >= tol_act and abs(fa) > abs(fb):
            # Attempt inverse quadratic interpolation or secant
            s = fb / fa
            if a == c:
                # Secant method
                p = 2 * m * s
                q = 1 - s
            else:
                # Inverse quadratic interpolation
                q = fa / fc
                r = fb / fc
                p = s * (2 * m * q * (q - r) - (b - a) * (r - 1))
                q = (q - 1) * (r - 1) * (s - 1)

            if p > 0:
                q = -q
            p = abs(p)

            # Accept interpolation only if it is within the bracket
            if 2 * p < min(3 * m * q - abs(tol_act * q), abs(e * q)):
                e = d
                d = p / q
            else:
                # Fall back to bisection
                d = m
                e = m
        else:
            # Bisection
            d = m
            e = m

        # Move a → b
        a, fa = b, fb

        # Step
        if abs(d) > tol_act:
            b += d
        else:
            b += tol_act if m > 0 else -tol_act

        fb = f(b, **kwargs)

        # Update c if needed
        if (fb > 0 and fc > 0) or (fb < 0 and fc < 0):
            c, fc = a, fa

    # Failed to converge
    raise ValueError(
        f"Error: brent_root() did not converge after {max_iter} iterations"
    )


def bisection(
    f: Callable, x1: float, x2: float, max_iter: int = 30, tol: float = 1e-12, **kwargs
) -> float:
    """
    Find a root of f(x) in the bracket [x1, x2] using the bisection method.

    Parameters
    ----------
    f : callable
        Function f(x, **kwargs) whose root is sought.
    x1, x2 : float
        Initial bracket such that f(x1) and f(x2) have opposite signs.
    max_iter : int, optional
        Maximum number of iterations (default: 30).
    tol : float, optional
        Convergence tolerance (default: 1e-12).
    **kwargs :
        Additional keyword arguments passed to f."""

    f1 = f(x1, **kwargs)
    f2 = f(x2, **kwargs)
    # print(f"Bisection start: x1={x1}, x2={x2}, f1={f1}, f2={f2}")

    if f1 == 0:
        return x1
    if f2 == 0:
        return x2

    if f1 * f2 > 0:
        # No bracket
        raise ValueError(
            f"Error: bisection() interval {x1} and {x2} does not bracket the roots"
        )

    for _ in range(max_iter):
        xm = 0.5 * (x1 + x2)
        fm = f(xm, **kwargs)

        if abs(fm) < tol:
            return xm

        if f1 * fm < 0:
            x2, f2 = xm, fm
        else:
            x1, f1 = xm, fm

    # print("Failed to converge in bisection")
    # Failed to converge
    raise ValueError(f"Error: bisection() did not converge after {max_iter} iterations")


if __name__ == "__main__":

    def f(x: float, **kwargs) -> float:
        return kwargs["a"] * x**2 + kwargs["b"] * x + kwargs["c"]

    print(f(2, a=2, b=-3, c=4))

    x1, x2 = find_bracket(f, -10, 10, 100, a=2, b=-3, c=-4)
    print(x1, x2)
    print(brent_root(f, x1, x2, max_iter=30, tol=1e-12, a=2, b=-3, c=-4))

    print(bisection(f, x1, x2, max_iter=100, tol=1e-12, a=2, b=-3, c=-4))
