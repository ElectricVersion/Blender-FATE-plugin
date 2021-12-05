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
    bpy.utils.register_class(ImportSMS)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(ExportMDL)
    bpy.utils.register_class(ExportSMS)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportMDL)
    bpy.utils.unregister_class(ImportSMS)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ExportMDL)
    bpy.utils.unregister_class(ExportSMS)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

def menu_func_import(self, context):
    self.layout.operator(ImportMDL.bl_idname, text="Import FATE mdl")
    self.layout.operator(ImportSMS.bl_idname, text="Import FATE sms")

def menu_func_export(self, context):
    self.layout.operator(ExportMDL.bl_idname, text="Export FATE mdl")
    self.layout.operator(ExportSMS.bl_idname, text="Export FATE sms")


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
        f.write(writer.txtData)
        f.close()
        
        return {'FINISHED'}

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
        
        print("VERTEX REFERENCES", len(reader.mdlData.vertexReferences))
        vertices = {}
        for i in range(len(reader.mdlData.vertexReferences)):
            v = reader.mdlData.vertexReferences[i]
            v2 = reader.mdlData.uvReferences[i]
            v3 = reader.mdlData.normalReferences[i]
            if v not in vertices:
                vertices[v] = VertexData()
                vertices[v].pos = reader.mdlData.vertices[v]
            vertices[v].uvPos.append(reader.mdlData.uvs[v2])
            vertices[v].normals.append(mathutils.Vector(reader.mdlData.normals[v3]))
            vertices[v].references.append(i)
        
        print("VERTEX COUNT", len(vertices))
        for i in range(len(vertices)):
            vert = bm.verts.new(vertices[i].pos)
            vert.normal = vertices[i].normals[0]
            vert.normal_update()
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        
        for f in reader.mdlData.triangles:
            faceVerts = []
            for i in f:
                if bm.verts[i] not in faceVerts:
                    faceVerts.append(bm.verts[i])
            print(faceVerts)
            if bm.faces.get(faceVerts) == None and len(faceVerts) == 3:
                face = bm.faces.new(faceVerts)
                face.normal_update()
        
        uv_layer = bm.loops.layers.uv.verify()
        for f in bm.faces:
            for loop in f.loops:
                loop_uv = loop[uv_layer]
                currentVert = vertices[loop.vert.index]
                loop_uv.uv = currentVert.uvPos.pop(0)
            #calculate the normal for the face from each vertex normal
            #faceVerts = {}
            #for i, v in enumerate(f.verts):
            #   faceVerts[i] = v
            
        bm.normal_update()
        bm.to_mesh(mesh)
        mesh.update()
        
        bm.free()
        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh)
        
        return {'FINISHED'}
        
