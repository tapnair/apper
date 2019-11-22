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
        """
        Args:
            event_id:
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
            on_thread_event = ThreadEventHandler(self.custom_event_received)
            custom_event.add(on_thread_event)
            handlers.append(on_thread_event)

            # create and start the new thread

            self.thread = FusionThread(self.event_id, self.run_in_thread)
            self.thread.daemon = True
            self.thread.start()

        except Exception as e:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            print(traceback.format_exc())
            print(e)

    def custom_event_received(self, event_dict):
        """
        Args:
            event_dict:
        """
        pass

    def run_in_thread(self, thread, event_id):
        """
        Args:
            thread:
            event_id:
        """
        pass

    def on_stop(self):
        app = adsk.core.Application.get()
        app.unregisterCustomEvent(self.event_id)


# The event handler that responds to the custom event being fired.
# Assumes message being received is a json string
class ThreadEventHandler(adsk.core.CustomEventHandler):
    def __init__(self, receiver_function):
        """
        Args:
            receiver_function:
        """
        self.receiver_function = receiver_function
        super().__init__()

    def notify(self, args):
        """
        Args:
            args:
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
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# The class for the new thread.
class FusionThread(threading.Thread):
    def __init__(self, event_id, run_in_thread):
        """
        Args:
            event_id:
            run_in_thread:
        """
        threading.Thread.__init__(self)

        self.event_id = event_id
        self.run_function = run_in_thread

        stop_event = threading.Event()
        self.stopped = stop_event

    def run(self):
        self.run_function(self, self.event_id)


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
        self.document_handler = DocumentHandler(self.document_event_received)
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
        self.workspace_handler = WorkspaceHandler(self.workspace_event_received)
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
class DocumentHandler(adsk.core.DocumentEventHandler):
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
class WorkspaceHandler(adsk.core.WorkspaceEventHandler):
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
        pass
        app = adsk.core.Application.cast(adsk.core.Application.get())
        ui = app.userInterface

        try:
            event_args = adsk.core.WorkspaceEventArgs.cast(args)
            workspace = event_args.workspace
            self.workspace_function(event_args, workspace)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        # ui.messageBox('In MyWorkspaceActivatedHandler event handler.')

