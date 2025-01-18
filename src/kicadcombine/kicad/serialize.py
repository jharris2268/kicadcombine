import json, os
from .sourcedesign import SourceDesign
from .placements import Placement
from .silkscreenline import SilkscreenLine

class SerializeError(Exception):
    def __init__(self, message, question=None):
        super().__init__()
        self.message=message
        self.question=question
        
    
        
        

def serialize_panel(panel, pathname):
        
    a,b=os.path.splitext(pathname)
    if b=='':
        pathname = pathname+'.json'
    
    elif b != '.json':
        raise SerializeError(f"design file should have extension '.json'")
        
    
    design = {
        'type': 'kicadcombine_design', 
        'source_designs': [],
        'placements': [],
        'silkscreen_lines': [],
        'output_filename': panel.output_filename,
        'board_size': None
    }
    sds=set()
    for placement in panel.placements:
        if not placement.design.name in sds:
            design['source_designs'].append({
                'name': placement.design.name, 
                'path': placement.design.path,
                'checksum': placement.design.checksum,
                'width': placement.design.width,
                'height': placement.design.height,
            })
        design['placements'].append({
            'source_design': placement.design.name,
            'x_pos': placement.x_pos,
            'y_pos': placement.y_pos,
            'angle': placement.angle
        })
    for panel in panel.silkscreen_lines:
        design['silkscreen_lines'].append({
            'x0': line.x0,
            'y0': line.y0,
            'x1': line.x1,
            'y1': line.y1,
            'width': line.width
        })
    
    if panel.board_size_type == 'specify':
        design['board_size'] = ['specify', panel.board_width, panel.board_height]
    else:
        design['board_size'] = [panel.board_size_type, None, None]
    
    json.dump(design, open(pathname, 'w'), indent=4)


def throw_exception(msg):
    raise SerializeError(msg)
    
    

def deserialize_panel(panel, pathname, allow_changes=False):
        
        if not os.path.exists(pathname):
            raise SerializeError(f"{pathname} does not exist")
            
        design=None
        try:
            design = json.load(open(pathname))
        except:
            raise SerializeError(f"file {pathname} not a json file")
            return
        
        wrong_format = lambda: throw_exception(f"file {pathname} not a kicadcombine json file")
        
        if not ('type' in design and 'source_designs' in design
                and 'placements' in design and 'silkscreen_lines' in design
                and 'board_size' in design and 'output_filename' in design):
            wrong_format()
            return 
        if not design['type']=='kicadcombine_design':
            wrong_format()
            return
        
        new_source_designs={}
        new_placements=[]
        new_silkscreen_lines=[]
        next_placement=panel.next_placement
        for sd in design['source_designs']:
            if not ('name' in sd and 'path' in sd and 'checksum' in sd and 'width' in sd and 'height' in sd):
                wrong_format()
                return
            if sd['name'] in panel.source_designs:
                existing_sd = panel.source_designs[sd['name']]
                
                if not sd['checksum']==existing_sd.checksum:
                    size_same = sd['height']==existing_sd.height and sd['width']==existing_sd.width
                
                    if not size_same and not allow_changes:
                        raise SerializeError(f"Source Design {sd['name']} changed, size {'same' if size_same else 'different'}", 'Allow Changes')
                
            else:
                if not os.path.exists(sd['path']):
                    raise Exception(f"Source Design {sd['path']} does not exist")
                    
                nsd = SourceDesign(sd['name'],sd['path'])
                if sd['checksum'] != nsd.checksum:
                    size_same = sd['height']==nsd.height and sd['width']==nsd.width
                
                    if not size_same and not allow_changes:
                        raise SerializeError(f"Source Design {sd['name']} changed, size {'same' if size_same else 'different'}", 'Allow Changes')
                        
                new_source_designs[nsd.name]=nsd
            
        for pl in design['placements']:
            if not ('source_design' in pl and 'x_pos' in pl and 'y_pos' in pl and 'angle' in pl):
                wrong_format()
                return
            
            pl_design=panel.source_designs.get(pl['source_design'])
            if not pl_design:
                pl_design=new_source_designs.get(pl['source_design'])
            if not pl_design:
                raise SerializeError(f"Source Design {pl['source_design']} not specified")
                return
            
            new_placements.append(Placement(next_placement, pl_design, pl['x_pos'], pl['y_pos'], pl['angle']))
            next_placement+=1
        for ln in design['silkscreen_lines']:
            if not ('x0' in ln and 'y0' in ln and 'x1' in ln and 'y1' in ln and 'width' in ln):
                wrong_format()
                return
            new_silkscreen_lines.append(SilkscreenLine(panel, ln['x0'], ln['y0'], ln['x1'], ln['y1'], ln['width']))
        
        panel.board_size_type, panel.board_width, panel.board_height = design['board_size']
        
        for n,sd in new_source_designs.items():
            panel.source_designs[n]=sd
        panel.placements.clear()
        for pl in new_placements:
            panel._placements[pl.idx]=pl
        panel.silkscreen_lines.clear()
        for ln in new_silkscreen_lines:
            panel.silkscreen_lines.append(ln)
        
        panel.next_placement=next_placement
        panel.output_filename = design['output_filename']
        panel.update_board_polygon()
        
