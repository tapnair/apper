import os
import platform
import subprocess
import sys
from glob import glob
from pathlib import Path

import adsk.core
import adsk.fusion


def install_from_requirements(lib_path: str) -> bool:
    """Installs the dependencies listed in requirementes.txt

    **note**: for now only pulls plain text names

    Returns:
        bool: success
    """
    get_requirements = _search_upward(Path(__file__).parent, "/requirements.txt")
    reqs = _requirements_list(get_requirements)
    if len(reqs) > 0:
        return _run_installer(_requirements_list(get_requirements), lib_path)
    else:
        return True


def install_from_list(reqs: list, lib_path: str) -> bool:
    """Installs all requirements listed in argument

    Args:
        reqs (list<str>): List of dependencies i.e ["numpy", "google"]
        lib_path: path to target installation location
    Returns:
        bool: success
    """
    return _run_installer(reqs, lib_path)


def remove_from_path(lib_path: str):
    """Unloads the path from Fusion Python Path"""
    if lib_path in sys.path:
        sys.path.remove(lib_path)


# ____________________ INTERNAL FUNCTION SECTION ________________________________ #

def _ask_for_permission(deps: list):
    """Creates a dialog that the user agrees to install the dependencies listed

    Args:
        deps (list): list of all dependent packages
        error (boolean): raises error on failure to agree - defaults to True

    Raises:
        RuntimeError: User did not agree to install the packages

    """
    app = adsk.core.Application.get()

    manifest_path = _search_upward(Path(__file__).parent, "/*.manifest")
    # sets name of addin for use by permissions dialog
    name = os.path.basename(manifest_path).split(".")[0]

    res = app.userInterface.messageBox(
        f"{_format_modules_for_message(deps, name)}",
        f"{name} Dependency Installation",
        adsk.core.MessageBoxButtonTypes.YesNoButtonType,
        adsk.core.MessageBoxIconTypes.QuestionIconType,
    )

    if res != adsk.core.DialogResults.DialogYes:
        raise RuntimeError("User Refused to install 3rd party dependencies")


def _sanitize_name(old_name: str) -> str:
    """Sanitized the names for printing and linking just in case

    Args:
        old_name (str): raw name

    Returns:
        str: sanitized string
    """
    old_name = old_name.split("[")[0]
    old_name = old_name.split("==")[0]
    return old_name


def _format_modules_for_message(modules: list, name: str) -> str:
    """To be used internally to format strings into links to be supplied to end user

    Args:
        modules (list<str>): list of dependency names without additional parameters

    Returns:
        str: nicely formatted rich text
    """
    ret = "<html><h1> Addin Dependency Install </h1>\n<hr>"
    ret += f"<font size=5>In order for the {name} addin to function the following dependencies must be installed, if you agree to install the following dependencies they will automatically be fetched and installed</font> \n<ul>"

    for module in modules:
        # just in case (who really knows)
        module_name = _sanitize_name(module)
        ret += f"<li><a href=http://www.pypi.org/project/{module_name}><font size=5>{module}</font></a></li>"

    ret += "</ul>\n"

    ret += "</html>"
    return ret


def _requirements_list(requirements_path: Path) -> list:
    """Reads lines of file and returns

    Args:
        requirements_path (str): Path of file to read from

    Returns:
        list: List of strings
    """
    reqs = []
    with open(requirements_path, "r") as reqFile:
        for line in reqFile.readlines():
            reqs.append(line.strip())
    return reqs


