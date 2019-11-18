import adsk.core
import adsk.fusion
import adsk.cam
import traceback

from typing import Optional, List

import os
from os.path import expanduser
import json
import uuid

import time


# Class to quickly access Fusion Application Objects
class AppObjects(object):

    def __init__(self):

        self.app = adsk.core.Application.cast(adsk.core.Application.get())

        # Get import manager
        self.import_manager = self.app.importManager

        # Get User Interface
        self.ui = self.app.userInterface

        self.document = self.app.activeDocument
        self.product = self.app.activeProduct

        self._design = self.design

    @property
    def design(self) -> Optional[adsk.fusion.Design]:
        design_ = self.document.products.itemByProductType('DesignProductType')
        if design_ is not None:
            return design_
        else:
            return None

    @property
    def cam(self) -> Optional[adsk.cam.CAM]:
        cam_ = self.document.products.itemByProductType('CAMProductType')
        if cam_ is not None:
            return cam_
        else:
            return None

    @property
    def units_manager(self) -> Optional[adsk.core.UnitsManager]:
        if self.product.productType == 'DesignProductType':
            units_manager_ = self._design.fusionUnitsManager
        else:
            units_manager_ = self.product.unitsManager

        if units_manager_ is not None:
            return units_manager_
        else:
            return None

    @property
    def export_manager(self) -> Optional[adsk.fusion.ExportManager]:
        if self._design is not None:
            export_manager_ = self._design.exportManager
            return export_manager_
        else:
            return None

    @property
    def root_comp(self) -> Optional[adsk.fusion.Component]:
        if self.product.productType == 'DesignProductType':
            root_comp_ = self.design.rootComponent
            return root_comp_
        else:
            return None

    @property
    def time_line(self) -> Optional[adsk.fusion.Timeline]:
        if self.product.productType == 'DesignProductType':
            if self._design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
                time_line_ = self.product.timeline

                return time_line_

        return None


def start_group() -> int:
    """Starts a time line group

    :return: The index of the time line
    :rtype: int
    """
    # Gets necessary application objects
    app_objects = get_app_objects()

    # Start time line group
    start_index = app_objects['time_line'].markerPosition

    return start_index


def end_group(start_index: int):
    """Ends a time line group

    :param start_index: Time line index
    :type start_index: int

    """

    # Gets necessary application objects
    app_objects = get_app_objects()

    end_index = app_objects['time_line'].markerPosition - 1

    app_objects['time_line'].timelineGroups.add(start_index, end_index)


def import_dxf(dxf_file, component, plane) -> adsk.fusion.Sketches:
    """Import dxf file with one sketch per layer.

    :param dxf_file: The full path to the dxf file
    :type dxf_file: str
    :param component: The target component for the new sketch(es)
    :type component: adsk.fusion.Component
    :param plane: The plane on which to import the DXF file.
    :type plane: adsk.fusion.ConstructionPlane or adsk.fusion.BRepFace
    :return: A Collection of the created sketches
    :rtype: adsk.core.ObjectCollection

    """

    ao = AppObjects()
    import_manager = ao.import_manager
    dxf_options = import_manager.createDXF2DImportOptions(dxf_file, plane)
    import_manager.importToTarget(dxf_options, component)
    sketches = dxf_options.results
    return sketches


def sketch_by_name(sketches: adsk.fusion.Sketches, name: str) -> adsk.fusion.Sketch:
    """Finds a sketch by name in a list of sketches Useful for parsing a collection of sketches such as DXF import results.

    :param sketches: A list of sketches.
    :type sketches: adsk.fusion.Sketches
    :param name: The name of the sketch to find.
    :return: The sketch matching the name if it is found.
    :rtype: adsk.fusion.Sketch

    Args:
        sketches (adsk.fusion.Sketches):
        name (str):
    """
    return_sketch = None
    for sketch in sketches:
        if sketch.name == name:
            return_sketch = sketch
    return return_sketch


