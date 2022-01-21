from .util import *

MATERIAL_STANDARD = 0
MATERIAL_PREALPHA = 1
MATERIAL_ALPHA = 2
MATERIAL_SHADOW = 3
MATERIAL_REFLECT = 4
MATERIAL_STATICCUBEMAP = 5
MATERIAL_ILLUMINATION = 6
MATERIAL_MULTIPLY = 7
MATERIAL_NORMALMAP = 8 
MATERIAL_SPHEREMAP = 9
MATERIAL_REFLECTPOST = 10
MATERIAL_STATICCUBEMAPPOST = 11
MATERIAL_SPHEREMAPPOST = 12
MATERIAL_TYPES = 13

def read_material_section(rdr):    
    material_references = {}
    material_has_color_key = {}
    material_color_key = {}
    material_is_double_sided = {}
    material_is_referenced = {}
    material_is_collideable = {}
    material_is_visible = {}
    material_type = {}
    
    # parse texture names
    for i in range(rdr.mdl_data.texture_count):
        texture_path = rdr.read_str().upper()
        texture_id = rdr.read_num(SINT32)
        rdr.mdl_data.texture_names[texture_id] = texture_path
    # load each material
    for i in range(rdr.mdl_data.material_count):
        duplicate = None
        opacity = None
        double_sided = None
        has_color_key = None
        render_last = None
        render_first	 = None
        data_i_D = None

        behavior_shifting = None
        behavior_flipbook = None
        flipbook_x_Frames = None
        flipbook_y_Frames = None
        shift_u = None
        shift_v = None
        flipbook_time = None

        behavior_shifting_2 = None
        behavior_flipbook_2 = None
        flipbook_x_Frames_2 = None
        flipbook_y_Frames_2 = None
        shift_u_2 = None
        shift_v_2 = None
        flipbook_time_2 = None

        rdr.mdl_data.material_names[i] = rdr.read_str()
        material_id = rdr.read_num(SINT32)
        double_sided = rdr.read_num(SINT32)
        material_is_collideable[material_id] = rdr.read_num(SINT32)
        material_is_visible[material_id] = rdr.read_num(SINT32)
        data_id = rdr.read_num(SINT32)
        
        has_color_key = rdr.read_num(SINT32)
        if has_color_key == 1:
            r = rdr.read_num(UINT16)
            g = rdr.read_num(UINT16)
            b = rdr.read_num(UINT16)
            material_color_key[material_id] = [r, g, b]
        
        behavior_shifting = rdr.read_num(SINT32)
        if behavior_shifting == 1:
            shift_u = rdr.read_num(FLOAT)
            shift_v = rdr.read_num(FLOAT)
        
        behavior_flipbook = rdr.read_num(SINT32)
        if behavior_flipbook == 1:
            flipbook_x_Frames = rdr.read_num(SINT16)
            flipbook_y_Frames = rdr.read_num(SINT16)
            flipbook_time = rdr.read_num(FLOAT)
            
        # second layer
        behavior_shifting_2 = rdr.read_num(SINT32)
        if behavior_shifting_2 == 1:
            shift_u_2 = rdr.read_num(FLOAT)
            shift_v_2 = rdr.read_num(FLOAT)
        
        behavior_flipbook_2 = rdr.read_num(SINT32)
        if behavior_flipbook_2 == 1:
            flipbook_x_Frames_2 = rdr.read_num(SINT16)
            flipbook_y_Frames_2 = rdr.read_num(SINT16)
            flipbook_time_2 = rdr.read_num(FLOAT)
        
        render_last = rdr.read_num(SINT32)
        render_first = rdr.read_num(SINT32)
            
        diffuse_r = rdr.read_num(SINT16) / 255.0
        diffuse_g = rdr.read_num(SINT16) / 255.0
        diffuse_b = rdr.read_num(SINT16) / 255.0
        
        ambient_r = rdr.read_num(SINT16) / 255.0
        ambient_g = rdr.read_num(SINT16) / 255.0
        ambient_b = rdr.read_num(SINT16) / 255.0

        specular_r = rdr.read_num(SINT16) / 255.0
        specular_g = rdr.read_num(SINT16) / 255.0
        specular_b = rdr.read_num(SINT16) / 255.0
        
        emissive_r = rdr.read_num(SINT16) / 255.0
        emissive_g = rdr.read_num(SINT16) / 255.0
        emissive_b = rdr.read_num(SINT16) / 255.0
        
        shininess = rdr.read_num(FLOAT)
        shininess_strength = rdr.read_num(FLOAT)
        
        material_type[material_id] = MATERIAL_STANDARD
        
        diffuse_map_id = rdr.read_num(SINT32)
        opacity_map_id = rdr.read_num(SINT32)
        reflection_map_id = rdr.read_num(SINT32)
        illumination_map_id = rdr.read_num(SINT32)
        bump_map_id = rdr.read_num(SINT32)
        sphere_map_id = rdr.read_num(SINT32)
        multiply_map_id = rdr.read_num(SINT32)
        
        material_references[material_id] = None
        material_object = None
        
        diffuse_map_path = None
        opacity_map_path = None
        reflection_map_path = None
        illumination_map_path = None
        normall_map_path = None
        sphere_map_path = None
        multiply_map_path = None
        
        material_type[material_id] = MATERIAL_STANDARD
        material_is_referenced[material_id] = False
        
        #I skipped this section for now
        #it assembles texture paths or something
        
        #skip to parsing objects