# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright (c) 2020 by Patrick Rainsberry.                                   ~
#  :license: Apache2, see LICENSE for more details.                            ~
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Fusion360AppEvents.py                                                       ~
#  This file is a component of apper.                                          ~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import adsk.core
import adsk.fusion
import adsk.cam

import traceback

import threading
import json

handlers = []


# The class for the new thread.
class Fusion360CustomThread:
    def __init__(self, event_id):
        """Creates a new Custom Event handler and a new thread

        Args:
            event_id: Unique id, can be used by other functions to trigger the event
        """
        pass
        self.event_id = event_id
        self.thread = None
        self.fusion_app = None

        app = adsk.core.Application.get()
        ui = app.userInterface

        try:
            # Register the custom event and connect the handler.
            app.unregisterCustomEvent(event_id)

            custom_event = app.registerCustomEvent(event_id)
            on_thread_event = _CustomThreadEventHandler(self.custom_event_received)
            custom_event.add(on_thread_event)
            handlers.append(on_thread_event)

            # create and start the new thread

            self.thread = _FusionThread(self.event_id, self.run_in_thread)
            self.thread.daemon = True
            self.thread.start()

        except Exception as e:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            print(traceback.format_exc())
            print(e)

    def custom_event_received(self, event_dict):
        """Function that will run when event is triggered

        Args:
            event_dict: Argument passed to event.  Decoded JSON as a dict
        """
        pass

    def run_in_thread(self, thread, event_id):
        """Function to run in new thread

        Args:
            thread: Reference to thread that function is running in
            event_id: reference to an event id, not necessarily relevant in this case
        """
        pass

    def on_stop(self):
        app = adsk.core.Application.get()
        app.unregisterCustomEvent(self.event_id)


class _CustomThreadEventHandler(adsk.core.CustomEventHandler):
    def __init__(self, receiver_function):
        """The event handler that responds to the custom event being fired.

        Assumes message being received is a json string

        Args:
            receiver_function:
        """
        self.receiver_function = receiver_function
        super().__init__()

    def notify(self, args):
        """Method overwritten on parent class that will be executed when the event fires

        Args:
            args: event arguments
        """
        app = adsk.core.Application.get()
        ui = adsk.core.UserInterface.cast(app.userInterface)

        try:
            # Make sure a command isn't running before changes are made.
            if ui.activeCommand != 'SelectCommand':
                ui.commandDefinitions.itemById('SelectCommand').execute()

            # Get the value from the JSON data passed through the event.
            event_dict = json.loads(args.additionalInfo)
            self.receiver_function(event_dict)

        except:
            if ui:
                ui.messageBox('Thread Handler Failed:\n{}'.format(traceback.format_exc()))


# The class for the new thread.
class _FusionThread(threading.Thread):
    def __init__(self, event_id, run_in_thread, input_data=None):
        """Starts a new thread and runs the given function in it

        Args:
            event_id: Unique id, can be used by other functions to trigger the event
            run_in_thread: Function to run in new thread
            input_data: Optional parameter to pass extra data to the thread
        """
        threading.Thread.__init__(self)

        self.event_id = event_id
        self.run_function = run_in_thread
        self.input_data = input_data

        stop_event = threading.Event()
        self.stopped = stop_event

    def run(self):
        self.run_function(self, self.event_id, self.input_data)


class Fusion360NewThread:
    def __init__(self, event_id, input_data=None):
        """Creates a new thread. Useful for firing custom events.

        Args:
            event_id: Unique id, can be used by other functions to trigger the event
        """
        pass
        self.event_id = event_id
        self.thread = None
        self.fusion_app = None
        self.input_data = input_data

        app = adsk.core.Application.get()
        ui = app.userInterface

        try:
            # create and start the new thread
            self.thread = _FusionThread(self.event_id, self.run_in_thread, self.input_data)
            self.thread.daemon = True
            self.thread.start()

        except Exception as e:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            print(traceback.format_exc())
            print(e)

    def run_in_thread(self, thread, event_id, input_data=None):
        """Function to run in new thread

        Args:
            thread: Reference to thread that function is running in
            event_id: reference to an event id, not necessarily relevant in this case
            input_data: Optional parameter to pass extra data to the thread
        """
        pass


