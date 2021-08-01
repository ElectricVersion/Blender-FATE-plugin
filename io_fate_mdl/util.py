import struct
import math

UINT32 = {"format": "L", "size": 4}
SINT32 = {"format": "l", "size": 4}
UINT16 = {"format": "H", "size": 2}
SINT16 = {"format": "h", "size": 2}
FLOAT  = {"format": "f", "size": 4}
BYTE  = {"format": "B", "size": 1}

class VertexData:
    def __init__(self):
        self.references = []
        self.uvPos = []
        self.pos = None

class ModelData:
    def __init__(self):
        self.textureNames = {}
        self.materialNames = {}
        self.userData = {}
        self.uvs = []
        self.vertices = []
        self.triangles = []
        self.materials = []
        self.textures = []
        self.normals = []
        self.vertexColors = []
        self.uvReferences = []
        self.vertexReferences = []
        
        self.activeObject = None
        
        self.modelScale = 1.0
        self.objectCount = 0
        self.lightsCount = 0
        self.pointsCount = 0
        self.pathsCount = 0
        self.materialCount = 0
        self.textureCount = 0
        self.totalVertexCount = 0
        self.totalFaceCount = 0
        return

class Reader:
    def __init__(self, p_input):
        self.filePosition = 0
        self.txtData = p_input
        self.mdlData = ModelData()
        
    def read_num(self, p_type = UINT32):
        output = []
        for i in range(p_type["size"]):
            output.append(self.txtData[self.filePosition + i])
        
        self.filePosition += p_type["size"]
        output = struct.unpack(p_type["format"], bytes(output))[0]
        print("Read " + str(p_type["size"]) + " bytes: " + str(output))
        
        return output
        
    def read_str(self, p_delim = '\0'):
        output = ""
        currentChar = None
        while currentChar != p_delim:
            currentChar = bytes([self.txtData[self.filePosition]]).decode("utf-8")
            output += currentChar
            self.filePosition += 1
        print("Read string: " + output)
        return output

class Writer:
    def __init__(self, p_context):
        self.txtData = bytes([])
        self.context = p_context
        self.mdlData = ModelData()
        
    def write_num(self, p_input, p_type = UINT32):
        output = struct.pack(p_type["format"], p_input)
        self.txtData += output
        print("Wrote " + str(p_type["size"]) + " bytes: " + str(output))
    
    def write_str(self, p_input):
        p_input += "\0"
        output = p_input.encode("utf-8")
        self.txtData += output
        print("Wrote string: " + str(output))
        
def compress_normal(p_normal, component):
    multiplier = (3.14159 / 255.0) * 2.0
    if component == 0: #x
        return round(math.asin(p_normal)/multiplier) 
    if component == 1: # z
        return 127 - round(math.atan(p_normal)/multiplier) # = AV
    if component == 2: #y
        return round(math.acos(p_normal)/multiplier) # = AU
    return 0