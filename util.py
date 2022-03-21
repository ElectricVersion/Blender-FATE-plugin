import struct
import math
import mathutils

UINT32 = {"format": "<L", "size": 4}
SINT32 = {"format": "<l", "size": 4}
UINT16 = {"format": "<H", "size": 2}
SINT16 = {"format": "<h", "size": 2}
FLOAT  = {"format": "<f", "size": 4}
BYTE  = {"format": "b", "size": 1}

class Vertex_Data:
    def __init__(self):
        self.references = []
        self.uv_pos = []
        self.pos = None
        self.normals = []
        self.bones = []
        self.bone_offsets = {}
        self.bone_weights = {}

class Bone_Data:
    def __init__(self):
        self.parent = None
        self.name = ""
        self.transform = None
        self.pos = None
        self.local_pos = None
        self.local_transform = None
        self.vertices = []
        self.vertex_offsets = []
        self.vertex_weights = []
        self.children = []

class Model_Data: # used for both SMS and MDL files since they have similar formats
    def __init__(self):
        self.texture_names = {}
        self.material_names = {}
        self.object_names = []
        self.user_data = {}
        self.uvs = []
        self.vertices = []
        self.triangles = []
        self.materials = []
        self.textures = []
        self.normals = []
        self.vertex_colors = []
        self.uv_references = []
        self.normal_references = []
        self.vertex_references = []
        
        self.active_object = None
        self.active_mesh = None
        
        self.model_scale = 1.0
        self.object_count = 0
        self.lights_count = 0
        self.points_count = 0
        self.paths_count = 0
        self.material_count = 0
        self.texture_count = 0
        self.total_vertex_count = 0
        self.total_face_count = 0
        
        #SMS stuff
        self.tag_count = 0
        self.version = ""
        self.tag_names = []
        self.tag_user_data = []
        self.bones = []
        self.vertex_dict = {}
        return

class Reader:
    def __init__(self, p_input):
        self.file_position = 0
        self.txt_data = p_input
        self.mdl_data = Model_Data()
        self.show_logs = True
        
    def read_num(self, p_type = UINT32):
        output = []
        for i in range(p_type["size"]):
            output.append(self.txt_data[self.file_position + i])
        
        self.file_position += p_type["size"]
        output = struct.unpack(p_type["format"], bytes(output))[0]
        if self.show_logs:
            print("Read " + str(p_type["size"]) + " bytes: " + str(output))
        return output
        
    def read_str(self, p_delim = '\0'):
        output = ""
        current_char = None
        while current_char != p_delim:
            current_char = bytes([self.txt_data[self.file_position]]).decode("utf-8")
            output += current_char
            self.file_position += 1
        if self.show_logs:
            print("Read string:", output)
        return output
        
    def read_block(self, p_len):
        output = ""
        current_char = None
        for i in range(p_len):
            current_char = bytes([self.txt_data[self.file_position]]).decode("utf-8")
            output += current_char
            self.file_position += 1
        print("Read block: " + output + "(len", len(output), ")")
        return output

class Writer:
    def __init__(self, p_context):
        self.txt_data = [] #bytes([])
        self.pos = 0 #position in txt_data in bytes
        self.context = p_context
        self.mdl_data = Model_Data()
    
    def FILE_END(self):
        return len(self.txt_data)
    
    def extend(self, p_len):
        self.txt_data += [0 for i in range(p_len)]
    
    def seek(self, p_pos):
        if p_pos > self.FILE_END():
            self.extend(p_pos - self.FILE_END())
        self.pos = p_pos
    
    def write(self, p_content):
        self.txt_data[self.pos:self.pos+(len(p_content))] = p_content
        self.pos += len(p_content)
    
    def write_num(self, p_input, p_type = UINT32):
        print("Writing ", p_input)
        output = struct.pack(p_type["format"], p_input)
        #if self.pos == self.FILE_END():
        #    self.extend(len(output))
        self.write(output)
        print("Wrote " + str(p_type["size"]) + " bytes: " + str(list(output)))
    
    def write_str(self, p_input, term = True):
        if term:
            p_input += '\0'
        output = p_input.encode("utf-8")
        self.write(list(output))
        print("Wrote string: " + str(output) + " of length", len(output))
        
def compress_normal(p_x, p_y, p_z):
    multiplier = (3.14159 / 255.0) * 2.0
    alpha = math.acos(p_y)
    AU = math.floor(alpha / multiplier)
    beta = math.acos(p_x / math.sin(alpha))
    AV = math.floor(beta / multiplier)
    return AU, AV

def decompress_normal(AU, AV):
    multiplier = (3.14159 / 255.0) * 2.0 # convert from 0-255 to radians
    alpha = AU * multiplier
    beta = AV * multiplier
    x = math.cos(beta) * math.sin(alpha)
    y = math.cos(alpha)
    z = math.sin(beta) * math.sin(alpha)
    return x, y, z

def approx(p_input, p_precision = 0.02):
    rounded_input = round(p_input)
    if abs(rounded_input - p_input) < p_precision:
        return rounded_input
    return p_input

#def sort_vector(p_bone_vec):
#    vec = p_bone_vec.to_tuple()
#    absvec = (abs(vec[0]), abs(vec[1]), abs(vec[2]))
#    x, y, z = 0,0,0
#    y = vec[abs_vec.index(max(absvec))]

def get_axis(p_vector):
    vec = p_vector.to_tuple()
    axis = vec.index(max(vec))
    return axis

#def convert_matrix(p_matrix):
#    mat_list = [[col for col in row] for row in p_matrix.row]
#    mat_list[0:2] = mat_list[1::-1]
#    return mathutils.Matrix(mat_list)
    

##this class is meant to allow for easy conversions between two
##-sets of values, e.g names to indices, and vice versa.
##-this way they can be accessed by either
#class Double_Dict:
#    def __init__(self, p_id1=1, p_id2=2):
#        self.id1 = p_id1
#        self.id2 = p_id2
#        self.dict1 = {}
#        self.dict2 = {}
#    def get_item(self, p_dict_id, p_item_key):
#        if p_dict_id == self.id1:
#            return self.dict2[p_item_key]
#        elif p_dict_id == self.id2:
#            return self.dict1[p_item_key]
#        else:
#            return None
#    def set_item(self, p_value1, p_value2):
#        self.dict1[p_value2] = p_value1
#        self.dict2[p_value1] = p_value2
#