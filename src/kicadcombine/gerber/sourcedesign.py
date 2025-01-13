from kicadcombine.utils import Bounds
from . import GerberFile
from .drillformat import DrillFile

import os.path

GERBER_EXTENSIONS = [
    '.drl',
    '.gbl','.gbs','.gbp','.gbo',
    '.gtl','.gts','.gtp','.gto',
    '.gm1',
    '.g1','.g2','.g3','.g4','.g5','.g6','.g7','.g8']


def check_for_gerber_files(path):
    
    for fl in os.listdir(path):
        a,b = os.path.splitext(fl)
        if b in GERBER_EXTENSIONS:
            return True
    
    return False
    
    

class SourceDesign:
    
    @staticmethod
    def from_path(pathname):
        
        
        
        fns = [fl for fl in os.listdir(pathname) if os.path.splitext(fl)[1] in GERBER_EXTENSIONS]
        if not fns:
            raise Exception("no gerber files")
            
        root_pos=None
        if len(fns)==1:
            
            root_pos = fns[0].rfind('-')
        else:
            root_pos = max(x for x in range(len(fns[0]))  if all(f.startswith(fns[0][:x]) for f in fns))
            if root_pos>1 and fns[0][root_pos-1]=='-':
                root_pos-=1        

        name = fns[0][:root_pos]
        
        parts = {}
        for f in fns:
            fn,fe = os.path.splitext(f)
            lyr_name = fn[root_pos+1:]
            if fe=='.drl':
                parts[lyr_name] = DrillFile.from_file(os.path.join(pathname, f))
            else:
                parts[lyr_name] = GerberFile.from_file(os.path.join(pathname, f))
            
        
        return SourceDesign(pathname, name, parts)
        
               
        
    
    
    def __init__(self, source_dir, name, parts):
        self.source_dir = source_dir
        self.name=name
        self.parts = parts
        
        if 'Edge_Cuts' in self.parts:
            self.bounding_box = self.parts['Edge_Cuts'].find_bounds()
        
        else:
            self.bounding_box = Bounds()
            for _,part in self.parts.items():
                if isinstance(part, GerberFile):
                    self.bounding_box.expand_bounds(part.find_bounds())
        
        self.left = self.bounding_box.min_x / 1_000_000
        self.top = -self.bounding_box.max_y / 1_000_000
        
        self.width = self.bounding_box.width / 1_000_000
        self.height = self.bounding_box.height / 1_000_000
        
    
    @property
    def has_edge_cuts(self):
        return 'Edge_Cuts' in self.parts
    
    @property
    def has_f_paste(self):
        return 'F_Paste' in self.parts
    
    @property
    def num_copper_layers(self):
        return sum(1 for lyr in self.parts if lyr.endswith('Cu'))
    
    
    def __repr__(self):
        return f"SourceDesign[{self.name} {len(self.parts)} layers, {self.num_copper_layers} copper {self.width}mm x {self.height}mm]"
