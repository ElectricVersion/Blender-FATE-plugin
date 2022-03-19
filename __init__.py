import bpy
from .util import *
from .read_material import *
from .write_material import *
from .read_mesh import *
from .write_mesh import *
from .read_sms_mesh import *
from .write_sms_mesh import *
import bmesh

from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
from bpy_extras.object_utils import AddObjectHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
import mathutils
from bpy_extras import object_utils
import math

bl_info = {
    "name": "FATE .mdl importer",
    "description": "Import and export FATE .mdl files ",
    "author": "ElectricVersion",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "category": "Import-Export"
}

def register():
    bpy.utils.register_class(Import_MDL)
    bpy.utils.register_class(Import_SMS)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(ExportMDL)
    bpy.utils.register_class(Export_SMS)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(Import_MDL)
    bpy.utils.unregister_class(Import_SMS)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ExportMDL)
    bpy.utils.unregister_class(Export_SMS)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

def menu_func_import(self, context):
    self.layout.operator(Import_MDL.bl_idname, text="Import FATE mdl")
    self.layout.operator(Import_SMS.bl_idname, text="Import FATE sms")

def menu_func_export(self, context):
    self.layout.operator(ExportMDL.bl_idname, text="Export FATE mdl")
    self.layout.operator(Export_SMS.bl_idname, text="Export FATE sms")


class ExportMDL(Operator, ExportHelper):
    """Import FATE model (.mdl)"""
    bl_idname = "export_mdl.mdl_data"
    bl_label = "Export FATE MDL"

    filename_ext = ".mdl"

    filter_glob: StringProperty(
        default="*.mdl",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return self.write_mdl_file(context, self.filepath)
        
    def write_mdl_file(self, context, filepath):
        print("Saving MDL file.")
        #first we make a bytes object of the file contents
        writer = util.Writer(context)
        
        write_mesh.write_basic_info(writer)
        write_material.write_material_section(writer)
        write_mesh.write_mesh_section(writer)
        
        f = open(filepath, 'wb')
        f.write(bytes(writer.txt_data))
        f.close()
        
        return {'FINISHED'}

class Import_MDL(Operator, ImportHelper):
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
        
        print("VERTEX REFERENCES", len(reader.mdl_data.vertex_references))
        vertices = {}
        for i in range(len(reader.mdl_data.vertex_references)):
            v = reader.mdl_data.vertex_references[i]
            v_2 = reader.mdl_data.uv_references[i]
            v_3 = reader.mdl_data.normal_references[i]
            if v not in vertices:
                vertices[v] = Vertex_Data()
                vertices[v].pos = reader.mdl_data.vertices[v]
            vertices[v].uv_pos.append(reader.mdl_data.uvs[v_2])
            vertices[v].normals.append(mathutils.Vector(reader.mdl_data.normals[v_3]))
            vertices[v].references.append(i)
        
        print("VERTEX COUNT", len(vertices))
        for i in range(len(vertices)):
            vert = bm.verts.new(vertices[i].pos)
            vert.normal = vertices[i].normals[0]
            vert.normal_update()
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        
        for f in reader.mdl_data.triangles:
            face_verts = []
            for i in f:
                if bm.verts[i] not in face_verts:
                    face_verts.append(bm.verts[i])
            print(face_verts)
            if bm.faces.get(face_verts) == None and len(face_verts) == 3:
                face = bm.faces.new(face_verts)
                face.normal_update()
        
        uv_layer = bm.loops.layers.uv.verify()
        for f in bm.faces:
            for loop in f.loops:
                loop_uv = loop[uv_layer]
                current_vert = vertices[loop.vert.index]
                loop_uv.uv = current_vert.uv_pos.pop(0)
            #calculate the normal for the face from each vertex normal
            #face_verts = {}
            #for i, v in enumerate(f.verts):
            #   face_verts[i] = v
            
        bm.normal_update()
        bm.to_mesh(mesh)
        mesh.update()
        
        bm.free()
        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh)
        
        return {'FINISHED'}
        
