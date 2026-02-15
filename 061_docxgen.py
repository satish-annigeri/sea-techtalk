import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Generating Documents from Templates
    """)
    return


@app.cell
def _():
    import marimo as mo

    from datetime import datetime
    from mailmerge import MailMerge
    import pandas as pd

    return MailMerge, datetime, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Templates are files with placeholders for values that will be filled later

    In this demonstration we will use Microsoft Word file as the template. Placeholders are created by **Insert -> Quick Parts -> Fields -> MergeField**. The file `certificate_template.docs` contains the MergeFields🥇
    1. `name`: the name of the person who attended the training program
    2. `trg_prog` the name of the training program
    3. `date`: the date of the training program
    4. `course`: the list of courses completed during the training program

    Below, we read the template file and print a list of names of all the MergeFields.
    """)
    return


@app.cell
def _(MailMerge):
    with MailMerge("certificate_template.docx") as doc:
        print(doc.get_merge_fields())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Input Data to Populate the Templates

    The input data can be read from a Microsoft Excel or CSV file or read from a database. The names of the columns in the data file correspond to the names of the MergeFields above. The template file is read, the MergeFields are replaced by the values corresponding to one attendee and saved as a new Microsoft Word file, one for each attendee. These Microsoft Word files can then be converted to PDF files and possibly emailed to the attendees.
    """)
    return


@app.cell
def _(pd):
    df = pd.read_excel("trg_prog_data.xlsx", sheet_name=0)
    df
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The name and training program details are stored in **Sheet 1** of the training program data file, and the list of courses attended by each attended is stored in **Sheet 2**. The number in the first column of **Sheet 2** corresponds to the `id` field of the attendee in **Sheet 1**.
    """)
    return


@app.cell
def _(pd):
    course_list = pd.read_excel("trg_prog_data.xlsx", sheet_name=1)
    course_list
    return (course_list,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Populating the template

    Each row of **Sheet 1** of the training program data file is processed one at a time. For each attendee, the list of courses attended as a part of the training program is picked from **Sheet 2** of the training program data file.
    """)
    return


@app.cell
def _(MailMerge, course_list, datetime, df):
    for _i in range(len(df)):
        with MailMerge("certificate_template.docx") as docx_tpl:
            _data = df.loc[_i].to_dict()
            _courses = course_list[course_list["id"] == _data["id"]].drop(["id"], axis=1).to_dict(orient="records")
            print(_courses)
            fname = f"{_i+1:02d}_{_data['name'].lower().replace(' ', '_')}.docx"
            print(fname, _data)
            _data["date"] = datetime.strftime(_data["date"], "%d-%m-%Y")
            docx_tpl.merge(**_data)
            docx_tpl.merge_rows("course", _courses)
            docx_tpl.write(fname)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The name of the Word file has the format `nn_name.docx`, with the name of the attendee in lower case and spaces replaced by `_`.

    ## Further Enhancements

    We could further enhance this script in the following ways🥇

    1. The Microsoft Word file can be converted to a PDF file and emailed to the attendee if the email address is known
    2. An HTML or a Markdown file could be used as a template file instead of the Microsoft Word file. These formats are simple text formats and do not need a closed source commercial application such as Microsoft Word.
    3. **Mako** or **Jinja2** template libraries can be used with HTML or Markdown template files to implement conditional processing of parts of the template file.
    """)
    return


if __name__ == "__main__":
    app.run()
