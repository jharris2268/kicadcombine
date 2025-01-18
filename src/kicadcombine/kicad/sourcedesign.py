import os.path

import pcbnew
import shapely as shp
import shapely.ops as sop

from .bounds import Bounds
from kicadcombine.utils import sha256_digest
from .boardoutline import find_board_outline_polygon

def get_kicad_pcb(dir):
    count=0
    if not os.path.exists(dir):
        raise Exception(f"path {dir} does not exist")


    
    if os.path.isdir(dir):
    
        for a,b,cc in os.walk(dir):
            for c in cc:
                d,e=os.path.splitext(c)
                if e=='.kicad_pcb':
                    yield d, os.path.join(a,c)
                    count+=1
    else:   
        a,c=os.path.split(dir)
        d,e=os.path.splitext(c)
        if e=='.kicad_pcb':
            yield d, dir
            count+=1
        else:
            raise Exception(f"expected {dir} to have extension .kicad_pcb")
        
        
    if not count:
        raise Exception(f"no kicad_pcb files in {dir}")
        
def open_source_designs(designs, dirs):
    
    duplicates=[]
    for d in dirs:
        for x,y in get_kicad_pcb(d):
            if x in designs:
                duplicates.append((x,y))
            else:
                designs[x] = SourceDesign(x, y)
            print(designs[x])
    return duplicates

class SourceDesign:
    
    
        
    
    def __init__(self, name, path):
        self.name=name
        self.path=path
        self.checksum = sha256_digest(path)
        self.board = pcbnew.LoadBoard(path)
        
        self.board_outline, self.offset = find_board_outline_polygon(self.board)
        self.bounds=Bounds(self.board_outline.bounds)
    
    
    @property
    def width(self):
        return self.bounds.width
    
    @property
    def height(self):
        return self.bounds.height
        
    @property
    def has_f_paste(self):
        return True
    
    @property
    def num_copper_layers(self):
        return self.board.GetCopperLayerCount()
    
    def get_board_outline(self, x_pos, y_pos, angle):
        poly = self.board_outline
        if angle:
            if angle == 90:
                poly = sop.transform(lambda x,y: [y,x], poly)
            elif angle == 180:
                max_x, max_y = self.bounds.max_x, self.bounds.max_y
                poly = sop.transform(lambda x,y: [max_x-x,max_y-y], poly)
            elif angle in (-90,270):
                max_x, max_y = self.bounds.max_x, self.bounds.max_y
                poly = sop.transform(lambda x,y: [max_y-y,max_x-x], poly)
            else:
                raise Exception("angle must be 0,90,180 or 270 degrees")
        
        return sop.transform(lambda x,y: [x+x_pos, y+y_pos], poly)
    
    def __repr__(self):
        return f"SourceDesign[{self.name}: {self.bounds.width:0.1f}mm x {self.bounds.height:0.1f}mm]"
