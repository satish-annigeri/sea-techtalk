import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium", layout_file="layouts/slides.slides.json")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Introduction

    * Python programming language
    * Python for numerical and scientific computation
    * Python for Computer Algebra System
    * Python for working with Microsoft Excel and CSV files
    * Python for generating documents from templates

    ```python
    import numpy as np

    x = np.array([[1, 2, 3], [4, 5,6], [7, 8, 9]])
    print(x)
    ```
    """)
    return


@app.cell
def _(mo):
    def factorial(n):
        return 1 if n == 0 else n * factorial(n - 1)

    mo.show_code(factorial(5))
    return


if __name__ == "__main__":
    app.run()
