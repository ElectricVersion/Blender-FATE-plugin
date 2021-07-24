import bpy
from io_fate_mdl.util import *
from io_fate_mdl.read_material import *
from io_fate_mdl.read_mesh import *
import bmesh

from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import AddObjectHelper
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
        return self.read_mdl_file(context, self.filepath)
        
    def read_mdl_file(self, context, filepath):
        print("Loading MDL file.")
        f = open(filepath, 'rb')
        data = f.read()
        f.close()
        #load the data
        
        reader = util.Reader(data)
        read_mesh.read_basic_info(reader)
        read_material.read_material_section(reader)
        read_mesh.read_mesh_section(reader)
        
        mesh = bpy.data.meshes.new("Untitled FATE Object")
        
        bm = bmesh.new()
        
        #print(reader.mdlData.vertices)
        
        vertices = {}
        for i in range(len(reader.mdlData.vertexReferences)):
            v = reader.mdlData.vertexReferences[i]
            v2 = reader.mdlData.uvReferences[i]
            if not (v in vertices):
                vertices[v] = VertexData()
                vertices[v].pos = reader.mdlData.vertices[v]
            vertices[v].uvPos.append(reader.mdlData.uvs[v2])
            vertices[v].references.append(i)
        
        for i in range(len(vertices)):
            vert = bm.verts.new(vertices[i].pos)
         
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()

        for f in reader.mdlData.triangles:
            bm.faces.new([bm.verts[i] for i in f])
        
        uv_layer = bm.loops.layers.uv.verify()
        for f in bm.faces:
            for loop in f.loops:
                loop_uv = loop[uv_layer]
                loop_uv.uv = vertices[loop.vert.index].uvPos.pop(0)

        
        bm.to_mesh(mesh)
        mesh.update()
        
        
        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh)
        
        return {'FINISHED'}