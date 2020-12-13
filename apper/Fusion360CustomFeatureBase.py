"""
Fusion360CustomFeatureBase.py
=============================
Python module for creating a Fusion 360 Custom Feature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 by Patrick Rainsberry.
:license: Apache 2.0, see LICENSE for more details.
"""
import traceback

import adsk.core
import adsk.fusion

import os.path


handlers = []

class Fusion360CustomFeatureBase:
    """The Fusion360CommandBase class wraps the common tasks used when creating a Fusion 360 Command.

        To create a new command create a new subclass of  Fusion360CommandBase
        Then override the methods and add functionality as required

        Args:
            name: The name of the command
            options: A dictionary of options for the command placement in the ui.  (TODO - Add docs for this)
        """
    def __init__(self, name: str, options: dict):
        self.app_name = options.get('app_name')
        self.fusion_app = options.get('fusion_app', None)

        self.feature_name = name
        self.feature_id = options.get('feature_id', 'default_feature_id')
        self.feature_edit_id = options.get('edit_cmd_id', 'demo_edit_cmd_id')
        self.roll_timeline = options.get('roll_timeline', False)
        icon_folder = options.get('feature_icons', 'demo_icons')
        self.resource_path = os.path.join('commands', 'resources', icon_folder)

        # Register CustomFeatureDefinition and attach event handlers.
        definition = adsk.fusion.CustomFeatureDefinition.create(self.feature_id, self.feature_name, self.resource_path)
        definition.isRollTimeline = self.roll_timeline
        definition.defaultName = self.feature_name
        # self.feature_edit_id = self.fusion_app.command_id_from_name('offset_b_box_edit')

        self.definition = definition

    def on_compute(self, args: adsk.fusion.CustomFeatureEventArgs):
        pass

    def on_edit(self, args: adsk.fusion.CustomFeatureEventArgs):
        pass

    def on_run(self):

        self.definition.editCommandId = self.fusion_app.command_id_from_name(self.feature_edit_id)

        compute_event = self.definition.customFeatureCompute
        on_compute_handler = _CustomFeatureComputeHandler(self)
        compute_event.add(on_compute_handler)
        handlers.append(on_compute_handler)

        # edit_event = definition.customFeatureCompute
        # on_edit_handler = _CustomFeatureEditHandler(self)
        # edit_event.add(on_edit_handler)

    def on_stop(self):
        # TODO this
        pass


class _CustomFeatureComputeHandler(adsk.fusion.CustomFeatureEventHandler):
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args: adsk.fusion.CustomFeatureEventArgs):
        try:
            # command_ = args.firingEvent.sender
            # command_inputs = command_.commandInputs
            #
            # input_values = self.cmd_object_.get_inputs()
            self.cmd_object_.on_compute(args)

        except:
            app = adsk.core.Application.cast(adsk.core.Application.get())
            ui = app.userInterface
            ui.messageBox('command executed failed: {}'.format(traceback.format_exc()))


class _CustomFeatureEditHandler(adsk.fusion.CustomFeatureEventHandler):
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args: adsk.fusion.CustomFeatureEventArgs):
        try:
            # command_ = args.firingEvent.sender
            # command_inputs = command_.commandInputs
            #
            # input_values = self.cmd_object_.get_inputs()
            self.cmd_object_.on_edit(args)

        except:
            app = adsk.core.Application.cast(adsk.core.Application.get())
            ui = app.userInterface
            ui.messageBox('command executed failed: {}'.format(traceback.format_exc()))
