import re, os.path, utils as ut, numbers, sys, copy

import .commands
import .fileformat

        

class GraphicalItem:
    def __init__(self, current_aperture):
        self.current_aperture=current_aperture
        self.items=[]
    
    def add(self, param_state, plotting_mode, item):
        self.items.append((param_state, plotting_mode, item))
    
    def __repr__(self):
        return f"GraphicalItem[aperture={self.current_aperture} {len(self.items)} items"

class GerberFile:
    @classmethod
    def from_file(filename):
        input_str = open(os.path.join(filename)).read()
        
        idx=0
        parts=[]
        
        for part in fileformat.iter_parts(input_str):
            
            if not isinstance(part, fileformat.Newline):
                part.command = commands.read_command(part.str)
                if str(part.command) != part.str:
                    raise Exception("read_command failed? ", part_str, command, str(command))
            
            parts.append(part)
                
        return GerberFile(filename, input_str, parts)
    
    def __init__(self, filename, input_str, parts):
        self.filename=filename
        self.input_str=input_str
        self.parts=parts
        
        self.analyze_parts()
    
    def analyze_parts(self):
        self.units=None
        self.num_digits=None
        
        param_state={'polarity':None,'mirroring':None,'rotation':None,'scaling':None}
        
        
        plotting_mode=None
        
        
        self.aperture_macros={}
        self.apertures={}
        
        self.graphical_items=[]
        
        curr_graphical_item = None
        
        for p in self.parts:
            if p.command:
                if isinstance(p.command, commands.Units):
                    self.units = 'mm' if p.command.units_mm else 'in'
                elif isinstance(p.command, commands.FormatSpec):
                    self.num_digits=p.command.num_digits
                elif isinstance(p.command, commands.LoadPolarity):
                    param_state['polarity']=p.command.polarity
                elif isinstance(p.command, commands.LoadMirroring):
                    param_state['mirroring']=p.command.mirroring
                elif isinstance(p.command, commands.LoadRotation):
                    param_state['rotation']=p.command.rotation
                elif isinstance(p.command, commands.LoadScaling):
                    param_state['scaling']=p.command.scaling
                elif isinstance(p.command, commands.PlotStateCommand):
                    if p.command.number=='01':
                        plotting_mode='Linear'
                    elif p.command.number=='02':
                        plotting_mode='ClockwiseArc'
                    elif p.command.number=='03':
                        plotting_mode='CounterClockwiseArc'
                    elif p.command.number=='75':
                        if not plotting_mode in ('ClockwiseArc','CounterClockwiseArc'):
                            print('PlotStateCommand[G75] when not in circual mode?')
                elif isinstance(p.command, commands.ApertureMacro):
                    self.aperture_macros[p.command.macro_name]=p.command
                elif isinstance(p.command, commands.ApertureDefinition):
                    self.apertures[p.command.ident]=p.command
                
                elif isinstance(p.command,commands.SetCurrentAperture):
                    if curr_graphical_item and curr_graphical_item.items:
                        self.graphical_items.append(curr_graphical_item)
                    
                    curr_graphical_item = GraphicalItem(p.command.ident)
                elif isinstance(p.command, commands.GraphicalOperation):
                    if not curr_graphical_item:
                        print("GraphicalOperation with no aperture set??", p)
                    
                    curr_graphical_item.add(param_state, plotting_mode, p.command)
                elif isinstance(p.command, commands.EndOfFile):
                    if curr_graphical_item and curr_graphical_item.items:
                        self.graphical_items.append(curr_graphical_item)
                        

def translate_gerber(gerberfile, x_offset, y_offset):
    new_parts=[]
    pos = 0
    for pt in gerberfile.parts:
        if isinstance(pt, fileformat.Newline):
            new_parts.append(Newline(pos))
            pos+=1
        elif not isinstance(pt.command, GraphicalOperation):
            new_part = copy.deepcopy(pt)
            ln = pt.end-pt.start
            new_part.start = pos
            new_part.end = pos+ln
            pos += ln
            new_parts.append(new_part)
            
        else:
            assert isinstance(pt, fileformat.Line)
            assert isinstance(pt.command, GraphicalOperation)
            
            type_ = pt.command.type
            x = None if pt.command.x is None else pt.command.x + x_offset
            y = None if pt.command.y is None else pt.command.y + y_offset
            i = pt.command.i
            j = pt.command.j
            
            new_command = GraphicalOperation(type_, x, y, i, j)
            new_command_str = str(new_command)
            new_part = Line(pos, pos+len(new_command_str), new_command_str, new_command)
            new_parts.append(new_part)
    
    
    return new_parts
                








    

