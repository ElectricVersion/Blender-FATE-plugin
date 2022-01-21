from .util import *
import bpy
import bpy.types

def write_material_section(wtr):
    for i in range(len(wtr.mdl_data.textures)):
        #texture names
        texture_path = wtr.mdl_data.textures[i].image.filepath
        texture_path = texture_path.rsplit("/")[-1]
        wtr.write_str(texture_path)
        wtr.write_num(i) #texture id
    #materials
    for i in range(len(wtr.mdl_data.materials)):
        wtr.write_str(wtr.mdl_data.materials[i].name) # material name
        wtr.write_num(i) #material ID
        wtr.write_num(0) #double sided?
        wtr.write_num(1) #collision for this material?
        wtr.write_num(1) #rendering for this material?
        wtr.write_num(0) #userdata ID (still dont know what this means)
        wtr.write_num(0) #has_color_key?
        wtr.write_num(0) #has shifting behavior?
        wtr.write_num(0) #has flipbook behavior?
        wtr.write_num(0) #has shifting behavior_2?
        wtr.write_num(0) #has flipbook behavior_2?
        wtr.write_num(0) #render last?
        wtr.write_num(0) #render first?
        
        wtr.write_num(150, SINT16) #diffuse R
        wtr.write_num(150, SINT16) #diffuse G
        wtr.write_num(150, SINT16) #diffuse B
        
        wtr.write_num(150, SINT16) #ambient R
        wtr.write_num(150, SINT16) #ambient G
        wtr.write_num(150, SINT16) #ambient B
        
        wtr.write_num(229, SINT16) #specular R
        wtr.write_num(229, SINT16) #specular G
        wtr.write_num(229, SINT16) #specular B
    
        wtr.write_num(0, UINT16) #emissive R
        wtr.write_num(0, UINT16) #emissive G
        wtr.write_num(0, UINT16) #emissive B
        
        wtr.write_num(0.1, FLOAT) #shininess
        wtr.write_num(0.0, FLOAT) #shininess strength
        
        wtr.write_num(0, SINT32) #diffuse texture
        wtr.write_num(-1, SINT32) #opacity texture
        wtr.write_num(-1, SINT32) #reflect texture
        wtr.write_num(-1, SINT32) #illumination texture
        wtr.write_num(-1, SINT32) #bump texture
        wtr.write_num(-1, SINT32) #sphere texture
        wtr.write_num(-1, SINT32) #multiply texture
        