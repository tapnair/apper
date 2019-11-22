============
Installation
============

The easiest way to get started with apper is to start from a template project.

This will download and structure a new add-in for you on your local system.

You can set some basic parameters and the template will generate everything you need to get started.

Prerequisites
-------------

* Python interpreter
* Install Git
* Adjust your path
* Packaging tools

Python interpreter
^^^^^^^^^^^^^^^^^^

Install Python for your operating system. Fusion 360 uses Python 3.7 so it is recommended to install this version locally as it will simplify setting up your development environment in general.

Consult the official `Python documentation <https://docs.python.org/3/using/index.html>`_ for details.

You can install the Python binaries from `python.org <https://www.python.org/downloads/mac-osx/>`_.


Install Git
^^^^^^^^^^^

Git is a free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency.

You will need to have git installed to properly setup your local environment.  It is recomended to just `install github desktop <https://desktop.github.com/>`_ if you do not already have git installed locally.

Alternatively you can review other `installation options <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.

Adjust your path
^^^^^^^^^^^^^^^^

Ensure that your ``bin`` folder is on your path for your platform. Typically ``~/.local/`` for UNIX and macOS, or ``%APPDATA%\Python`` on Windows. (See the Python documentation for `site.USER_BASE <https://docs.python.org/3/library/site.html#site.USER_BASE>`_ for full details.)


MacOS
"""""

For bash shells, add the following to your ``.bash_profile`` (adjust for other shells):

.. code-block:: bash

    # Add ~/.local/ to PATH
    export PATH=$HOME/.local/bin:$PATH

Remember to load changes with ``source ~/.bash_profile`` or open a new shell session.


Windows
"""""""

Ensure the directory where cookiecutter will be installed is in your environment's ``Path`` in order to make it possible to invoke it from a command prompt. To do so, search for "Environment Variables" on your computer (on Windows 10, it is under ``System Properties`` --> ``Advanced``) and add that directory to the ``Path`` environment variable, using the GUI to edit path segments.

Example segments should look like ``%APPDATA%\Python\Python3x\Scripts``, where you have your version of Python instead of ``Python3x``.

You may need to restart your command prompt session to load the environment variables.

.. seealso:: See `Configuring Python (on Windows) <https://docs.python.org/3/using/windows.html#configuring-python>`_ for full details.



Install cookiecutter
^^^^^^^^^^^^^^^^^^^^

`cookiecutter <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`_ creates projects from project templates and is an amazing resource

For more detailed installation instructions see their `documentation <https://cookiecutter.readthedocs.io/en/latest/installation.html>`_

First install cookie cutter into your local python environment

.. code-block:: bash

    pip install cookiecutter

Or potentially if you have a separate python 3 installation you may need to use:

.. code-block:: bash

    pip3 install cookiecutter

Using the Template
------------------

Navigate to the Fusion 360 Addins directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Putting your addin in the following directory will allow Fusion 360 to automatically recognize it

**Mac:**

.. code-block:: bash

    cd ~
    cd /Library/Application Support/Autodesk/Autodesk\ Fusion\ 360/API/AddIns/

**Windows:**

.. code-block:: bat

    cd  C:\Users\%YOUR_USER_NAME%\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns


Run the cookiecutter template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This will create your add-in directory.

.. code-block:: bash

    cookiecutter https://github.com/tapnair/cookiecutter-fusion360-addin.git

Open your new add-in
^^^^^^^^^^^^^^^^^^^^

In Fusion 360 click on the tools tab and select the **Scripts and Add-ins** command

.. image:: ../_static/addin_dialog.png
   :width: 523
   :alt: Fusion Add-in Dialog

You can now either **Run** your new add-in or select **Edit** to open it in VS Code