def _search_upward(path_string: Path, flag: str, timeout=7) -> Path:
    """Looks up directories until finding something that matches the path

    Args:
        path_string (Path): Path to look upward at
        flag (str): Filter for matching pattern
        timeout (int, optional): The amount of traversals before failure. Defaults to 7.

    Raises:
        RuntimeError: Can timeout
        RuntimeError: Can not be a valid path

    Returns:
        Path: Path of first object found
    """
    if timeout < 1:
        raise RuntimeError(
            f"Cannot find File matching the filter {flag} in file tree containing fusionPipInstaller"
        )

    new_path = ""

    if path_string.is_dir():
        files = glob(str(path_string) + flag, recursive=False)
        if len(files) > 0:
            new_path = os.path.join(path_string, files[0])
    else:
        raise RuntimeError(f"{path_string} \t - is not a path")

    return new_path if new_path != "" else _search_upward(path_string.parent, flag, timeout - 1)


def _run_installer(items: list, lib_path: str) -> bool:
    """Checks to see if each item is importable, imports if needed

    Args:
        items (list<str>): list of dependencies
    Returns:
        bool: success
    """
    app = adsk.core.Application.get()
    ui = app.userInterface

    if app.isOffLine:
        ui.messageBox(
            "Unable to install dependencies when Fusion is offline. Please connect to the internet and try again!"
        )
        return False

    _ask_for_permission(items)

    progress_bar = ui.createProgressDialog()
    progress_bar.isCancelButtonShown = False
    progress_bar.reset()
    progress_bar.show("Addin", f"Installing dependencies...", 0, 4, 0)
    adsk.doEvents()

    python_folder = _get_python_folder()

    for item in items:
        progress_bar.progressValue += 1
        progress_bar.message = f"Installing {item}..."
        adsk.doEvents()

        _install_module(python_folder, item, lib_path)

    progress_bar.hide()

    return True


def _get_python_folder():
    system = platform.system()

    if system == "Windows":
        python_folder = Path(os.__file__).parents[1]

    elif system == "Darwin":
        python_folder = Path(os.__file__).parents[2] / "bin"
        _check_install_pip(python_folder)

    else:
        raise ImportError(f"Unsupported platform! This add-in only supports windows and macos")

    return python_folder


# fetches pip if it doesn't already exist in the correct directory
def _check_install_pip(python_folder: Path):
    if not os.path.exists(os.path.join(python_folder, "get-pip.py")):
        # fetch the pip installer
        subprocess.run(f'curl https://bootstrap.pypa.io/get-pip.py -o \"{python_folder / "get-pip.py"}\"', shell=True)

        # runs the process to install pip
        subprocess.run(f'\"{python_folder / "python"}\" \"{python_folder / "get-pip.py"}\"', shell=True)


def _install_module(python_folder: Path, mod_name: str, lib_path: str) -> bool:
    """Attempts to fetch pip script and resolve dependencies with less user interaction
    Args:
        python_folder: python executable folder
        mod_name: string name of import
        lib_path: path to target install location
    Returns:
        bool: success
    """
    # This will run ->  pip install --target=./addinPath/site-packages --upgrade pipDep
    if sys.platform == 'darwin':
        subprocess.run(
            f'\"{python_folder / "python"}\" -m pip install --target=\"{lib_path}\" --upgrade {mod_name}',
            shell=True
        )
    else:
        try:
            p = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', f'--target={lib_path}', mod_name],
                # shell=True,
                # check=True,
                # capture_output=True,
                # text=True,
                # timeout=300,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE
            )
            app = adsk.core.Application.get()
            app.userInterface.messageBox("Return Code:  " + str(p.returncode))
            if p.stdout is not None:
                print(f'{p.stdout}')
            if p.stderr is not None:
                print(f'{p.stderr}')
        except subprocess.CalledProcessError as e:
            app = adsk.core.Application.get()
            if e.returncode is not None:
                app.userInterface.messageBox("Return Code:  " + str(e.returncode))
                print("Return Code:  " + str(e.returncode))
            if e.output is not None:
                app.userInterface.messageBox(e.output)
                print(e.output)
            if e.stdout is not None:
                app.userInterface.messageBox(e.stdout)
                print(e.stdout)
            if e.stderr is not None:
                app.userInterface.messageBox(e.stderr)
                print(e.stderr)


    # TODO some validation
    return True
