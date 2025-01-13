import re
from .utils import next_name

class Hole:
    def __init__(self, lineno,drill, x, y):
        self.lineno=lineno
        self.drill=drill
        self.x=x
        self.y=y
    def __repr__(self):
        return f"Hole[{self.lineno} {self.drill} X{self.x:0.5f} Y{self.y:0.5f}"

    def merge(self, drill_renames, x_offset, y_offset):
        return Hole(None, drill_renames[self.drill], self.x+x_offset, self.y+y_offset)

    def __str__(self):
        return f"X{self.x:0.5f}Y{self.y:0.5f}"    

class Slot:
    def __init__(self, lineno,drill, x, y, x2, y2):
        self.lineno=lineno
        self.drill=drill
        self.x=x
        self.y=y
        self.x2=x2
        self.y2=y2
    def __repr__(self):
        return f"Slot[{self.lineno} {self.drill} X{self.x:0.5f} Y{self.y:0.5f} to X{self.x2:0.5f} Y{self.y2:0.5f}"
        
    def merge(self, drill_renames, x_offset, y_offset):
        return Slot(None, drill_renames[self.drill], self.x+x_offset, self.y+y_offset, self.x2+x_offset, self.y2+y_offset)
    
    def __str__(self):
        return f"X{self.x:0.5f}Y{self.y:0.5f}G85X{self.x2:0.5f}Y{self.y2:0.5f}"    

class DrillSpec:
    def __init__(self, lineno, name, params):
        self.lineno=lineno
        self.name=name
        self.params=params
    
    def __repr__(self):
        return f"DrillSpec[{self.lineno} {self.name} params: {self.params}]"
    
    def __str__(self):
        return f"{self.name}{self.params}"
class DrillFile:
    
    def __init__(self, filename):
        self.filename=filename
        self.comments = []
        self.units = None
        self.drill_spec = {}
        self.holes = {}
    
    def __repr__(self):
        return f"DrillFile[{self.filename} {self.units} num_drills={len(self.drill_spec)}, num_holes={len(self.holes)}]"
    
    
    @staticmethod
    def from_file(filename):


        drillfile = DrillFile(filename)
        
        has_m48=False
        
        has_percent=False
        
        fmat = None
        
        
        curr_drill=None
        
        for i,lnx in enumerate(open(filename)):
            ln=lnx.rstrip()
            if ln.startswith('; '):
                drillfile.comments.append((i, ln[2:]))
                
            elif ln=='M48':
                has_m48=True
            elif ln.startswith('FMAT'):
                if ln!='FMAT,2':
                    raise Exception("expected FMAT,2")
            
            elif ln in ('INCH','METRIC'):
                drillfile.units = ln
            
            elif ln.startswith('T'):
                if not has_percent:
                    pp=re.match('^(T\d+)(.+)$', ln)
                    if not pp:
                        raise Exception("expected drill spec (T/d+)([spec])")
                    drill,spec = pp.groups()
                    drillfile.drill_spec[drill] = DrillSpec(i,drill, spec)
                else:
                    pp=re.match('^(T\d+)$', ln)
                    if not pp:
                        raise Exception("expected drill name (T/d+)")
                    drill,=pp.groups()
                    if not drill in drillfile.drill_spec:
                        raise Exception("drill %s not specified?" % drill)
                    curr_drill = drill
                    
            elif ln in ('G90','G05'):
                #???
                pass
            elif ln =='%':
                has_percent=True
            
            elif ln.startswith('X'):
                if curr_drill is None:
                    raise Exception("no drill set?")
                pp = re.match('^X(\-?[0-9]+(\.[0-9]+)?)Y(\-?[0-9]+(\.[0-9]+)?)(G85X(\-?[0-9]+(\.[0-9]+)?)Y(\-?[0-9]+(\.[0-9]+)?))?$', ln)
                if not pp:
                    raise Exception("expected X[number]Y[number]", ln)
                
                ppg=pp.groups()
                if not len(ppg) in (4,9):
                    raise Exception("??", ppg)
                
                
                x=float(ppg[0])
                y=float(ppg[2])
                if ppg[5] is None:
                    
                    drillfile.add_hole(Hole(i,curr_drill, x, y))
                else:
                    x2=float(ppg[5])
                    y2=float(ppg[7])
                    drillfile.add_hole(Slot(i,curr_drill, x, y, x2, y2))
                
            elif ln=='M30':
                #end of file
                pass
            else:
                raise Exception("unexpected line ", ln)
    
    
        return drillfile
    
    def add_hole(self, hole):
        if not hole.drill in self.holes:
            if not hole.drill in self.drill_spec:
                raise Exception(f"unknown drill {hole.drill}")
            
            self.holes[hole.drill]=[]
        
        self.holes[hole.drill].append(hole)


    def merge(self, other, x_offset, y_offset):
        
        if other.units != self.units:
            raise Exception("different units")
            
        drill_renames={}
        for _, ds in other.drill_spec.items():
            found=False
            for _,cd in self.drill_spec.items():
                if ds.params == cd.params:
                    drill_renames[ds.name] = cd.name
                    found=True
            if not found:
                new_name=next_name(self.drill_spec, 'T')
                new_drill_spec = DrillSpec(None, new_name, ds.params)
                self.drill_spec[new_name]=new_drill_spec
                drill_renames[ds.name] = new_name
        
        for k,v in other.holes.items():
            for hh in v:
                nhh = hh.merge(drill_renames, x_offset, y_offset)
                self.add_hole(nhh)
            
            
        
        
    def to_str(self):
        
        drill_order = sorted(self.drill_spec, key=lambda x: int(x[1:]))
        
        result = []
        result.append('M48')
        result.append('FMAT,2')
        result.append(self.units)
        
        for d in drill_order:
            result.append(str(self.drill_spec[d]))
        
        result.append('%')
        result.append('G90')
        result.append('G05')
        
        for drill in drill_order:
            result.append(drill)
            for hole in self.holes[drill]:
                result.append(str(hole))
        
        
        result.append('M30')
        return "\n".join(result)
                
        
def merge_drillfiles(output_prfx, spec):
    is_npth = spec[0][0].filename.endswith('-NPTH.drl')
    is_pth = spec[0][0].filename.endswith('-PTH.drl')
    if is_pth==is_npth:
        raise Exception("??")
    ext = '-NPTH.drl' if is_npth else '-PTH.drl'
    output = DrillFile(output_prfx + ext)
    output.units='METRIC'
    
    for df, x_offset, y_offset in spec:
        output.merge(df, x_offset, -y_offset)
    
    return output
