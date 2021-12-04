import struct
import math

UINT32 = {"format": "L", "size": 4}
SINT32 = {"format": "l", "size": 4}
UINT16 = {"format": "H", "size": 2}
SINT16 = {"format": "h", "size": 2}
FLOAT  = {"format": "f", "size": 4}
BYTE  = {"format": "b", "size": 1}

class VertexData:
    def __init__(self):
        self.references = []
        self.uvPos = []
        self.pos = None
        self.normals = []
        self.bones = []
        self.boneOffsets = {}
        self.boneWeights = {}

class BoneData:
    def __init__(self):
        self.parent = None
        self.name = ""
        self.transform = None
        self.pos = None
        self.localPos = None
        self.localTransform = None
        self.vertices = []
        self.vertexOffsets = []
        self.vertexWeights = []
        self.children = []

class ModelData: # used for both SMS and MDL files since they have similar formats
    def __init__(self):
        self.textureNames = {}
        self.materialNames = {}
        self.objectNames = []
        self.userData = {}
        self.uvs = []
        self.vertices = []
        self.triangles = []
        self.materials = []
        self.textures = []
        self.normals = []
        self.vertexColors = []
        self.uvReferences = []
        self.normalReferences = []
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
        
        #SMS stuff
        self.tagCount = 0
        self.version = ""
        self.tagNames = []
        self.tagUserData = []
        self.bones = []
        self.vertexDict = {}
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
        
    def read_block(self, p_len):
        output = ""
        currentChar = None
        for i in range(p_len):
            currentChar = bytes([self.txtData[self.filePosition]]).decode("utf-8")
            output += currentChar
            self.filePosition += 1
        print("Read block: " + output)
        return output

class Writer:
    def __init__(self, p_context):
        self.txtData = bytes([])
        self.context = p_context
        self.mdlData = ModelData()
        
    def write_num(self, p_input, p_type = UINT32, p_addr = -1):
        output = struct.pack(p_type["format"], p_input)
        if p_addr < 0:
            self.txtData += output
        else:
            sizeToReplace = p_type["size"]
            rewrittenData = self.txtData[0:p_addr]
            rewrittenData += output
            postData = self.txtData[p_addr+sizeToReplace:len(self.txtData)]
            rewrittenData += postData
            self.txtData = rewrittenData
        print("Wrote " + str(p_type["size"]) + " bytes: " + str(output))
    
    def write_str(self, p_input, term = True):
        if term:
            p_input += "\0"
        output = p_input.encode("utf-8")
        self.txtData += output
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
