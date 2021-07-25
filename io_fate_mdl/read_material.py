from io_fate_mdl.util import *

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
    materialReferences = {}
    materialHasColorKey = {}
    materialColorKey = {}
    materialIsDoubleSided = {}
    materialIsReferenced = {}
    materialIsCollideable = {}
    materialIsVisible = {}
    materialType = {}
    
    # parse texture names
    for i in range(rdr.mdlData.textureCount):
        texturePath = rdr.read_str().upper()
        textureId = rdr.read_num(SINT32)
        rdr.mdlData.textureNames[textureId] = texturePath
    # load each material
    for i in range(rdr.mdlData.materialCount):
        duplicate = None
        opacity = None
        doubleSided = None
        hasColorKey = None
        renderLast = None
        renderFirst	 = None
        dataID = None

        behaviorShifting = None
        behaviorFlipbook = None
        flipbookXFrames = None
        flipbookYFrames = None
        shiftU = None
        shiftV = None
        flipbookTime = None

        behaviorShifting2 = None
        behaviorFlipbook2 = None
        flipbookXFrames2 = None
        flipbookYFrames2 = None
        shiftU2 = None
        shiftV2 = None
        flipbookTime2 = None

        rdr.mdlData.materialNames[i] = rdr.read_str()
        materialId = rdr.read_num(SINT32)
        doubleSided = rdr.read_num(SINT32)
        materialIsCollideable[materialId] = rdr.read_num(SINT32)
        materialIsVisible[materialId] = rdr.read_num(SINT32)
        dataId = rdr.read_num(SINT32)
        
        hasColorKey = rdr.read_num(SINT32)
        if hasColorKey == 1:
            r = rdr.read_num(UINT16)
            g = rdr.read_num(UINT16)
            b = rdr.read_num(UINT16)
            materialColorKey[materialId] = [r, g, b]
        
        behaviorShifting = rdr.read_num(SINT32)
        if behaviorShifting == 1:
            shiftU = rdr.read_num(FLOAT)
            shiftV = rdr.read_num(FLOAT)
        
        behaviorFlipbook = rdr.read_num(SINT32)
        if behaviorFlipbook == 1:
            flipbookXFrames = rdr.read_num(SINT16)
            flipbookYFrames = rdr.read_num(SINT16)
            flipbookTime = rdr.read_num(FLOAT)
            
        # second layer
        behaviorShifting2 = rdr.read_num(SINT32)
        if behaviorShifting2 == 1:
            shiftU2 = rdr.read_num(FLOAT)
            shiftV2 = rdr.read_num(FLOAT)
        
        behaviorFlipbook2 = rdr.read_num(SINT32)
        if behaviorFlipbook2 == 1:
            flipbookXFrames2 = rdr.read_num(SINT16)
            flipbookYFrames2 = rdr.read_num(SINT16)
            flipbookTime2 = rdr.read_num(FLOAT)
        
        renderLast = rdr.read_num(SINT32)
        renderFirst = rdr.read_num(SINT32)
            
        diffuseR = rdr.read_num(SINT16) / 255.0
        diffuseG = rdr.read_num(SINT16) / 255.0
        diffuseB = rdr.read_num(SINT16) / 255.0
        
        ambientR = rdr.read_num(SINT16) / 255.0
        ambientG = rdr.read_num(SINT16) / 255.0
        ambientB = rdr.read_num(SINT16) / 255.0

        specularR = rdr.read_num(SINT16) / 255.0
        specularG = rdr.read_num(SINT16) / 255.0
        specularB = rdr.read_num(SINT16) / 255.0
        
        emissiveR = rdr.read_num(SINT16) / 255.0
        emissiveG = rdr.read_num(SINT16) / 255.0
        emissiveB = rdr.read_num(SINT16) / 255.0
        
        shininess = rdr.read_num(FLOAT)
        shininessStrength = rdr.read_num(FLOAT)
        
        materialType[materialId] = MATERIAL_STANDARD
        
        diffuseMapId = rdr.read_num(SINT32)
        opacityMapId = rdr.read_num(SINT32)
        reflectionMapId = rdr.read_num(SINT32)
        illuminationMapId = rdr.read_num(SINT32)
        bumpMapId = rdr.read_num(SINT32)
        sphereMapId = rdr.read_num(SINT32)
        multiplyMapId = rdr.read_num(SINT32)
        
        materialReferences[materialId] = None
        materialObject = None
        
        diffuseMapPath = None
        opacityMapPath = None
        reflectionMapPath = None
        illuminationMapPath = None
        normallMapPath = None
        sphereMapPath = None
        multiplyMapPath = None
        
        materialType[materialId] = MATERIAL_STANDARD
        materialIsReferenced[materialId] = False
        
        #I skipped this section for now
        #it assembles texture paths or something
        
        #skip to parsing objects