class Import_SMS(Operator, ImportHelper):
    """Import FATE model (.sms)"""
    bl_idname = "import_sms.sms_data"
    bl_label = "Import FATE SMS"

    # ImportHelper mixin class uses this
    filename_ext = ".sms"

    filter_glob: StringProperty(
        default="*.sms",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return self.read_sms_file(context, self.filepath)
        
    def read_sms_file(self, context, filepath):
        print("Loading SMS file.")
        f = open(filepath, 'rb')
        data = f.read()
        f.close()
        #load the data
        
        reader = util.Reader(data)
        read_sms_mesh.read_basic_info(reader)
        read_material.read_material_section(reader)
        read_sms_mesh.read_mesh_section(reader)
        
        armature = bpy.data.armatures.new("Untitled FATE Armature")
        object_utils.object_data_add(context, armature)
        override = bpy.context.copy()
        override["object"] = armature
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')
        armature_ebones = bpy.context.object.data.edit_bones
        #armature_bones = bpy.context.object.data.bones
        
        for i in range(len(reader.mdl_data.bones)):
            v = reader.mdl_data.bones[i]
            armature_ebones.new(name=v.name)
            #armature_ebones[v.name].use_relative_parent = True
            #armature_ebones[v.name].use_inherit_rotation = True
            #bpy.context.object.data.edit_bones[v.name].use_local_location = True
        #print(len(list(armature_ebones)))
        for i in range(len(reader.mdl_data.bones)):
            v = reader.mdl_data.bones[i]
            a_bone = armature_ebones[v.name]
            #bone.translate(mathutils.Vector(v.transform.c[3][0:3]))
            #bone.length = 0.01
            if v.parent > -1:
                a_bone.parent = armature_ebones[reader.mdl_data.bones[v.parent].name]
            else:
                a_bone.parent = None
            #bpy.context.object.data.edit_bones[v.name].tail = v.transform.c[3]
        
        #find the root bone
        root_bone = None
        for i in range(len(reader.mdl_data.bones)):
            v = reader.mdl_data.bones[i]
            if v.parent == -1:
                root_bone = i
            else:
                parent = reader.mdl_data.bones[v.parent]
                parent.children.append(i)
        print(root_bone)
        bones = reader.mdl_data.bones
        bone_order = [root_bone]
        while len(bone_order) < len(bones):
            for i in range(len(bones)):
                v = bones[i]
                if i not in bone_order and v.parent in bone_order:
                    bone_order.append(i)
        print(bone_order)
        #for i in bone_order:
        #    v = bones[i]
        #    parent_tfm = mathutils.Matrix.Identity(4)
        #    if v.parent > -1:
        #        parent_tfm = reader.mdl_data.bones[v.parent].local_transform
        #        inverted_tfm = v.local_transform.inverted()
        #        inverted_tfm.translation = v.pos
        #        print("inverted_tfm", v.name)
        #        print(inverted_tfm)
        #        print("parent_tfm", v.name)
        #        print(parent_tfm)
        #        v.local_transform = parent_tfm @ inverted_tfm
        #        #print("TRANSFORMS")
        #        #print(i.transform)
        #        #print(parent.transform)
        #        #print(i.local_transform)
        #    else:
        #        #v.local_transform = mathutils.Matrix.Identity(4)
        #        v.local_transform.translation = v.pos
        #    print("FINAL TRANSFORM FOR", v.name)
        #    print(v.local_transform)
        #    v.local_pos = v.local_transform.to_translation()
        
        for i in bone_order:
            v = bones[i]
            a_bone = armature_ebones[v.name]
            #a_bone.head = v.pos
            a_bone.length = 1.0
            #print(a_bone.use_relative_parent)
            #a_bone.matrix = v.transform
            #print(a_bone.use_relative_parent)
            #a_bone.translate(v.local_pos)
            tfm_loc = v.local_transform# @ mathutils.Matrix.Scale(-1, 4)
            tfm = v.transform.copy()
            axis, roll = bpy.types.Bone.AxisRollFromMatrix(tfm)
            #local_tfm = tfm.copy()
            #tfm_loc = v.local_transform.to_3x3()
            head_pos = mathutils.Vector((0,0,0))
            parent_tfm = mathutils.Matrix.Identity(4)
            if v.parent > -1:
                parent = bones[v.parent]
                parent_tfm = parent.local_transform
                #parent_tfm = bpy.types.Bone.MatrixFromAxisRoll(parent.tail - parent.head, parent.roll)
                #parent_tfm = mathutils.Matrix.Rotation(math.pi/2, 3, parent.vector)
                #v.local_transform = parent_tfm @ v.local_transform
                #parent_tfm_local = parent_tfm.to_4x4()
                #parent_tfm_local.translation = parent.head
                #axis = parent_tfm @ axis
                #head_pos = parent_tfm.translation.copy()
                head_pos = a_bone.parent.tail
                tfm_loc = parent_tfm @ tfm_loc
                v.local_transform = tfm_loc
                #tfm.translation = v.pos
            a_bone.head = head_pos
            #a_bone.tail = mathutils.Matrix.LocRotScale(a_bone.head, axis, None) @ v.pos
            a_bone.tail = (v.local_transform.translation)
            if a_bone.length < 0.001:
                a_bone.tail = tfm_loc @ mathutils.Vector(v.pos.normalized())
            a_bone.roll = roll
            #a_bone.tail = (tfm @ v.pos) + a_bone.head
            print(v.name, a_bone.head)
            print("MATRIX", v.name, tfm_loc)        
        #for i in bone_order:
        #    v = bones[i]
        #    a_bone = armature_ebones[v.name]
        #    if len(a_bone.children) == 1:
        #        a_bone.tail = a_bone.children[0].head
        #    elif len(a_bone.children) > 1:
        #        average_pos = mathutils.Vector((0.0,0.0,0.0))
        #        for j in a_bone.children:
        #            average_pos = average_pos + j.head
        #        average_pos = average_pos / len(a_bone.children)
        #        a_bone.tail = average_pos
        #    else:
        #        a_bone.length = 0.5
        #for i in bone_order:
        #    v = bones[i]
        #    a_bone = armature_ebones[v.name]
        #    if a_bone.length < 0.001:
        #        a_bone.length = 0.1
        print(len(list(armature_ebones)))
        
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        
        
        bm = bmesh.new()
        mesh = bpy.data.meshes.new("Untitled FATE Object")
        #print(reader.mdl_data.object_count)
        #print(len(reader.mdl_data.vertices))
        #print(len(reader.mdl_data.triangles))
        for i in range(len(reader.mdl_data.vertices)):
            #print("NEW VERTEX")
            vertex_bones = reader.mdl_data.vertices[i].bones
            vertex_position = mathutils.Vector((0,0,0))
            for j in vertex_bones:
                bone_weight = reader.mdl_data.vertices[i].bone_weights[j]
                bone_name = reader.mdl_data.bones[j].name
                #print(bone_name)
                bone_pos_local = reader.mdl_data.bones[j].local_pos
                bone_tfm_local = reader.mdl_data.bones[j].local_transform
                #print(bone_tfm_local)
                bone_offset =  mathutils.Vector(reader.mdl_data.vertices[i].bone_offsets[j])
                #print("WEIGHT " + str(bone_weight))
                bone_offset = bone_tfm_local @ bone_offset
                vertex_position_new = bone_offset
                vertex_position_new = vertex_position_new * bone_weight
                #print(vertex_position_new)
                vertex_position = vertex_position + vertex_position_new
            if len(vertex_bones) == 0:
                vertex_position = root_bone.local_pos
            vert = bm.verts.new( vertex_position )
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        
        #print(reader.mdl_data.tag_user_data)
        
        for f in reader.mdl_data.triangles:
            if bm.faces.get((bm.verts[f[0]], bm.verts[f[1]], bm.verts[f[2]])) == None:
                bm.faces.new((bm.verts[f[0]], bm.verts[f[1]], bm.verts[f[2]]))
        
        for i in range(len(reader.mdl_data.uvs)):
            uv = reader.mdl_data.uvs[i]
            reader.mdl_data.vertices[i].uv_pos.append(uv)
        
        uv_layer = bm.loops.layers.uv.verify()
        for f in bm.faces:
            for loop in f.loops:
                loop_uv = loop[uv_layer]
                current_vert = reader.mdl_data.vertices[loop.vert.index]
                loop_uv.uv = current_vert.uv_pos[0]
        
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()
        
        object_utils.object_data_add(context, mesh)
        #override = bpy.context.copy()
        override["object"] = mesh
        v_groups = bpy.context.object.vertex_groups
        
        for bone in reader.mdl_data.bones:
            if v_groups.get(bone.name) == None:
                v_groups.new(name=bone.name)
        for v in range(len(mesh.vertices)):
            vertex_index = v
            for bone_index in reader.mdl_data.vertices[vertex_index].bones:
                bone_weight = reader.mdl_data.vertices[vertex_index].bone_weights[bone_index]
                bone = reader.mdl_data.bones[bone_index]
                v_groups[bone_index].add([vertex_index], bone_weight, "REPLACE")
        arm_mod = bpy.data.objects[mesh.name].modifiers.new("Armature", "ARMATURE") #add armature modifier to the mesh
        arm_mod.object = bpy.data.objects[armature.name] #set the modifier to use the newly created armature
        #print(reader.mdl_data.object_count)
        #print(reader.mdl_data.object_names)
        return {'FINISHED'}
        
class Export_SMS(Operator, ExportHelper):
    """Import FATE model (.sms)"""
    bl_idname = "export_sms.sms_data"
    bl_label = "Export FATE SMS"

    filename_ext = ".sms"

    filter_glob: StringProperty(
        default="*.sms",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return self.write_sms_file(context, self.filepath)
        
    def write_sms_file(self, context, filepath):
        print("Saving SMS file.")
        #first we make a bytes object of the file contents
        writer = util.Writer(context)
        
        write_sms_mesh.write_basic_info(writer)
        write_material.write_material_section(writer)
        write_sms_mesh.write_mesh_section(writer)
        
        f = open(filepath, 'wb')
        f.write(bytes(writer.txt_data))
        f.close()
        
        return {'FINISHED'}
