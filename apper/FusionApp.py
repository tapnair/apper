"""
FusionApp.py
============
Python module for creating a Fusion 360 Addin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 by Patrick Rainsberry.
:license: Apache 2.0, see LICENSE for more details.

"""
import logging
import traceback

import adsk.core
import json

import os
from os.path import expanduser

from typing import Optional, List, Union, Any, Iterable


class FusionApp:
    """Base class for creating a Fusion 360 Add-in

    Args:
        name: The name of the addin
        company: the name of your company or organization
        debug: set this flag as True to enable more interactive feedback when developing.
    """

    def __init__(self, name: str, company: str, debug: bool):
        self.name = name
        self.company = company
        self.debug = debug
        self.commands = []
        self.events = []
        self.features = []
        self.tabs = []
        self.default_dir = self._get_default_dir()
        self.preferences = self.get_all_preferences()
        self.root_path = ''
        self.command_dict = {}
        self.custom_toolbar_tab = True
        self.logger: Optional[logging.Logger] = None
        self.logging_enabled = False

    def add_command(
            self,
            name: str,
            command_class: Any,
            options: dict
    ):
        """Adds a command to the application

        Args:
            name: The name of the command
            command_class: This should be your subclass of apper.Fusion360CommandBase or apper.PaletteCommandBase
            options: Set of options for the command see the full set of `options <usage/options>`_
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            base_cmd_id = options.get('cmd_id', 'default_id')
            new_id = self.company + "_" + self.name + "_" + base_cmd_id
            options['cmd_id'] = new_id

            options['app_name'] = self.name
            options['fusion_app'] = self

            tab_id = options.get('toolbar_tab_id', None)
            tab_name = options.get('toolbar_tab_name', None)

            if tab_name is None:
                options['toolbar_tab_name'] = self.name

            if tab_id is None:
                options['toolbar_tab_id'] = self.name
            else:
                if ui.allToolbarTabs.itemById(tab_id) is not None:
                    self.custom_toolbar_tab = False

            _workspace = options.get('workspace', 'FusionSolidEnvironment')

            if isinstance(_workspace, str):
                if self.custom_toolbar_tab:
                    _this_tab_id = options['toolbar_tab_id'] + '_' + _workspace
                    options['toolbar_tab_id'] = _this_tab_id

                command = command_class(name, options)

                self.commands.append(command)
                self.command_dict[base_cmd_id] = new_id

            elif isinstance(_workspace, Iterable):
                if all(isinstance(item, str) for item in _workspace):
                    for workspace in _workspace:
                        options['workspace'] = workspace

                        _this_id = new_id + '_' + workspace
                        options['cmd_ctrl_id'] = _this_id

                        _this_tab_id = options['toolbar_tab_id'] + '_' + workspace
                        options['toolbar_tab_id'] = _this_tab_id

                        command = command_class(name, options)
                        self.commands.append(command)
                        self.command_dict[base_cmd_id] = new_id
            else:
                raise TypeError  # TODO or something along that line

        except:
            if ui:
                ui.messageBox('Apper Add Command failed: {}'.format(traceback.format_exc()))

    def command_id_from_name(self, name: str) -> Optional[str]:
        """Returns the full cmd_id defined by apper

        Args:
            name: this is the value set in options for cmd_id

        Returns:
            The full cmd_id (i.e. CompanyName_AppName_cmd_id)
        """
        cmd_id = self.command_dict.get(name)
        return cmd_id

    def add_document_event(self, event_id: str, event_type: adsk.core.DocumentEvent, event_class: Any):
        """Register a document event that can respond to various document actions

        Args:
            event_id: A unique identifier for the event
            event_type: Any document event in the current application
            event_class: Your subclass of apper.Fusion360DocumentEvent
        """
        doc_event = event_class(event_id, event_type)
        doc_event.fusion_app = self
        self.events.append(doc_event)

    def add_custom_event(self, event_id: str, event_class: Any, auto_start: bool = True):
        """Register a custom event to respond to a function running in a new thread

        Args:
            event_id: A unique identifier for the event
            event_class: Your subclass of apper.Fusion360CustomThread
            auto_start: Whether the thread should start when the addin starts
        """

        custom_event = event_class(event_id, auto_start)
        custom_event.fusion_app = self
        self.events.append(custom_event)

    def add_custom_event_no_thread(self, event_id: str, event_class: Any):
        """Register a custom event

        Args:
            event_id: A unique identifier for the event
            event_class: Your subclass of apper.Fusion360CustomThread
        """

        custom_event = event_class(event_id)
        custom_event.fusion_app = self
        self.events.append(custom_event)

    def add_workspace_event(self, event_id: str, workspace_name: str, event_class: Any):
        """Register a workspace event that can respond to various workspace actions

        Args:
            event_id: A unique identifier for the event
            workspace_name: name of the workspace (i.e.
            event_class: Your subclass of apper.Fusion360WorkspaceEvent
        """
        workspace_event = event_class(event_id, workspace_name)
        workspace_event.fusion_app = self
        self.events.append(workspace_event)

    def add_command_event(self, event_id: str, event_type: Any, event_class: Any):
        """Register a workspace event that can respond to various workspace actions

        Args:
            event_id: A unique identifier for the event
            event_type: One of [UserInterface.commandCreated, UserInterface.commandStarting, UserInterface.commandTerminated]
            event_class: Your subclass of apper.Fusion360CommandEvent class
        """
        command_event = event_class(event_id, event_type)
        command_event.fusion_app = self
        self.events.append(command_event)

    def add_web_request_event(self, event_id: str, event_type: adsk.core.WebRequestEvent, event_class: Any):
        """Register a workspace event that can respond to various workspace actions

        Args:
            event_id: A unique identifier for the event
            event_class: Your subclass of apper.Fusion360WebRequestEvent
            event_type: Opened or Inserting from URL event type such as (app.openedFromURL)
        """
        web_request_event = event_class(event_id, event_type)
        web_request_event.fusion_app = self
        self.events.append(web_request_event)

    def add_custom_feature(
            self,
            name: str,
            feature_class: Any,
            options: dict
    ):
        """Register a workspace event that can respond to various workspace actions

        Args:
            name: The name of the command
            feature_class: This should be your subclass of apper.Fusion360CustomFeatureBase
            options: Set of options for the command see the full set of `options <usage/options>`_
        """
        options['app_name'] = self.name
        options['fusion_app'] = self

        custom_feature = feature_class(name, options)
        custom_feature.fusion_app = self
        self.features.append(custom_feature)

    def check_for_updates(self):
        """Not Implemented"""
        pass

    def run_app(self):
        """Runs the Addin"""

        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        try:
            for run_command in self.commands:
                run_command.on_run()

            for run_feature in self.features:
                run_feature.on_run()
        except:
            if ui:
                ui.messageBox('Running App failed: {}'.format(traceback.format_exc()))

    def stop_app(self):
        """Stops the Addin and cleans up all of the created UI elements"""

        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            for stop_command in self.commands:
                stop_command.on_stop()

            for toolbar_tab in self.tabs:
                if toolbar_tab.isValid:
                    toolbar_tab.deleteMe()

            for event in self.events:
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

    def get_all_preferences(self) -> dict:
        """Gets all preferences stored for this application

        Returns:
            All preferences as a dictionary
        """
        file_name = os.path.join(self.default_dir, "preferences.json")
        all_preferences = self.read_json_file(file_name)

        return all_preferences

    @staticmethod
    def read_json_file(file_name):
        """Static method to read a json file and return a dictionary object

        Will fail if the input file cannot be interpreted as a JSON object

        Returns:
            Input file as a dictionary
        """
        if os.path.exists(file_name):
            with open(file_name) as f:
                try:
                    new_dict = json.load(f)
                except:
                    new_dict = {}
        else:
            new_dict = {}

        return new_dict

    def get_group_preferences(self, group_name: str) -> dict:
        """Gets preferences for a particular group (typically a given command)

        Args:
            group_name: name of parent group in which to store preferences

        Returns:
            A dictionary of just the options associated to this particular group
        """
        all_preferences = self.get_all_preferences()
        group_preferences = all_preferences.get(group_name, {})
        return group_preferences

    def save_preferences(self, group_name: str, new_group_preferences: dict, merge: bool):
        """Saves preferences for the application

        Args:
            group_name: name of parent group in which to store preferences
            new_group_preferences: Dictionary of preferences to save
            merge: If True then the new preferences in the group will be merged, if False all old values are deleted

        Returns:
            A string with possible values: "Updated", "Created", or "Failed"

        """

        all_preferences = self.get_all_preferences()

        old_group_preferences = all_preferences.get(group_name, None)

        if old_group_preferences is not None:
            result = "Updated"
        else:
            result = "Created"

        if merge:
            old_group_preferences.update(new_group_preferences)
            all_preferences[group_name] = old_group_preferences
        else:
            all_preferences[group_name] = new_group_preferences

        if not self._write_preferences(all_preferences):
            result = "Failed"
        return result

    def _write_preferences(self, preferences_dict: dict):
        file_name = os.path.join(self.default_dir, "preferences.json")
        try:
            preferences_text = json.dumps(preferences_dict)
            with open(file_name, "w") as f:
                f.write(preferences_text)
            if self.logging_enabled:
                self.logger.info(f"Preference file written at: {file_name}")
            return True
        except:
            if self.logging_enabled:
                self.logger.error(f"Preference file creation failed for: {file_name}")
            return False

    def initialize_preferences(self, defaults: dict, force=False):
        """Initializes preferences for the application

        Args:
            defaults: a default set of preferences
            force: If True, any existing user preferences will be over-written

        Returns:
            A string with possible values: "Created", "Exists", or "Failed"

        """
        file_name = os.path.join(self.default_dir, "preferences.json")
        if (not os.path.exists(file_name)) or force:
            if self._write_preferences(defaults):
                result = "Created"
                if self.logging_enabled:
                    self.logger.info(f"Preference file created at: {file_name}")
            else:
                result = "Failed"
                if self.logging_enabled:
                    self.logger.error(f"Preference file creation failed for: {file_name}")
        else:
            result = "Exists"
        return result

    def enable_logging(self):
        log_dir = os.path.join(self.default_dir, "Logs", "")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_name = os.path.join(log_dir, self.name + '.log')

        self.logger = logging.getLogger(self.name)
        self.logger.handlers = []
        self.logger.setLevel("INFO")
        handler = logging.FileHandler(file_name)
        log_format = "%(asctime)s %(levelname)s -- %(message)s"
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logging_enabled = True


