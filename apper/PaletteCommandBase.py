# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright (c) 2020 by Patrick Rainsberry.                                   ~
#  :license: Apache2, see LICENSE for more details.                            ~
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  PaletteCommandBase.py                                                       ~
#  This file is a component of ApperSample.                                    ~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import traceback

import adsk.core
from .Fusion360CommandBase import Fusion360CommandBase

import os
import sys


class PaletteCommandBase(Fusion360CommandBase):
    """Class for creating a Fusion 360 Command that will show a web palette

        Args:
            name: Name of the Command
            options: Dictionary of options
        """

    def __init__(self, name: str, options: dict):
        super().__init__(name, options)

        self.palette_id = options.get('palette_id', 'Default Command Name')
        self.palette_name = options.get('palette_name', 'Palette Name')

        rel_path = options.get('palette_html_file_url', '')

        self.path = os.path.dirname(
            os.path.relpath(sys.modules[self.__class__.__module__].__file__, self.fusion_app.root_path))

        resource_path = os.path.join('./', self.path, rel_path)

        self.palette_html_file_url = resource_path
        # self.palette_html_file_url = rel_path

        self.palette_is_visible = options.get('palette_is_visible', True)
        self.palette_show_close_button = options.get('palette_show_close_button', True)
        self.palette_is_resizable = options.get('palette_is_resizable', True)
        self.palette_width = options.get('palette_width', 600)
        self.palette_height = options.get('palette_height', 600)

        self.palette = None
        self.args = None
        self.handlers = []
        self.html_handlers = []

    def _get_create_event(self):
        return _PaletteCreatedHandler(self)

    def on_html_event(self, html_args: adsk.core.HTMLEventArgs):
        """
        Args:
            html_args: the arguments sent with the command from the html page
        """
        pass

    def on_palette_close(self):
        """Run when the palette is closed

        """
        pass

    def on_palette_execute(self, palette: adsk.core.Palette):
        """Function is run when the palette is executed.  Useful to gather initial data and send to html page

        Args:
            palette: Reference to the palette
        """
        pass

    def on_stop(self):
        """Function is run when the addin stops.

        Clean up.  If overridden ensure to execute with super().on_stop()
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        palette = ui.palettes.itemById(self.palette_id)

        for handler in self.html_handlers:
            palette.incomingFromHTML.remove(handler)

        if palette:
            palette.deleteMe()

        super().on_stop()


class _PaletteCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Event handler for the palette created event.

    Args:
        cmd_object: the parent command object
    """
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        """Method executed by Fusion.  DOn't rename

        Args:
            args: args for command
        """
        try:

            command_ = args.command
            inputs_ = command_.commandInputs

            on_execute_handler = _PaletteExecuteHandler(self.cmd_object_)
            command_.execute.add(on_execute_handler)
            self.cmd_object_.handlers.append(on_execute_handler)

            self.cmd_object_.on_create(command_, inputs_)

        except:
            app = adsk.core.Application.cast(adsk.core.Application.get())
            ui = app.userInterface
            ui.messageBox('Command created failed: {}'.format(traceback.format_exc()))


class _PaletteExecuteHandler(adsk.core.CommandEventHandler):
    """Event handler for the palette execution event.

    Args:
        cmd_object: the parent command object
    """

    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        """Method executed by Fusion.  Don't rename

        Args:
            args: args for command
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        try:

            # Create and display the palette.
            palette = ui.palettes.itemById(self.cmd_object_.palette_id)

            if not palette:
                palette = ui.palettes.add(
                    self.cmd_object_.palette_id,
                    self.cmd_object_.palette_name,
                    self.cmd_object_.palette_html_file_url,
                    self.cmd_object_.palette_is_visible,
                    self.cmd_object_.palette_show_close_button,
                    self.cmd_object_.palette_is_resizable,
                    self.cmd_object_.palette_width,
                    self.cmd_object_.palette_height
                )

                # Add handler to HTMLEvent of the palette.
                on_html_event_handler = _HTMLEventHandler(self.cmd_object_)
                palette.incomingFromHTML.add(on_html_event_handler)
                self.cmd_object_.handlers.append(on_html_event_handler)
                self.cmd_object_.html_handlers.append(on_html_event_handler)

                # Add handler to CloseEvent of the palette.
                on_closed_handler = _PaletteCloseHandler(self.cmd_object_)
                palette.closed.add(on_closed_handler)
                self.cmd_object_.handlers.append(on_closed_handler)

            else:
                palette.htmlFileURL = self.cmd_object_.palette_html_file_url
                palette.isVisible = True

            self.cmd_object_.on_palette_execute(palette)

        except:
            ui.messageBox('Palette ({}) Execution Failed: {}'.format(
                self.cmd_object_.palette_html_file_url,
                traceback.format_exc())
            )


class _HTMLEventHandler(adsk.core.HTMLEventHandler):
    """Event handler for the palette HTML event.

    Args:
        cmd_object: the parent command object
    """

    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        """Method executed by Fusion.  Don't rename

        Args:
            args: args for command
        """
        try:
            html_args = adsk.core.HTMLEventArgs.cast(args)
            self.cmd_object_.on_html_event(html_args)

        except:
            app = adsk.core.Application.cast(adsk.core.Application.get())
            ui = app.userInterface
            ui.messageBox('Failed Handling HTML Event:\n{}'.format(traceback.format_exc()))


class _PaletteCloseHandler(adsk.core.UserInterfaceGeneralEventHandler):
    """Event handler for the palette close event.

    Args:
        cmd_object: the parent command object
    """
    def __init__(self, cmd_object):
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        """Method executed by Fusion.  Don't rename

        Args:
            args: args for command
        """
        try:
            self.cmd_object_.on_palette_close()

        except:
            app = adsk.core.Application.cast(adsk.core.Application.get())
            ui = app.userInterface
            ui.messageBox('Failed During Palette Close:\n{}'.format(traceback.format_exc()))
