from io_fate_mdl.util import *

def write_basic_info(wtr):
    wtr.write_num(1.0, FLOAT) #model scale
    wtr.write_num(1, UINT32) #objects count (for now only one object can be exported per file)
    wtr.write_num(0, UINT32) #lights count
    wtr.write_num(0, UINT32) #points count
    wtr.write_num(0, UINT32) #paths count
    
    activeObject = wtr.context.active_object
    materialSlots = activeObject.material_slots.values()
    
    for i in materialSlots:
        material = i.material
        
    wtr.write_num(len(materials), UINT32) #materials count
    wtr.write_num(1, UINT32) #textures count