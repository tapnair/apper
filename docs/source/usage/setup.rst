Getting Started
===============

The easiest way to get started with apper is to start from a template project.

This will download and structure a new add-in for you on your local system.

You can set some basic parameters and the template will generate everything you need to get started.

Install cookiecutter
--------------------

`cookiecutter <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`_ creates projects from project templates and is an amazing resource

For more detailed installation instructions see their `documentation <https://cookiecutter.readthedocs.io/en/latest/installation.html>`_

First install cookie cutter into your local python environment

>>> pip install cookiecutter

Or potentially if you have a separate python 3 installation you may need to use:

>>> pip3 install cookiecutter

Navigate to the Fusion 360 Addins directory
-------------------------------------------

Putting your addin in the following directory will allow Fusion 360 to automatically recognize it

**Mac:**

>>> cd ~
>>> cd /Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/

**Windows:**

>>> cd  TODO

Run the cookiecutter template
------------------------------

This will create your addin directory.

>>> cookiecutter cookiecutter https://github.com/tapnair/cookiecutter-fusion360-addin.git

Open your new add-in
---------------------

In Fusion 360 click on the tools tab and select the **Scripts and Add-ins** command

.. image:: ../_static/addin_dialog.png
   :width: 523
   :alt: Fusion Add-in Dialog

You can now either **Run** your new add-in or select **Edit** to open it in VS Code