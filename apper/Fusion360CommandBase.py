import traceback

import adsk.core
import adsk.fusion

import os.path


def _destroy_object(obj_to_be_deleted):
    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface

    if ui and obj_to_be_deleted:
        if obj_to_be_deleted.isValid:
            obj_to_be_deleted.deleteMe()
        else:
            ui.messageBox(obj_to_be_deleted.id + 'is not a valid object')


class Fusion360CommandBase:
    def __init__(self, name, options):

        self.app_name = None
        self.fusion_app = None

        self.cmd_name = name

        self.cmd_description = options.get('cmd_description', 'Default Command Description')
        self.cmd_id = options.get('cmd_id', 'default_cmd_id')

        self.workspace = options.get('workspace', 'FusionSolidEnvironment')
        self.toolbar_panel_id = options.get('toolbar_panel_id', 'SolidScriptsAddinsPanel')
        self.toolbar_tab_id = options.get('toolbar_tab_id', 'ToolsTab')
        self.custom_tab = False

        self.add_to_drop_down = options.get('add_to_drop_down', False)
        self.drop_down_cmd_id = options.get('drop_down_cmd_id', 'Default_DC_CmdId')
        self.drop_down_resources = options.get('drop_down_resources', './resources')
        self.drop_down_name = options.get('drop_down_name', 'Drop Name')

        self.command_in_nav_bar = options.get('command_in_nav_bar', False)

        self.command_visible = options.get('command_visible', True)
        self.command_enabled = options.get('command_enabled', True)
        self.command_promoted = options.get('command_promoted', False)

        self.debug = False

        self.command = None
        self.command_inputs = None
        self.args = None
        self.control = None
        self.command_definition = None
        self.changed_input = None
        self.args = None

        resources_folder = options.get('cmd_resources', 'demo_icons')
        self.cmd_resources = os.path.join('./', 'commands', 'resources', resources_folder)

        # global set of event handlers to keep them referenced for the duration of the command
        self.handlers = []

        # self.fusion_app.commands.append(self)

    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input,
                         input_values):
        pass

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        pass

    def _get_create_event(self):

        return CommandCreatedEventHandler(self)

    # Returns a dictionary for all inputs. Very useful for creating quick Fusion 360 Add-ins
    def get_inputs(self):
        value_types = [adsk.core.BoolValueCommandInput.classType(), adsk.core.DistanceValueCommandInput.classType(),
                       adsk.core.FloatSliderCommandInput.classType(), adsk.core.FloatSpinnerCommandInput.classType(),
                       adsk.core.IntegerSliderCommandInput.classType(),
                       adsk.core.IntegerSpinnerCommandInput.classType(),
                       adsk.core.ValueCommandInput.classType(), adsk.core.SliderCommandInput.classType(),
                       adsk.core.StringValueCommandInput.classType()]

        list_types = [adsk.core.ButtonRowCommandInput.classType(), adsk.core.DropDownCommandInput.classType(),
                      adsk.core.RadioButtonGroupCommandInput.classType()]

        selection_types = [adsk.core.SelectionCommandInput.classType()]

        input_values = {}
        input_values.clear()

        for command_input in [self.command_inputs.item(i) for i in range(0, self.command_inputs.count)]:

            # If the input type is in this list the value of the input is returned
            if command_input.objectType in value_types:
                input_values[command_input.id] = command_input.value
                input_values[command_input.id + '_input'] = command_input

            # TODO need to account for radio and button multi select also
            # If the input type is in this list the name of the selected list item is returned
            elif command_input.objectType in list_types:
                if command_input.objectType == adsk.core.DropDownCommandInput.classType():
                    if command_input.dropDownStyle == adsk.core.DropDownStyles.CheckBoxDropDownStyle:
                        input_values[command_input.id] = command_input.listItems
                        input_values[command_input.id + '_input'] = command_input

                    else:
                        if command_input.selectedItem is not None:
                            input_values[command_input.id] = command_input.selectedItem.name
                            input_values[command_input.id + '_input'] = command_input
                else:
                    if command_input.selectedItem is not None:
                        input_values[command_input.id] = command_input.selectedItem.name
                    else:
                        input_values[command_input.id] = None
                    input_values[command_input.id + '_input'] = command_input

            # If the input type is a selection an array of entities is returned
            elif command_input.objectType in selection_types:
                selections = []
                if command_input.selectionCount > 0:
                    for i in range(0, command_input.selectionCount):
                        selections.append(command_input.selection(i).entity)

                input_values[command_input.id] = selections
                input_values[command_input.id + '_input'] = command_input

            else:
                input_values[command_input.id] = command_input.name
                input_values[command_input.id + '_input'] = command_input

        return input_values

    def on_run(self):

        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            if self.command_in_nav_bar:
                toolbars = ui.toolbars
                nav_bar = toolbars.itemById('NavToolbar')
                controls = nav_bar.controls
            else:
                all_workspaces = ui.workspaces
                this_workspace = all_workspaces.itemById(self.workspace)
                if this_workspace is None:
                    ui.messageBox(self.toolbar_panel_id + 'is not a valid workspace')
                    raise ValueError

                # Add to existing Toolbar Tab or create a new one
                all_toolbar_tabs = this_workspace.toolbarTabs
                toolbar_tab = all_toolbar_tabs.itemById(self.toolbar_tab_id)
                if toolbar_tab is None:
                    toolbar_tab = all_toolbar_tabs.add(self.toolbar_tab_id, self.toolbar_tab_id)
                    toolbar_tab.activate()
                    self.fusion_app.tabs.append(toolbar_tab)

                # Add to existing Toolbar Panel or create a new one
                all_toolbar_panels = toolbar_tab.toolbarPanels
                toolbar_panel = all_toolbar_panels.itemById(self.toolbar_panel_id)
                if toolbar_panel is None:
                    toolbar_panel = all_toolbar_panels.add(self.toolbar_panel_id, self.toolbar_panel_id)

                # Controls for the defined panel
                controls = toolbar_panel.controls

            # If adding to drop down, find or create dropdown in parent
            if self.add_to_drop_down:
                drop_control = controls.itemById(self.drop_down_cmd_id)
                if not drop_control:
                    drop_control = controls.addDropDown(
                        self.drop_down_name,
                        self.drop_down_resources,
                        self.drop_down_cmd_id)
                controls = drop_control.controls

            # Check if control exists (with apper this should never happen)
            self.control = controls.itemById(self.cmd_id)
            if self.control is None:

                # Check if control exists (with apper this should never happen)
                self.command_definition = ui.commandDefinitions.itemById(self.cmd_id)
                if not self.command_definition:

                    # Create the command definition
                    self.command_definition = ui.commandDefinitions.addButtonDefinition(
                        self.cmd_id,
                        self.cmd_name,
                        self.cmd_description,
                        self.cmd_resources
                    )

                # Add command created event handler
                on_command_created_handler = self._get_create_event()
                self.command_definition.commandCreated.add(on_command_created_handler)
                self.handlers.append(on_command_created_handler)

                # Create the new control
                self.control = controls.addCommand(self.command_definition)

                # Set options for control
                self.control.isVisible = self.command_visible
                self.control.isEnabled = self.command_enabled
                self.control.isPromoted = self.command_promoted

        except:
            if ui:
                ui.messageBox('AddIn Start Failed: {}'.format(traceback.format_exc()))

    def on_stop(self):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            parent = self.control.parent
            _destroy_object(self.control)
            _destroy_object(self.command_definition)

            if parent.objectType == adsk.core.DropDownControl.classType():
                if parent.controls.count == 0:
                    drop_control = parent
                    parent = drop_control.parent
                    drop_control.deleteMe()

            if parent.objectType == adsk.core.ToolbarPanel.classType():
                if parent.controls.count == 0:
                    parent.deleteMe()

        except:
            if ui:
                ui.messageBox('AddIn Stop Failed: {}'.format(traceback.format_exc()))


class PreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            command_ = args.firingEvent.sender
            command_inputs = command_.commandInputs
            self.cmd_object_.command_inputs = command_inputs

            if self.cmd_object_.debug:
                ui.messageBox('***Debug *** Preview: {} execute preview event triggered'.
                              format(self.cmd_object.command.parentCommandDefinition.id))
            input_values = self.cmd_object_.get_inputs()
            self.cmd_object_.on_preview(command_, command_inputs, args, input_values)

        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))


class DestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            command_ = args.firingEvent.sender
            command_inputs = command_.commandInputs
            reason_ = args.terminationReason

            if self.cmd_object_.debug:
                ui.messageBox(
                    '***Debug ***Command: {} destroyed'.format(
                        self.cmd_object.command.parentCommandDefinition.id
                    )
                )
                ui.messageBox("***Debug ***Reason for termination= " + str(args.terminationReason))
            input_values = self.cmd_object_.get_inputs()
            self.cmd_object_.on_destroy(command_, command_inputs, reason_, input_values)

        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            command_ = args.firingEvent.sender
            command_inputs = command_.commandInputs
            changed_input = args.input

            if self.cmd_object_.debug:
                ui.messageBox(
                    '***Debug Input: {} changed event triggered'.format(
                        self.cmd_object.command.parentCommandDefinition.id
                    )
                )
                ui.messageBox(
                    '***Debug The Input: {} was the command'.format(self.cmd_object.changed_input.id)
                )

            input_values = self.cmd_object_.get_inputs()

            self.cmd_object_.on_input_changed(command_, command_inputs, changed_input, input_values)

        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        try:
            command_ = args.firingEvent.sender
            command_inputs = command_.commandInputs

            if self.cmd_object_.debug:
                ui.messageBox(
                    '***Debug command: {} executed successfully'.format(
                        self.cmd_object.command.parentCommandDefinition.id
                    )
                )
            input_values = self.cmd_object_.get_inputs()

            self.cmd_object_.on_execute(command_, command_inputs, args, input_values)

        except:
            if ui:
                ui.messageBox('command executed failed: {}'.format(traceback.format_exc()))


class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:

            command_ = args.command
            inputs_ = command_.commandInputs
            self.cmd_object_.command_inputs = inputs_

            on_execute_handler = CommandExecuteHandler(self.cmd_object_)
            command_.execute.add(on_execute_handler)
            self.cmd_object_.handlers.append(on_execute_handler)

            on_input_changed_handler = InputChangedHandler(self.cmd_object_)
            command_.inputChanged.add(on_input_changed_handler)
            self.cmd_object_.handlers.append(on_input_changed_handler)

            on_destroy_handler = DestroyHandler(self.cmd_object_)
            command_.destroy.add(on_destroy_handler)
            self.cmd_object_.handlers.append(on_destroy_handler)

            on_execute_preview_handler = PreviewHandler(self.cmd_object_)
            command_.executePreview.add(on_execute_preview_handler)
            self.cmd_object_.handlers.append(on_execute_preview_handler)

            if self.cmd_object_.debug:
                ui.messageBox('***Debug ***Panel command created successfully')

            self.cmd_object_.on_create(command_, inputs_)

        except:
            if ui:
                ui.messageBox('Command created failed: {}'.format(traceback.format_exc()))