def extrude_all_profiles(sketch, distance, component, operation) -> adsk.fusion.ExtrudeFeature:
    """Create extrude features of all profiles in a sketch The new feature will
    be created in the given target component and extruded by a distance

    :param sketch: The sketch from which to get profiles
    :type sketch: adsk.fusion.Sketch
    :param distance: The distance to extrude the profiles.
    :type distance: float
    :param component: The target component for the extrude feature
    :type component: adsk.fusion.Component
    :param operation: The feature operation type from enumerator.
    :type operation: adsk.fusion.FeatureOperations
    :return: THe new extrude feature.
    :rtype: adsk.fusion.ExtrudeFeature

    """
    profile_collection = adsk.core.ObjectCollection.create()
    for profile in sketch.profiles:
        profile_collection.add(profile)

    extrudes = component.features.extrudeFeatures
    ext_input = extrudes.createInput(profile_collection, operation)
    distance_input = adsk.core.ValueInput.createByReal(distance)
    ext_input.setDistanceExtent(False, distance_input)
    extrude_feature = extrudes.add(ext_input)
    return extrude_feature


def create_component(target_component, name) -> adsk.fusion.Occurrence:
    """Creates a new empty component in the target component

    :param target_component: The target component for the new component
    :type target_component:
    :param name: The name of the new component
    :type name: str
    :return: The reference to the occurrence of the newly created component.
    :rtype: adsk.fusion.Occurrence

    """
    transform = adsk.core.Matrix3D.create()
    new_occurrence = target_component.occurrences.addNewComponent(transform)
    new_occurrence.component.name = name
    return new_occurrence


def rect_body_pattern(target_component, bodies, x_axis, y_axis, x_qty, x_distance, y_qty,
                      y_distance) -> adsk.core.ObjectCollection:
    """Creates rectangle pattern of bodies based on vectors

    Args:
        target_component: Component in which to create the patern
        bodies (list of adsk.fusion.BRepBody): bodies to pattern
        x_axis(adsk.core.Vector3D): vector defining direction 1
        y_axis (adsk.core.Vector3D): vector defining direction 2
        x_qty (int): Number of instances in direction 1
        x_distance (float): Distance between instances in direction 1
        y_qty (int): Number of instances in direction 1
        y_distance (float): Distance between instances in direction 1

    """
    move_feats = target_component.features.moveFeatures

    x_bodies = adsk.core.ObjectCollection.create()
    all_bodies = adsk.core.ObjectCollection.create()

    for body in bodies:
        x_bodies.add(body)
        all_bodies.add(body)

    for i in range(1, x_qty):

        # Create a collection of entities for move
        x_source = adsk.core.ObjectCollection.create()

        for body in bodies:
            new_body = body.copyToComponent(target_component)
            x_source.add(new_body)
            x_bodies.add(new_body)
            all_bodies.add(new_body)

        x_transform = adsk.core.Matrix3D.create()
        x_axis.normalize()
        x_axis.scaleBy(x_distance * i)
        x_transform.translation = x_axis

        move_input_x = move_feats.createInput(x_source, x_transform)
        move_feats.add(move_input_x)

    for j in range(1, y_qty):
        # Create a collection of entities for move
        y_source = adsk.core.ObjectCollection.create()

        for body in x_bodies:
            new_body = body.copyToComponent(target_component)
            y_source.add(new_body)
            all_bodies.add(new_body)

        y_transform = adsk.core.Matrix3D.create()
        y_axis.normalize()
        y_axis.scaleBy(y_distance * j)
        y_transform.translation = y_axis

        move_input_y = move_feats.createInput(y_source, y_transform)
        move_feats.add(move_input_y)

    return all_bodies


# Creates Combine Feature in target with all tool bodies as source
def combine_feature(target_body: adsk.fusion.BRepBody, tool_bodies: List[adsk.fusion.BRepBody],
                    operation: adsk.fusion.FeatureOperations):
    """Creates Combine Feature in target with all tool bodies as source

    Args:
        target_body (adsk.fusion.BRepBody): Target body for the combine feature
        tool_bodies: (list of adsk.fusion.BRepBody): A list of tool bodies for the combine
        operation (adsk.fusion.FeatureOperations): An Enumerator defining the feature operation type
    """

    # Get Combine Features
    combine_features = target_body.parentComponent.features.combineFeatures

    # Define a collection and add all tool bodies to it
    combine_tools = adsk.core.ObjectCollection.create()

    for tool in tool_bodies:
        # todo add error checking
        combine_tools.add(tool)

    # Create Combine Feature
    combine_input = combine_features.createInput(target_body, combine_tools)
    combine_input.operation = operation
    combine_features.add(combine_input)


