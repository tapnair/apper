import importlib
import os
import platform
import subprocess
import sys
from glob import glob
from pathlib import Path

import adsk.fusion


def installFromRequirements() -> bool:
    """Installs the dependencies listed in requirementes.txt

    **note**: for now only pulls plain text names

    Returns:
        bool: success
    """
    getRequirements = __searchUpward(Path(__file__).parent, "/requirements.txt")
    reqs = __getDepList(getRequirements)
    if len(reqs) > 0:
        return __runInstaller(__getDepList(getRequirements))
    else:
        return True


def installFromList(reqs: []) -> bool:
    """Installs all requirements listed in argument

    Args:
        reqs (list<str>): List of dependencies i.e ["numpy", "google"]

    Returns:
        bool: success
    """
    return __runInstaller(reqs)


def unloadLibs(libPath):
    """Unloads the path from Fusion Python Path"""
    if libPath in sys.path:
        sys.path.remove(libPath)


# ____________________ INTERNAL FUNCTION SECTION ________________________________ #


def __runInstaller(reqs: list) -> bool:
    """Internal wrapper for calling the methods to do the install and check

    Args:
        reqs (list<str>): list of all dependencies by name

    Returns:
        bool: success
    """
    # manifestPath = __searchUpward(Path(__file__).parent, "/*.manifest")
    # sets name of addin for use by permissions dialog
    # __addinName = os.path.basename(manifestPath).split(".")[0]

    # This should come after checking
    # if not __askForPermission(reqs, __addinName):
    #    return False
    return __checkImportable(reqs)


def __askForPermission(deps: list, error=False) -> bool:
    """Creates a dialog that the user agrees to install the dependencies listed

    Args:
        deps (list): list of all dependent packages
        error (boolean): raises error on failure to agree - defaults to True

    Raises:
        RuntimeError: User did not agree to install the packages

    Returns:
        bool: success
    """
    app = adsk.core.Application.get()

    manifestPath = __searchUpward(Path(__file__).parent, "/*.manifest")
    # sets name of addin for use by permissions dialog
    name = os.path.basename(manifestPath).split(".")[0]

    res = app.userInterface.messageBox(
        f"{__formatDepsForMessage(deps, name)}",
        f"{name} Dependency Installation",
        3,
        1,
    )

    if res != 2 and error:
        raise RuntimeError("User Refused to install 3rd party dependencies")

    return res == 2


def __sanitizeName(oldName: str) -> str:
    """Sanitized the names for printing and linking just in case

    Args:
        oldName (str): raw name

    Returns:
        str: sanitized string
    """
    oldName = oldName.split("[")[0]
    oldName = oldName.split("==")[0]
    return oldName


def __formatDepsForMessage(deps: list, name: str) -> str:
    """To be used internally to format strings into links to be supplied to end user

    Args:
        deps (list<str>): list of dependency names without additional parameters

    Returns:
        str: nicely formatted rich text
    """
    ret = "<html><h1> Addin Dependency Install </h1>\n<hr>"
    ret += f"<font size=5>In order for the {name} addin to function the following dependencies must be installed, if you agree to install the following dependencies they will automatically be fetched and installed</font> \n<ul>"

    for dep in deps:
        # just in case (who really knows)
        depName = __sanitizeName(dep)
        ret += f"<li><a href=www.pypi.org/project/{depName}><font size=5>{dep}</font></a></li>"

    ret += "</ul>\n"

    ret += "</html>"
    return ret


def __getDepList(reqPath: str) -> list:
    """Reads lines of file and returns

    Args:
        reqPath (str): Path of file to read from

    Returns:
        list: List of strings
    """
    reqs = []
    with open(reqPath, "r") as reqFile:
        for line in reqFile.readlines():
            reqs.append(line.strip())
    return reqs