class Fusion360CustomEvent:
    def __init__(self, event_id):
        """Creates a new Custom Event handler

        Args:
            event_id: Unique id, can be used by other functions to trigger the event
        """
        pass
        self.event_id = event_id
        self.thread = None
        self.fusion_app = None

        app = adsk.core.Application.get()
        ui = app.userInterface

        try:
            # Register the custom event and connect the handler.
            app.unregisterCustomEvent(event_id)

            custom_event = app.registerCustomEvent(event_id)
            on_custom_event = _CustomThreadEventHandler(self.custom_event_received)
            custom_event.add(on_custom_event)
            handlers.append(on_custom_event)

        except Exception as e:
            if ui:
                ui.messageBox('Failed creating custom event:\n{}'.format(traceback.format_exc()))
            print(traceback.format_exc())
            print(e)

    def custom_event_received(self, event_dict: dict):
        """Function that will run when event is triggered

        Args:
            event_dict: Argument passed to event.  Decoded JSON as a dict
        """
        pass

    def on_stop(self):
        app = adsk.core.Application.get()
        app.unregisterCustomEvent(self.event_id)


# The class for the new thread.
class Fusion360DocumentEvent:
    def __init__(self, event_id: str, event_type):
        """
        Args:
            event_id:
            event_type:
        """
        self.event_id = event_id
        self.fusion_app = None
        self.event_type = event_type
        self.document_handler = _DocumentHandler(self.document_event_received)
        event_type.add(self.document_handler)
        handlers.append(self.document_handler)

    def document_event_received(self, event_args, document):
        """
        Args:
            event_args:
            document:
        """
        pass

    def on_stop(self):
        self.event_type.remove(self.document_handler)


# The class for the new thread.
class Fusion360WorkspaceEvent:
    def __init__(self, event_id, event_type):
        """
        Args:
            event_id:
            event_type:
        """
        self.event_id = event_id
        self.fusion_app = None
        self.event_type = event_type
        self.workspace_handler = _WorkspaceHandler(self.workspace_event_received)
        event_type.add(self.workspace_handler)
        handlers.append(self.workspace_handler)

    def workspace_event_received(self, event_args, workspace):
        """
        Args:
            event_args:
            workspace:
        """
        pass

    def on_stop(self):
        self.event_type.remove(self.workspace_handler)