# Get default directory
def get_default_dir(app_name):
    """Creates a directory in the user's home folder to store data related to this app

    Args:
        app_name (str): Name of the Application
    """

    # Get user's home directory
    default_dir = expanduser("~")

    # Create a subdirectory for this application settings
    default_dir = os.path.join(default_dir, app_name, "")

    # Create the folder if it does not exist
    if not os.path.exists(default_dir):
        os.makedirs(default_dir)

    return default_dir


def get_settings_file(app_name):
    """Create (or get) a settings file name in the default app directory

    Args:
        app_name (str): Name of the Application
    """
    default_dir = get_default_dir(app_name)
    file_name = os.path.join(default_dir, ".settings.json")
    return file_name


# Write App Settings
def write_settings(app_name, settings):
    """Write a settings file into the default directory for the app

    Args:
        app_name (str): Name of the Application
        settings (dict): Stores a dictionary as a json string
    """
    settings_text = json.dumps(settings)
    file_name = get_settings_file(app_name)

    f = open(file_name, "w")
    f.write(settings_text)
    f.close()


# Read App Settings
def read_settings(app_name):
    """Read a settings file into the default directory for the app

    Args:
        app_name (str): Name of the Application
    """
    file_name = get_settings_file(app_name)
    if os.path.exists(file_name):
        with open(file_name) as f:
            try:
                settings = json.load(f)
            except:
                settings = {}
    else:
        settings = {}

    return settings


# Creates directory and returns file name for log file
def get_log_file_name(app_name):

    default_dir = get_default_dir(app_name)

    log_dir = os.path.join(default_dir, "logs", "")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

    # Create file name in this path
    log_file_name = app_name + '-Log-' + time_stamp + '.txt'

    file_name = os.path.join(log_dir, log_file_name)

    return file_name


def open_doc(data_file: adsk.core.DataFile):
    """Simple wrapper to open a dataFile in the application window

    Args:
        data_file(adsk.core.DataFile): The data file to open
    """
    app = adsk.core.Application.get()

    try:
        document = app.documents.open(data_file, True)
        if document is not None:
            document.activate()
    except:
        pass


# get a UUID - URL safe, Base64
def get_a_uuid():
    """get a UUID - URL safe, Base64"""

    r_uuid = str(uuid.uuid4())
    return r_uuid


def item_id(item, app_name):
    """Gets (and possibly assigns) a unique identifier (UUID) to any item in Fusion 360

    Args:
        item: Any Fusion Object that supports attributes
        app_name (str): Name of the Application
    """
    this_id = None
    if item.attributes is not None:
        if item.attributes.itemByName(app_name, "id") is not None:
            this_id = item.attributes.itemByName(app_name, "id").value
        else:
            new_id = get_a_uuid()
            item.attributes.add(app_name, "id", new_id)
            this_id = new_id

    return this_id


def get_item_by_id(this_id, app_name):
    """Returns an item based on the assigned ID set with item_id()

    Args:
        this_id(str): The unique id generated originally by calling item_id()
        app_name (str): Name of the Application
    """
    ao = AppObjects()
    attributes = ao.design.findAttributes(app_name, "id")

    item = None
    for attribute in attributes:
        if attribute.value == this_id:
            item = attribute.parent

    return item


def get_log_file(app_name):
    """Gets the filename for a default log file

    Args:
        app_name (str): Name of the Application
    """
    default_dir = get_default_dir(app_name)
    file_name = os.path.join(default_dir, "logger.log")
    return file_name


def get_std_out_file(app_name):
    """Get temporary stdout file for the app

    Args:
        app_name (str): Name of the Application
    """
    default_dir = get_default_dir(app_name)
    file_name = os.path.join(default_dir, "std_out.txt")
    return file_name


def get_std_err_file(app_name):
    """Get temporary stderr file for the app

    Args:
        app_name (str): Name of the Application
    """
    default_dir = get_default_dir(app_name)
    file_name = os.path.join(default_dir, "std_err.txt")
    return file_name
