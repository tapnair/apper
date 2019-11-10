import traceback

import adsk.core
import json

import os
from os.path import expanduser


class FusionApp:
    def __init__(self, name, company, debug):
        self.name = name
        self.company = company
        self.debug = debug
        self.commands = []
        self.custom_events = []
        self.document_events = []
        self.tabs = []
        self.default_dir = self._get_default_dir()
        self.preferences = self.get_preferences()

    def add_command(self, name, command_class, options):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            _cmd_id = options.get('cmd_id', 'default_id')
            options['cmd_id'] = self.company + "_" + self.name + "_" + _cmd_id

            options['app_name'] = self.name
            options['fusion_app'] = self
            options['debug'] = self.debug

            command = command_class(name, options)
            self.commands.append(command)

        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))


    def check_for_updates(self):
        pass

    def run_app(self):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        try:
            for run_command in self.commands:
                run_command.on_run()
        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))

    def stop_app(self):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            for stop_command in self.commands:
                stop_command.on_stop()

            for toolbar_tab in self.tabs:
                if toolbar_tab.isValid:
                    toolbar_tab.deleteMe()

            for event in self.custom_events:
                event.on_stop()

            for event in self.document_events:
                event.on_stop()

        except:
            if ui:
                ui.messageBox('Input changed event failed: {}'.format(traceback.format_exc()))

    # Get default directory
    def _get_default_dir(self):

        # Get user's home directory
        default_dir = expanduser("~")

        # Create a subdirectory for this application settings
        default_dir = os.path.join(default_dir, self.name, "")

        # Create the folder if it does not exist
        if not os.path.exists(default_dir):
            os.makedirs(default_dir)

        return default_dir

    def get_preferences(self):
        file_name = os.path.join(self.default_dir, ".preferences.json")

        if os.path.exists(file_name):
            with open(file_name) as f:
                try:
                    preferences = json.load(f)
                except:
                    preferences = {}
        else:
            preferences = {}

        return preferences

    def save_preferences(self, preferences):

        preferences_text = json.dumps(preferences)

        file_name = os.path.join(self.default_dir, ".preferences.json")
        with open(file_name, "w") as f:
            f.write(preferences_text)