# Event handler for the documentActivated event.
class _DocumentHandler(adsk.core.DocumentEventHandler):
    def __init__(self, document_event_received):
        """
        Args:
            document_event_received:
        """
        self.document_function = document_event_received
        super().__init__()

    def notify(self, args):
        """
        Args:
            args:
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface
        try:
            event_args = adsk.core.DocumentEventArgs.cast(args)

            document = event_args.document

            self.document_function(event_args, document)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

        # # Code to react to the event.
        # ui.messageBox('In MyDocumentActivatedHandler event handler.')


# Event handler for the workspaceActivated event.
class _WorkspaceHandler(adsk.core.WorkspaceEventHandler):
    def __init__(self, workspace_event_received):
        """
        Args:
            workspace_event_received:
        """
        super().__init__()
        self.workspace_function = workspace_event_received

    def notify(self, args):
        """
        Args:
            args:
        """
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            event_args = adsk.core.WorkspaceEventArgs.cast(args)
            workspace = event_args.workspace
            self.workspace_function(event_args, workspace)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        # ui.messageBox('In MyWorkspaceActivatedHandler event handler.')


# Event handler for the workspaceActivated event.
class WebRequestHandler(adsk.core.WebRequestEventHandler):
    """Web Request Handler

    """
    def __init__(self, web_request_event_received):
        """
        Args:
            web_request_event_received:
        """
        super().__init__()
        self.web_request_function = web_request_event_received

    def notify(self, args):
        """
        Args:
            args:
        """
        pass
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            event_args = adsk.core.WebRequestEventArgs.cast(args)
            file = event_args.file
            fusion_id = event_args.id
            occurrence_or_document = event_args.occurrenceOrDocument
            private_info = event_args.privateInfo
            properties = event_args.properties

            # TODO implement error checking and type checks here.  Was getting weird errors.
            # if len(event_args.privateInfo) > 1:
            #     try:
            #         private_info = json.loads(event_args.privateInfo)
            #     except:
            #         private_info = ""
            # if len(event_args.properties) > 1:
            #     try:
            #         properties = json.loads(event_args.properties)
            #     except:
            #         properties = ""

            self.web_request_function(event_args, file, fusion_id, occurrence_or_document, private_info, properties)

        except:
            ui.messageBox('Failed to load data in event handler:\n{}'.format(traceback.format_exc()))
        # ui.messageBox('In MyWorkspaceActivatedHandler event handler.')


# The class for the new thread.
class Fusion360WebRequestEvent:
    """Create a new Web Request Event action

        Args:
            event_id: A unique id for this event
            event_type: One of: [Application.insertedFromURL, Application.insertingFromURL, Application.openedFromURL, Application.openingFromURL]
        """

    def __init__(self, event_id: str, event_type):
        self.event_id = event_id
        self.fusion_app = None
        self.event_type = event_type
        self.web_request_handler = WebRequestHandler(self.web_request_event_received)
        event_type.add(self.web_request_handler)
        handlers.append(self.web_request_handler)

    def web_request_event_received(self, event_args, file, fusion_id, occurrence_or_document, private_info, properties):
        """This function will be executed in response to the command event

            Args:
                properties: design properties passed with the file (Partnumber Number, Description, Name)
                private_info: Extra info passed as json object
                fusion_id: A unique identifier to help determine whether the component is new or an instance
                occurrence_or_document: If opened, then it is a new document.  If it was inserted, it is the created occurence
                file: Path to the file that was just received
                event_args: WebRequestEventArgs
            """
        pass

    def on_stop(self):
        """stop listening to the event"""
        self.event_type.remove(self.web_request_handler)


class _CommandEventHandler(adsk.core.ApplicationCommandEventHandler):
    def __init__(self, command_function):
        super().__init__()
        self.command_function = command_function

    def notify(self, args):
        try:
            event_args = adsk.core.ApplicationCommandEventArgs.cast(args)
            command_id = event_args.commandId
            command_definition = event_args.commandDefinition
            self.command_function(event_args, command_id, command_definition)

        except:
            app = adsk.core.Application.cast(adsk.core.Application.get())
            ui = app.userInterface
            ui.messageBox('Failed to handle Command Event:\n{}'.format(traceback.format_exc()))


class Fusion360CommandEvent:
    def __init__(self, event_id, event_type):
        """Create a new Command Event action

        Args:
            event_id: A unique id for this event
            event_type: One of: [UserInterface.commandCreated, UserInterface.commandStarting, UserInterface.commandTerminated]
        """
        self.event_id = event_id
        self.fusion_app = None
        self.event_type = event_type
        self.command_handler = _CommandEventHandler(self.command_event_received)
        event_type.add(self.command_handler)
        handlers.append(self.command_handler)

    def command_event_received(self, event_args, command_id, command_definition):
        """This function will be executed in response to the command event

        Args:
            command_definition: the command definition of the command that was just executed
            command_id: the id of the command that was just executed
            event_args: ApplicationCommandEventArgs
        """
        pass

    def on_stop(self):
        """stop listening to the event"""
        self.event_type.remove(self.command_handler)