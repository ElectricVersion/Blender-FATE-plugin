import struct

UINT32 = {"format": "L", "size": 4}
SINT32 = {"format": "l", "size": 4}
UINT16 = {"format": "H", "size": 2}
SINT16 = {"format": "h", "size": 2}
FLOAT  = {"format": "f", "size": 4}

class Reader:
    filePosition = 0
    data = None
    
    def __init__(self, p_input):
        self.filePosition = 0
        self.data = p_input
        
    def read_num(self, p_type = UINT32):
        output = []
        for i in range (0, p_type["size"]):
            output.append(self.data[self.filePosition + i])
        
        self.filePosition += p_type["size"]
        output = struct.unpack(p_type["format"], bytes(output))[0]
        print("Read " + str(p_type["size"]) + " bytes: " + str(output))
        
        return output
        
    def read_str(self, p_delim = '\0'):
        output = ""
        currentChar = None
        while currentChar != p_delim:
            currentChar = bytes([self.data[self.filePosition]]).decode("utf-8")
            output += currentChar
            self.filePosition += 1
        print("Read string: " + output)
        return output
