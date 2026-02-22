# README

This repository contains the material that was presented at the Structural Engineers' Association Tech Talk titled "Python for Structural Engineers" on February 20, 2026.

# LICENSE
The software and documentation in this repository is licensed under the MIT License.

# USING THIS REPOSITORY

## Tools you will need
The Python code in this repository is in the form of marimo notebooks. A merimo notebook runs in a web browser and can contain code cells or Markdown cells. The code in the code cells can be executed, and marimo being a reactive notebook, executing code in a cell will **automatically** execute code in all other cells that depend on the variable in the cell irrespective of their physicallocation within the notebook. This is similar to the automatic recalculations in Microsoft Excel when you change the value in one cell.

To work with notebooks in this repository, you will need the following tools:

1. `git` to clone this repository to your own local repository on your own machine
2. `uv` to manage your Python projects, which includes installing Python, creating a new local repository or working with a cloned repository, installing and updating Python packages from PyPI, the Python packages repository on the Internet

You can work in Microsoft Windows, GNU/Linux or macOS. You must be ready to open the Command Prompt on Microsoft Windows. People working on GNU/Linux or macOS must work in the terminal but most users on those platforms are familiar with this.


## Installing `git`

You can `git` in the following ways, depending on your platform:
1. Microsoft Windows: Download from [here](https://gitforwindows.org/) and install
2. Debian, Ubuntu GNU/Linux: Use the `apt` package manager
3. Other GNU/Linux distributions: The package manager for your distribution will have `git` in the repository
4. macOS: Use `brew`

After installing, verify it is installed and accessible from your Command Prompt or terminal:
```bash
> git --version
```
If installed corretly, you must see `git version n.nn.n` where `n.nn.n` is the version of `git` installed on your machine.

To see help on using `git`, type
```bash
> git --help
```
This will display all the commands available and their brief explanation.For more information, visit the [documentation](https://git-scm.com/docs) for `git`.

## Installing `uv`

If you are using Microsoft Windows 11, note that the command to download and install `uv` following the instructions from the [Astral documentation](https://docs.astral.sh/uv/)  must be typed in the Windows PowerShell. Open Windows PowerShell by pressing the `Windows` key on your keyboard and typing `powershell` in the search bar until you see it listed, and then clicking on it.

```bash
PS> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
If you are using GNU/Linux or macOS, open the `bash` terminal and type the following command.

```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```
or 
```bash
$ wget -qO- https://astral.sh/uv/install.sh | sh
```
This will install the latest version of `uv` on your machine.

Once installed, you can upgrade `uv` to the latest verion with the command
```bash
> uv self update
```
Since `uv` is currently in early stages of its deevlopment, check for a new version frequently, say, every week.

Use `uv` from the Microsoft Windows Command Prompt or the terminal on GNU/Linux or macOS. You may have to close and open the terminal after installing `uv` for the change in the `PATH` environment variable to take effect.

To get help on using `uv` use the following command:

```bash
> uv --help
> uv -V
```

## Cloning this repository

You must have `git` installed on your system to clone this GitHub repository. You can download and install git for Microsoft Windows from [Git home page](https://gitforwindows.org/). On GNU/Linux or macOS, use the package management tool to install `git`.


With `git` installed you can clone this reporsitory to your current working directory. This requires that you are connected to the Internet.

```bash
> git clone https://github.com/satish-annigeri/sea-techtalk.git
```
This will create a folder named `sea-techtalk` in your current working directory.

Alternately, visit the url `https://github.com/satish-annigeri/sea-techtalk` in your web browser and click the green coloured button `Code` and from the dropdown ment click on `Download ZIP`. This will download the contents of the github repository as a ZIP file which you can the unzip into your preferred folder using a tool such `WinZip` of `7-zip` or the Windows File Explorer.

You can explore the cloned local repository with the command
```bash
> git status
> git log
```

## Setting up your Python environment
Open the Windows Command Prompt or the GNU/Linux or macOS terminal to use `uv`. Open the Windows Command Prompt in one of the following ways:

1. Press the `Windows` key on your keyboard and type `cmd` and click on Command Prompt to open the Windows Command Prompt window. Then navigate to the folder where you cloned the GitHub repository.
2. Open Windows File Explorer and navigate to the folder where you cloned the GitHub erpository. Click inside the address bar at the top of Windows File Explorer (where the path to the folder is displayed) and type the command `cmd` and press `Enter`. This opens the Windows Command prompt with the selected folder as the current working directory.

If you are using GNU/Linux or macOS, open the `bash` terminal.

Use `uv` to create your Python virtual environment with the following commands at the Command Prompt or terminal
```bash
> uv sync
> uv run python -V
> uv pip list
```
The first command downloads and installs the required version of Python from the Internet if necessary, the second displays the version of Python installed in your virtual environment and the third lists all the packages installed in your virtual environment.

#### Creating a fresh Python project

If you are starting a new project of your own instead of cloning an existing GitHub repository, you can set up a virtual environment for your project as follows:

1. Create a folder at a chosen location on your file system, giving it a suitable name. You can do this with Windows File Explorer in Windows 11 or in a `bash` terminal in GNU/Linux or macOS.
2. Open Windows Command Prompt and change into the folder created for the project with the `cd` command.
3. Initialize the project. This creates the `.python-version` file
4. Add the packages required by your project. This will add the names of the packages to the `pyproject.toml` file

The sequence of commands to be typed at the command prompt in both Windows 11 Command Prompt as well the GNU/Linux and macOS terminal are shown below:

```bash
> uv init
> uv add numpy
```
The first command initializes the project and the second command installs the Python package `numpy` to the project and updates `pyproject.toml` file to erflect this change.

## Using marimo

marimo is a browser based coding and documentation system. It can be used in the place of an IDE for small programs or to demonstrate your code to others while it is not ideal for large code bases. However, it enables building interactive web GUIs as a front end to large code bases.


A marimo notebook opens in your default web browser. If you wish, you can copy paste the code from the Command Prompt or the terminal into your favourite web browser.

A marimo notebook consists of cells, which can be:
1. A **code cell* which can contain Python code that can be executed
2. A ** Markdown cell** which can contain text written in [Markdown](https://www.markdownguide.org/) syntax. Markdown is simple to learn and can render mathematical expression using a subset of the LaTeX markup language.

marimo notebook cells are reactive, that is, when the value of a variable changes, it automatically updates all cells which depend on thchanged value.

You can open a marimo notebook in the **edit** mode if you wish to view the code. If you opena marimo notebook in **run** mode, you cannot view the code but you can see the output generated by the code. Here is how you can open a notebook named `demo.py` in **edit** and **run** mode with the following commands when using `uv`:
```bash
> uv run -- marimo edit demo.py
> uv run -- marimo run demo.py
```

## VS Code code editor
Python scripts (Python programs are called scripts), can be created in any text editor of your choice, such as Notepad on Windows or Vim on GNU/Linux on macOS. The current popular code editor is Microsoft VS Code. You can download and install VS Code for your machine and Operating System from [VS Code web page](https://code.visualstudio.com/download).

VS Code is a general purpose code editor and works for many programming languages. To work with Python, it is best to install VS Code Extensions that make this easy. This is done by clicking on the Extensions icon on the left vertical toolbar, searching for the required extension in the search bar, clicking on the name of the extension and clicking **Install** on the window to the right. Install the following Extensions:

1. Python extension from Microsoft
2. Ruff extension from Astral Software

You have now created a Python project with a virtual environment and are ready to run the scripts.

## Executing the scripts

Navigate to the cloned directory and type the command to execute any of the Python scripts from the Windows Command Prompt or the bash terminal. Most scripts in the repository are Marimo Notebooks.

Following command executes the script named `01_num_plt.py`:
```bash
> uv run -- marimo edit 01_np_plt.py
```
This runs the Marimo app within your default web browser in the **edit** mode. A Marimo app consists of cells that may contain Python code or Markdown text. To execute Python code in any of the cells, either press the run button to the bottom left of the cell or click the mouse anywhere within the cell and press `Ctrl+Enter` keys.

You can view the Marimo notebooks in the **run** mode where you can see only the output generated by the Notebook, but not the code that generates it.

```bash
> uv run -- marimo run 01_np_plt.py
```

If VS Code is open, you can open a terminal window within VS Code by pressing the key combination `` Ctrl+` `` where `` ` `` is the backquote character (usually to the left of the numeric key `1` on the first row of the keyboard, along with the `~` character). You can then type the above command within the terminal window.