class ImportSMS(Operator, ImportHelper):
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
        armatureBones = bpy.context.object.data.edit_bones
        
        for i in range(len(reader.mdlData.bones)):
            v = reader.mdlData.bones[i]
            bpy.ops.armature.bone_primitive_add(name=v.name)
            #bpy.context.object.data.edit_bones[v.name].use_inherit_rotation = True
            #bpy.context.object.data.edit_bones[v.name].use_local_location = True
        
        for i in range(len(reader.mdlData.bones)):
            v = reader.mdlData.bones[i]
            bone = armatureBones[v.name]
            #bone.translate(mathutils.Vector(v.transform.c[3][0:3]))
            #bone.length = 0.01
            if v.parent > -1:
                bone.parent = armatureBones[reader.mdlData.bones[v.parent].name]
            #bpy.context.object.data.edit_bones[v.name].tail = v.transform.c[3]
        
        #find the root bone
        rootBone = None
        for i in range(len(reader.mdlData.bones)):
            v = reader.mdlData.bones[i]
            if v.parent == -1:
                rootBone = v
            else:
                parent = reader.mdlData.bones[v.parent]
                parent.children.append(i)
        
        done = False
        boneProcOrder = []
        boneOrder = []
        currentBone = rootBone
        while not done:
            boneOrder.append(currentBone)
            children = currentBone.children
            for i in children:
                boneProcOrder.append(reader.mdlData.bones[i])
            if len(boneProcOrder) == 0:
                done = True
            else:
                currentBone = boneProcOrder.pop(0)
        
        #print(boneOrder)
        boneDict = {}
        #for i in reader.mdlData.bones:
        #    boneDict[i.name.rstrip("\x00")] = i
        #print(boneDict)
        
        #for i in boneOrder:
        #    v = armatureBones[i.name]
        #    #tfm = boneDict[i.name].transform @ mathutils.Matrix.Translation(boneDict[i.name].pos)
        #    #tfmLoc, tfmRot, tfmSca = tfm.decompose()
        #    #v.head = boneDict[i.name].pos @ boneDict[i.name].transform
        #for i in boneOrder:
        #    #v = armatureBones[i.name]
        #    #if v.parent:
        #    #    v.head = v.head + v.parent.head
        #    #    v.tail = v.parent.head
            
        for i in boneOrder:
            if i.parent > -1:
                parent = reader.mdlData.bones[i.parent]
                invertedTfm = i.localTransform.inverted()
                invertedTfm.translation = i.pos
                i.localTransform = parent.localTransform @ invertedTfm
                #print("TRANSFORMS")
                #print(i.transform)
                #print(parent.transform)
                #print(i.localTransform)
            else:
                i.localTransform = mathutils.Matrix.Identity(4)
            i.localPos = i.localTransform.to_translation()
        
        for i in boneOrder:
            aBone = armatureBones[i.name]
            aBone.head = i.localPos
        for i in boneOrder:
            aBone = armatureBones[i.name]
            if len(aBone.children) == 1:
                aBone.tail = aBone.children[0].head
            elif len(aBone.children) > 1:
                averagePos = mathutils.Vector((0.0,0.0,0.0))
                for j in aBone.children:
                    averagePos = averagePos + j.head
                averagePos = averagePos / len(aBone.children)
                aBone.tail = averagePos
            else:
                aBone.length = 0.5
        
        
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        
        armatureBones = armature.bones
        
        
        bm = bmesh.new()
        mesh = bpy.data.meshes.new("Untitled FATE Object")
        #print(reader.mdlData.objectCount)
        #print(len(reader.mdlData.vertices))
        #print(len(reader.mdlData.triangles))
        for i in range(len(reader.mdlData.vertices)):
            #print("NEW VERTEX")
            vertexBones = reader.mdlData.vertices[i].bones
            vertexPosition = mathutils.Vector((0,0,0))
            for j in vertexBones:
                boneWeight = reader.mdlData.vertices[i].boneWeights[j]
                boneName = reader.mdlData.bones[j].name
                #print(boneName)
                bonePosLocal = reader.mdlData.bones[j].localPos
                boneTfmLocal = reader.mdlData.bones[j].localTransform
                #print(boneTfmLocal)
                boneOffset =  mathutils.Vector(reader.mdlData.vertices[i].boneOffsets[j])
                #print("WEIGHT " + str(boneWeight))
                boneOffset = boneTfmLocal @ boneOffset
                vertexPositionNew = boneOffset
                vertexPositionNew = vertexPositionNew * boneWeight
                #print(vertexPositionNew)
                vertexPosition = vertexPosition + vertexPositionNew
            if len(vertexBones) == 0:
                vertexPosition = rootBone.localPos
            vert = bm.verts.new( vertexPosition )
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        
        #print(reader.mdlData.tagUserData)
        
        for f in reader.mdlData.triangles:
            if bm.faces.get((bm.verts[f[0]], bm.verts[f[1]], bm.verts[f[2]])) == None:
                bm.faces.new((bm.verts[f[0]], bm.verts[f[1]], bm.verts[f[2]]))
        
        for i in range(len(reader.mdlData.uvs)):
            uv = reader.mdlData.uvs[i]
            reader.mdlData.vertices[i].uvPos.append(uv)
        
        uv_layer = bm.loops.layers.uv.verify()
        for f in bm.faces:
            for loop in f.loops:
                loop_uv = loop[uv_layer]
                currentVert = reader.mdlData.vertices[loop.vert.index]
                loop_uv.uv = currentVert.uvPos[0]
        
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()
        
        object_utils.object_data_add(context, mesh)
        #override = bpy.context.copy()
        override["object"] = mesh
        vGroups = bpy.context.object.vertex_groups
        
        for bone in reader.mdlData.bones:
            if vGroups.get(bone.name) == None:
                vGroups.new(name=bone.name)
        for v in range(len(mesh.vertices)):
            vertexIndex = v
            for boneIndex in reader.mdlData.vertices[vertexIndex].bones:
                boneWeight = reader.mdlData.vertices[vertexIndex].boneWeights[boneIndex]
                bone = reader.mdlData.bones[boneIndex]
                vGroups[boneIndex].add([vertexIndex], boneWeight, "REPLACE")
        
        
        #print(reader.mdlData.objectCount)
        #print(reader.mdlData.objectNames)
        return {'FINISHED'}
        
class ExportSMS(Operator, ExportHelper):
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
        f.write(writer.txtData)
        f.close()
        
        return {'FINISHED'}
