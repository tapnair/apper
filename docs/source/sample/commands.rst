========
Commands
========

App Structure
-------------

Once you have executed the cookiecutter template.  You will have the following directory and file structure in your new addin folder.

When running an addin Fusion 360 expects to see a directory with a .py and .manifest file all with the same name.  This is the minimum requirement for your application to be recognized.  You should see these two files with your app name in the new directory.  The manifest file doesn't really require much editing.

::

    ApperSample
    ├── apper
    │   └── ...
    ├── commands
    │   ├── SampleCommand1.py
    │   ├── SampleCommand2.py
    │   ├── SamplePaletteCommand.py
    │   ├── SampleCustomEvent.py
    │   ├── SampleDocumentEvent.py
    │   ├── SampleWorkspaceEvent.py
    │   └── resources
    │       ├── command_icons
    │       │   └── ...
    │       └── palette_icons
    │           └── ...
    ├── ApperSample.py
    ├── ApperSample.manifest
    ├── LICENCE.txt
    └── README.md


Your_App.py (ApperSample in this case) is the main entry point to the app.  Here you will define the commands that will be added and where they will be placed in the ui.

Imports
-------

In this sample the commands and events are defined in a number of files that need to be imported.  Typically I create each command in its own file unless there are two commands that will be sharing much of the same logic, but it doesn't really matter.

.. code-block::

    import traceback

    import adsk.core
    from .apper import apper

    # Basic Fusion 360 Command Base samples
    from .commands.SampleCommand1 import SampleCommand1
    from .commands.SampleCommand2 import SampleCommand2

    # Palette Command Base samples
    from .commands.SamplePaletteCommand import SamplePaletteSendCommand, SamplePaletteShowCommand

    # Various Application event samples
    from .commands.SampleCustomEvent import SampleCustomEvent1
    from .commands.SampleDocumentEvents import SampleDocumentEvent1, SampleDocumentEvent2
    from .commands.SampleWorkspaceEvents import SampleWorkspaceEvent1


Create the App
--------------

To create commands in your addin the first step is to create an instance of :class:`FusionApp <apper.FusionApp>`.

.. code-block::

    my_addin = apper.FusionApp('ApperSample ', "Autodesk ", False)

Standard Commands
-----------------

Commands are created by subclassing :class:`FusionCommandBase <apper.Fusion360CommandBase>` and overriding their *on_xxx* methods.

You add commands to an apper based add-in by calling the :func:`add_command <apper.FusionApp.add_command>` function

    .. autofunction:: apper.FusionApp.FusionApp.add_command

Sample Command 1
^^^^^^^^^^^^^^^^

This is adding the command to a panel called "Commands" on the apps Tab in the solid environment.

**SampleCommand1** is the basic *Hello World* Fusion 360 command.

It adds a button to the UI that, when clicked, will display a message box with some text.

Command Definition
^^^^^^^^^^^^^^^^^^

In the main add-in file we will define the command placement in the UI and define which command the button will be ascociated with.  The .. autofunction:: apper.FusionApp.FusionApp.add_command function takes the name of the command, the command class, and a set of options.

.. code-block::

    my_addin.add_command(
        'Sample Command 1',
        SampleCommand1,
        {
            'cmd_description': 'Hello World!',
            'cmd_id': 'sample_cmd_1',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'Commands',
            'cmd_resources': 'command_icons',
            'command_visible': True,
            'command_promoted': True,
        }
    )

`Learn more about available options by clicking here <usage/options>`_

Command Class
^^^^^^^^^^^^^

This command class is defined in a separate file called **SampleCommand1.py**

You can see we are subclassing the Fusion360CommandBase.  It is not really important to understand the details of this, but if you just follow this format it will be easy to replicate.

Inside your command class definition you will override one or methods :
* :func:`on_create <apper.Fusion360CommandBase.on_create>`
* :func:`on_execute <apper.Fusion360CommandBase.on_execute>`
* :func:`on_preview <apper.Fusion360CommandBase.on_preview>`
* :func:`on_input_changed <apper.Fusion360CommandBase.on_input_changed>`
* :func:`on_destroy <apper.Fusion360CommandBase.on_destroy>`

In this case we are only overriding the :func:`on_execute <apper.Fusion360CommandBase.on_execute>` method.  So when the user clicks the button the code in this function is immediately executed.

.. code-block::

    import adsk.core
    from ..apper import apper
    from ..apper.apper import AppObjects


    class SampleCommand1(apper.Fusion360CommandBase):
        def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
            ao = AppObjects()
            ao.ui.messageBox("Hello World!")

Sample Command 2
^^^^^^^^^^^^^^^^

Now let's look at a little more complete add-in.  In this case we are going to override a number of methods in the :class:`Fusion360CommandBase <apper.Fusion360CommandBase>` class.

on_create
^^^^^^^^^

The :func:`on_create <apper.Fusion360CommandBase.on_create>` function is executed when the user clicks your icon in the Fusion 360 UI.  This is typically where you would define a set of user inputs for your command.  The Fusion 360 API makes creating these user interfaces very easy.  By getting a reference to the CommandInputs of the command, you can simply add items to the interface.  Ass you add items Fusion 360 basically adds them to the bottom of the stack.

.. code-block::

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        # General purpose helper class for quick access to common objects
        ao = AppObjects()

        # Create a default value using a string
        default_value = adsk.core.ValueInput.createByString('1.0 in')

        # Get teh user's current units
        default_units = ao.units_manager.defaultLengthUnits

        # Create a value input.  This will respect units and user defined equation input.
        inputs.addValueInput('value_input_id', '*Sample* Value Input', default_units, default_value)

        # Other Input types
        inputs.addBoolValueInput('bool_input_id', '*Sample* Check Box', True)
        inputs.addStringValueInput('string_input_id', '*Sample* String Value', 'Some Default Value')
        inputs.addSelectionInput('selection_input_id', '*Sample* Selection', 'Select Something')

        # Read Only Text Box
        inputs.addTextBoxCommandInput('text_box_input_id', 'Selection Type: ', 'Nothing Selected', 1, True)

        # Create a Drop Down
        drop_down_input = inputs.addDropDownCommandInput('drop_down_input_id', '*Sample* Drop Down',
                                                         adsk.core.DropDownStyles.TextListDropDownStyle)
        drop_down_items = drop_down_input.listItems
        drop_down_items.add('List_Item_1', True, '')
        drop_down_items.add('List_Item_2', False, '')

on_input_changed
^^^^^^^^^^^^^^^^

The :func:`on_input_changed <apper.Fusion360CommandBase.on_input_changed>` function is executed when the user changes any input value in your ui.  This function is typically used to make adjustments to the user interface itself.  For example you may want to hide or show certain options based on another input such as a checkbox for "advaced options" or something along those lines.  In this case we are updating the text box text with the object type of whatever the user has selected.  Note code in this method will not affect the graphics window.  If you want to update the displayed geometry you should use the :func:`on_preview <apper.Fusion360CommandBase.on_preview>` method.