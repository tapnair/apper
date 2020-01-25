import traceback

import adsk.core
from .Fusion360CommandBase import Fusion360CommandBase

# handlers = []
import os
import sys


class PaletteCommandBase(Fusion360CommandBase):
    def __init__(self, name: str, options: dict):
        """
        Args:
            name:
            options:
        """
        super().__init__(name, options)

        self.palette_id = options.get('palette_id', 'Default Command Name')
        self.palette_name = options.get('palette_name', 'Palette Name')

        rel_path = options.get('palette_html_file_url', '')

        self.path = os.path.dirname(
            os.path.relpath(sys.modules[self.__class__.__module__].__file__, self.fusion_app.root_path))

        resource_path = os.path.join('./', self.path, rel_path)

        # self.palette_html_file_url = resource_path
        self.palette_html_file_url = rel_path

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
        return PaletteCreatedHandler(self)

    def on_html_event(self, html_args: adsk.core.HTMLEventArgs):
        """
        Args:
            html_args (adsk.core.HTMLEventArgs):
        """
        pass

    def on_palette_close(self):
        pass

    def on_palette_execute(self, palette: adsk.core.Palette):
        """
        Args:
            palette (adsk.core.Palette):
        """
        pass

    def on_stop(self):
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        palette = ui.palettes.itemById(self.palette_id)

        for handler in self.html_handlers:
            palette.incomingFromHTML.remove(handler)

        if palette:
            palette.deleteMe()

        super().on_stop()


# Base Class for creating Fusion 360 Palette
class PaletteCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self, cmd_object):
        """
        Args:
            cmd_object:
        """
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        """
        Args:
            args:
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:

            command_ = args.command
            inputs_ = command_.commandInputs

            on_execute_handler = PaletteExecuteHandler(self.cmd_object_)
            command_.execute.add(on_execute_handler)
            self.cmd_object_.handlers.append(on_execute_handler)

            if self.cmd_object_.debug:
                ui.messageBox('***Debug *** Palette Panel command created successfully')

            self.cmd_object_.on_create(command_, inputs_)

        except:
            if ui:
                ui.messageBox('Command created failed: {}'.format(traceback.format_exc()))


class PaletteExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, cmd_object):
        """
        Args:
            cmd_object:
        """
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        """
        Args:
            args:
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        try:

            command_ = args.command
            inputs_ = command_.commandInputs

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
                on_html_event_handler = HTMLEventHandler(self.cmd_object_)
                palette.incomingFromHTML.add(on_html_event_handler)
                self.cmd_object_.handlers.append(on_html_event_handler)
                self.cmd_object_.html_handlers.append(on_html_event_handler)

                # Add handler to CloseEvent of the palette.
                on_closed_handler = PaletteCloseHandler(self.cmd_object_)
                palette.closed.add(on_closed_handler)
                self.cmd_object_.handlers.append(on_closed_handler)
            else:
                palette.htmlFileURL = self.cmd_object_.palette_html_file_url
                palette.isVisible = True

            self.cmd_object_.on_palette_execute(palette)

            if self.cmd_object_.debug:
                ui.messageBox('***Debug command: {} executed successfully'.format(
                    self.cmd_object_.parentCommandDefinition.id))

        except:
            if ui:
                ui.messageBox('Palette Execution Failed: {}'.format(traceback.format_exc()) + self.cmd_object_.palette_html_file_url)


# Event handler for the palette HTML event.
class HTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self, cmd_object):
        """
        Args:
            cmd_object:
        """
        super().__init__()

        self.cmd_object_ = cmd_object

    def notify(self, args):
        """
        Args:
            args:
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            # ui.messageBox("in event")
            html_args = adsk.core.HTMLEventArgs.cast(args)

            self.cmd_object_.on_html_event(html_args)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the palette close event.
class PaletteCloseHandler(adsk.core.UserInterfaceGeneralEventHandler):
    def __init__(self, cmd_object):
        """
        Args:
            cmd_object:
        """
        super().__init__()
        self.cmd_object_ = cmd_object

    def notify(self, args):
        """
        Args:
            args:
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            # Delete the palette created by this add-in.
            self.cmd_object_.on_palette_close()
            # palette = ui.palettes.itemById(self.cmd_object_.palette_id)
            # if palette:
            #     palette.deleteMe()

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))







