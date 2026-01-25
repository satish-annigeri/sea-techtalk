# README

This repository contains the material to be presented at the Structural Engineers' Association Tech Talk titled "Python for STructural Engineers" in February 2026.

## Cloning this repository

If you have `git` installed and you know how to use `git`, clone this reporsitory to your machine to your current working directory

```bash
>git clone https://github.com/satish-annigeri/sea-techtalk.git
```
This will create a folder named `sea-techtalk` in your current working directory.

Alternately, visit the url `https://github.com/satish-annigeri/sea-techtalk` in your web browser and click the green coloured button `Code` and from the dropdown ment click on `Download ZIP`. This will download the contents of the github repository as a ZIP file which you can the unzip into your preferred folder using a tool such `WinZip` of `7-zip` or the Windows File Explorer.

## Setting up your Python environment

My current preferred way of managing Python projects is with the Astral `uv`. Here are the steps I recommend:

1. Install `uv`
2. Change into the folder where you cloned or unzipped the contents of the `sea-techtalk` github repository
3. Use `uv` to list the available versions of Python and install the one you prefer. Usually it is preferable to install the latest version available.
4. Download and install the packages required to run the Python scripts and/or apps in the repository

## Installing `uv`

If you are using Microsoft Windows 11, note that the command to download and install `uv` from the Astral website must be typed in the Windows PowerShell. To open Windows PowerShell, press the `Windows` key on your keyboard and type `powershell` and you can see it listed, when you can click on it to open the PowerShell window.

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

## Install Python
To use `uv` on Windows, you will have to open the Windows Command Prompt. To do this, you can press the `Windows` key on your keyboard and type `cmd` and click on Command Prompt to open the Windows Command Prompt window.

If you are using GNU/Linux or macOS, open the `bash` terminal.

Check the version of `uv` and list the available versions of Python for your machine with the following commands:
```bash
> uv -V
> uv python list
```
This versions of Python shown in blue are already installed on your machine and the versions available are indicated with `<download available>`.

Install version 3.14 of Python for your machine with the following command:
```bash
> uv python install 3.14
> uv python list
```
Confirm that the requested version of Python is installed.

## Create a virtual environment and install required packages
It is standard practice to create a separate virtual environment for each Python project you work on. A virtual environment, usually referred to an `venv`, is created within the folder where your Python code resides. 

### Within the cloned repository
The commands described below must be typed at the Windows Command prompt if you are in Windows 11 or the `bash` terminal if you are in GNU/Linux or macOS.

In Windows 11, you can do this by selecting the folder, clicking in the address bar at the top of Windows File Explorer (where the path to the folder is displayed) and typing the command `cmd` and pressing enter. This opens the Windows Command prompt with the selected folder as the current working directory.

In GNU/Linux or macOS, open the `bash` terminal and use the `cd` command to navigate to the cloned repository.

```bash
> uv init
> uv sync
```
This will initialize the project (it creates the `.python-version` file in your folder) and set the latest version of Python installed on your machine as the required version of Python. The second command creates the `.venv` folder in your project folder and use the `pyproject.toml` in the cloned repository to download install the required Python packages from the PyPI Python repository. This will require that your machine be connected to the Internet.

### Within your own new Python project folder

If you are starting a new project of your own, you can do as follows:

1. Create a folder at a chosen location on your file system, giving it a suitable name. You can do this with Windows File Explorer in Windows 11 or in a `bash` terminal in GNU/Linux or macOS.
2. Change into that folder created for the project with the `cd` command.
3. Initialize the project. This creates the `.python-version` file
4. Add the packages required by your project. This will create the `pyproject.toml` file and list the added packages to it

The sequence of commands to be typed at the command prompt in both Windows 11 Command Prompt as well the GNU/Linux and macOS terminal are shown below:

```bash
> uv init
> uv add numpy
```
The second command above installs the Python package `numpy` to your virtual environment and list it in the `pyproject.toml` file.

## VS Code code editor
Python scripts (Python programs are called scripts), can be created in any text editor of your choice, such as Notepad on Windows or Vim on GNU/Linux oe macOS. The current popular code editor is Microsoft VS Code. You can download and install VS Code for your machine and Operating System from https://code.visualstudio.com/download.

VS Code is a general purpose code editor that works for many programming languages. To work with Python, it is best to install VS Code Extensions that make this easy. This is done by clicking on the Extensions icon on the left vertical toolbar, searching for the required extension in the search bar, clicking on the name of the extension and clicking **Install** on the window to the right. Install the following Extensions:

1. Python extension from Microsoft
2. Ruff extension from Astral Software

You are now created a Python project with a virtual environment and are ready to run the scripts.