def __searchUpward(pathStr: Path, flag: str, timeout=7) -> Path:
    """Looks up directories until finding something that matches the path

    Args:
        pathStr (Path): Path to look upward at
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

    newPath = ""

    if pathStr.is_dir():
        files = glob(str(pathStr) + flag, recursive=False)
        if len(files) > 0:
            newPath = os.path.join(pathStr, files[0])
    else:
        raise RuntimeError(f"{pathStr} \t - is not a path")

    return newPath if newPath != "" else __searchUpward(pathStr.parent, flag, timeout - 1)


def __checkDepsLibName(item: str) -> bool:
    """Checks if the current dependency is loaded
    Args:
        item (str): Name of the package to install
    Returns:
        bool: Success
    """
    try:
        item = __sanitizeName(item)
        item_res = importlib.util.find_spec(item)
        if item_res is not None:
            return True
        return False
    # this only happens on windows somehow
    except ModuleNotFoundError:
        return False


def __setupLibsFolder() -> Path:
    # go up until find manifest file
    parentPath = Path(__searchUpward(Path(__file__).parent, "/*.manifest")).parent

    # add pip-lib to manifest file location
    libPath = os.path.join(parentPath, "site-packages")

    # create dir if it doesn't exist
    if not os.path.exists(libPath):
        os.makedirs(libPath)

    # adds pip-lib to path
    if not libPath in sys.path:
        sys.path.insert(1, libPath)

    return libPath


def __checkImportable(items: list) -> bool:
    """Checks to see if each item is importable, imports if needed

    Args:
        items (list<str>): list of dependencies

    Raises:
        RuntimeError: Cannot find or install libarary supplied

    Returns:
        bool: success
    """

    # Just in case
    libPath = __setupLibsFolder()

    asked = False
    for item in items:
        if type(item) is str:
            itemName = __sanitizeName(item)

            if __checkDepsLibName(itemName):
                continue
            else:
                if not asked:
                    if __askForPermission(items):
                        asked = True
                    else:
                        return False

                # If instlal cross encounters an error propogate it up
                if __installCross(item) is False:
                    # Cannot install dependency
                    raise RuntimeError(
                        f"Fusion Pip Installer cannot find or install {item}"
                    )
                else:
                    # checks once more after install now
                    if not __checkDepsLibName(itemName):
                        # soemthing is wrong at this point?
                        return False
    return True


def __installCross(pipDep: str) -> bool:
    """Attempts to fetch pip script and resolve dependencies with less user interaction
    Args:
        pipDep (pipDep): string name of import
    Raises:
        ImportError: Unrecognized Platform
    Returns:
        bool: Success
    Notes:
        Liam originally came up with this style after realizing accessing the python dir was too unreliable.
    """

    app = adsk.core.Application.get()
    ui = app.userInterface

    if app.isOffLine:
        ui.messageBox(
            "Unable to install dependencies when Fusion is offline. Please connect to the internet and try again!"
        )
        return False

    progressBar = ui.createProgressDialog()
    progressBar.isCancelButtonShown = False
    progressBar.reset()
    progressBar.show("Addin", f"Installing dependencies...", 0, 4, 0)

    # this is important to reduce the chance of hang on startup
    adsk.doEvents()

    system = platform.system()

    libPath = __setupLibsFolder()

    if system == "Windows":
        pythonFolder = Path(os.__file__).parents[
            1
        ]  # Assumes the location of the fusion python executable is two folders up from the os lib location

    elif system == "Darwin":  # macos
        pythonFolder = Path(os.__file__).parents[2] / "bin"
        progressBar.message = f"Fetching pip..."
        adsk.doEvents()

        # fetches pip if it doesn't already exist in the correct directory
        if not os.path.exists(os.path.join(pythonFolder, "get-pip.py")):
            # fetch the pip installer
            subprocess.run(
                f"curl https://bootstrap.pypa.io/get-pip.py -o \"{pythonFolder / 'get-pip.py'}\"",
                shell=True,
            )

            # runs the process to install pip
            subprocess.run(
                f"\"{pythonFolder / 'python'}\" \"{pythonFolder / 'get-pip.py'}\"",
                shell=True,
            )
    else:
        raise ImportError(
            f"Unsupported platform! This add-in only supports windows and macos"
        )

    progressBar.progressValue += 1
    progressBar.message = f"Installing {pipDep}..."
    adsk.doEvents()

    # This will run ->  pip install --target=./addinPath/site-packages --upgrade pipDep
    subprocess.run(
        f"\"{pythonFolder / 'python'}\" -m pip install --target={libPath} --upgrade {pipDep}",
        shell=True,
    )

    # this is somehow necessary
    # if system == "Darwin":
    #    pipAntiDeps = ["dataclasses", "typing"]
    #    for depName in pipAntiDeps:
    #        progressBar.message = f"Uninstalling {depName}..."
    #        adsk.doEvents()
    # really should look into re-creating this
    #        subprocess.run(
    #            f"\"{pythonFolder / 'python'}\" -m pip uninstall {depName} -y",
    #            shell=True,
    #        )

    progressBar.hide()

    try:
        # checks just the santized lib name
        return __checkDepsLibName(pipDep)
    except ImportError:
        return False
