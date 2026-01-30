import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""
    # Manipulate PDF documents using PyMuPDF package

    ## Import required packages
    """)
    return


@app.cell
def _():
    import marimo as mo

    import io
    import fitz
    import tabula
    from PIL import Image, ImageOps
    return Image, ImageOps, fitz, io, mo, tabula


@app.cell
def _(mo):
    mo.md(r"""
    ## Print document information
    """)
    return


@app.cell
def _(fitz):
    print(fitz.__doc__)
    fname = "sea_expenses.pdf"
    _doc = fitz.open(fname)
    print(f"Document: {fname} Number of pages: {_doc.page_count}")
    print(_doc.metadata)
    return (fname,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Display a page of a PDF document as a scaled image

    1. Open a document file
    2. Load a page with specified page number (First page is counted as page 0)
    3. Get a pixel map of the page to a specified scale, using a scaling matrix
    4. Convert the pixel map to an image in a specified format, PNG in the following example
    5. Display the image
    """)
    return


@app.cell
def _(Image, ImageOps, fitz, fname, io):
    _scale = 0.5
    _mat = fitz.Matrix(_scale, _scale)

    _doc = fitz.open(fname)
    _page1 = _doc.load_page(1)
    _pix1 = _page1.get_pixmap(matrix=_mat)
    _img1 = Image.open(io.BytesIO(_pix1.tobytes("png")))
    _img1 = ImageOps.expand(_img1, border=1, fill="blue")
    _img1
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Convert all tables in an entire document into a CSV file
    """)
    return


@app.cell
def _(fname, tabula):
    tabula.convert_into(fname, "output.csv", output_format="csv", pages="all")
    return


@app.cell
def _(fname, tabula):
    _tables = tabula.read_pdf(fname, pages="all", multiple_tables=True)
    _tables
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Add header and footer to each page

    1. Define a static/dynamic header
    2. Define a static/dynamic footer
    3. Open the file as a document
    4. Loop over each page of the document
    5. Insert the header and footer text into each page
    6. Save the document with a different name
    7. Save the file
    """)
    return


@app.cell
def _(fitz, fname):
    _doc = fitz.open(fname)
    _header = "Design Basis Report"
    _footer = "Page %i of %i"
    for _page in _doc:
        _page.insert_text((45, 30), _header)
        _page.insert_text(  # insert footer 50 points above page bottom
            (45, _page.rect.height - 50),
            _footer % (_page.number + 1, _doc.page_count),
        )
    _doc.save("output_hf.pdf")
    _doc.close()
    return


if __name__ == "__main__":
    app.run()
