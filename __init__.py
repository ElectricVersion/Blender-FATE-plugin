import bpy
from io_fate_mdl.util import *
from io_fate_mdl.read_material import *

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


bl_info = {
    "name": "FATE .mdl importer",
    "description": "Import and export FATE .mdl files ",
    "author": "ElectricVersion",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "category": "Import-Export"
}

def register():
    bpy.utils.register_class(ImportMDL)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportMDL)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

def menu_func_import(self, context):
    self.layout.operator(ImportMDL.bl_idname, text="Import FATE model")

class ImportMDL(Operator, ImportHelper):
    """Import FATE model (.mdl)"""
    bl_idname = "import_mdl.mdl_data"
    bl_label = "Import FATE MDL"

    # ImportHelper mixin class uses this
    filename_ext = ".mdl"

    filter_glob: StringProperty(
        default="*.mdl",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return read_mdl_file(context, self.filepath)

def read_mdl_file(context, filepath):
    print("Loading MDL file.")
    f = open(filepath, 'rb')
    data = f.read()
    f.close()
    #load the data
    
    r = util.Reader(data)
    read_material.read_material_section(r)
    
    #print(data)

    return {'FINISHED'}