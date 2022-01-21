import struct
import math

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
        
    def read_num(self, p_type = UINT32):
        output = []
        for i in range(p_type["size"]):
            output.append(self.txt_data[self.file_position + i])
        
        self.file_position += p_type["size"]
        output = struct.unpack(p_type["format"], bytes(output))[0]
        print("Read " + str(p_type["size"]) + " bytes: " + str(output))
        
        return output
        
    def read_str(self, p_delim = '\0'):
        output = ""
        current_char = None
        while current_char != p_delim:
            current_char = bytes([self.txt_data[self.file_position]]).decode("utf-8")
            output += current_char
            self.file_position += 1
        print("Read string: " + output)
        return output
        
    def read_block(self, p_len):
        output = ""
        current_char = None
        for i in range(p_len):
            current_char = bytes([self.txt_data[self.file_position]]).decode("utf-8")
            output += current_char
            self.file_position += 1
        print("Read block: " + output)
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
        self.txt_data[self.pos:self.pos+len(p_content)] = p_content
        self.pos += len(p_content)
    
    def write_num(self, p_input, p_type = UINT32):
        output = struct.pack(p_type["format"], p_input)
        if self.pos == self.FILE_END():
            self.extend(len(output))
        self.write(list(output))
        print("Wrote " + str(p_type["size"]) + " bytes: " + str(output))
    
    
    def write_str(self, p_input, term = True):
        if term:
            p_input += "\0"
        output = p_input.encode("utf-8")
        self.write(list(output))
        print("Wrote string: " + str(output))
        
def compress_normal(p_x, p_y, p_z):
    multiplier = (3.14159 / 255.0) * 2.0
    alpha = math.acos(p_y)
    AU = math.floor(alpha / multiplier)
    beta = math.asin(p_z / math.sin(alpha))
    AV = math.floor(beta / multiplier)
    return AU, AV

def decompress_normal(AU, AV):
    multiplier = 3.14159 / 255.0 # convert from 0-255 to radians
    alpha = AU * 2.0 * multiplier
    beta = AV * 2.0 * multiplier
    x = math.cos(beta) * math.sin(alpha)
    y = math.cos(alpha)
    z = math.sin(beta) * math.sin(alpha)
    return x, y, z
