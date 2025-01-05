import re, os.path, numbers, copy


from . import commands
from . import fileformat
from .parsecommand import read_command
        

class GraphicalItem:
    def __init__(self, state=None):
        self.state = State() if state is None else copy.deepcopy(state) 
        
        self.items=[]
    
    def add(self, plotting_mode, item):
        self.items.append((plotting_mode, item))
    
    def __repr__(self):
        return f"GraphicalItem[aperture={self.state.aperture} {len(self.items)} items]"

    
    @property
    def params(self):
        return self.state.params

    @property
    def shapes(self):
        shapes=[]
        curr = []
        for a,b in self.items:
            #if a!='Linear':
                #raise Exception("arcs not impl")
                        
            if b.type=='D02':
                if curr:
                    shapes.append(('r' if self.state.in_region else 'l', curr))
                    curr=[]
            
            if a=='l':
                curr.append((a, (b.x or 0)*0.000001, (b.y or 0)*-0.000001))
            else:
                curr.append((a, (b.x or 0)*0.000001, (b.y or 0)*-0.000001, (b.i or 0)*-0.000001, (b.j or 0)*-0.000001))
            if b.type=='D03':
                shapes.append(('p',curr[0]))
                curr=[]
        if curr:
            shapes.append(('r' if self.state.in_region else 'l', curr))
        return shapes
    
class State:
    def __init__(self):
        self.aperture=None
        
        
        self.polarity=None
        #self.mirroring=None
        #self.rotation=None
        #self.scaling=None
        
        self.net_name = None
        self.pin_name = None
        self.comp_name = None
        self.in_region=False
    
    def __eq__(self, other):
        return isinstance(other, State) and self.params == other.params
    
    def check(self, gi):
        return self == gi
    
    @property
    def params(self):
        return dict((k,v) for k,v in self.__dict__.items() if not v is None)
    
class Aperture:
    def __init__(self, attributes, name, params):
        self.attributes = attributes
        self.name=name
        self.params=params
    def __repr__(self):
        return f"Aperture[{self.name} {{{' '.join('%s=%s' % (k,v) for k,v in self.attributes.items())}}} [{self.params}]]"
        

class GerberFile:
    @staticmethod
    def from_file(filename):
        input_str = open(os.path.join(filename)).read()
        
        idx=0
        parts=[]
        
        for part in fileformat.iter_parts(input_str):
            
            if not isinstance(part, fileformat.Newline):
                part.command = read_command(part.str)
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
        self.file_attributes={}
        state = State()
        plotting_mode=None
        
        curr_aperture_attrs={}
        
        self.aperture_macros={}
        self.apertures={}
        
        self.comments=[]
        
        self.graphical_items=[]
        
        curr_graphical_item = None
        
        for p in self.parts:
            if p.command:
                if isinstance(p.command, commands.Units):
                    self.units = 'mm' if p.command.units_mm else 'in'
                elif isinstance(p.command, commands.FormatSpec):
                    self.num_digits=p.command.num_digits
                    
                elif isinstance(p.command, commands.FileAttributes):
                    self.file_attributes[p.command.name]=p.command.values
                    
                elif isinstance(p.command, commands.LoadPolarity):
                    state.polarity=p.command.polarity
                #elif isinstance(p.command, commands.LoadMirroring):
                #    state.mirroring=p.command.mirroring
                #elif isinstance(p.command, commands.LoadRotation):
                #    state.rotation=p.command.rotation
                #elif isinstance(p.command, commands.LoadScaling):
                #    state.scaling=p.command.scaling
                
                
                elif isinstance(p.command, commands.PlotStateCommand):
                    if p.command.number=='01':
                        plotting_mode='l' #linear
                    elif p.command.number=='02':
                        plotting_mode='c' #clockwise
                    elif p.command.number=='03':
                        plotting_mode='a' #anticlockwise / counterclockwise
                    elif p.command.number=='75':
                        if not plotting_mode in ('c', 'a'):
                            print('PlotStateCommand[G75] when not in clockwise / counterclockwise arc mode?')
                
                elif isinstance(p.command, commands.ApertureAttributes):
                    curr_aperture_attrs[p.command.name]=p.command.values
                
                elif isinstance(p.command, commands.ApertureMacro):
                    self.aperture_macros[p.command.macro_name]=p.command
                elif isinstance(p.command, commands.ApertureDefinition):
                    self.apertures[p.command.ident]=Aperture(dict(curr_aperture_attrs.items()), p.command.template_name, p.command.template_params)
                
                elif isinstance(p.command, commands.RegionStateCommand):
                    if p.command.number=='36':
                        state.in_region=True
                        if curr_graphical_item.items:
                            self.graphical_items.append(curr_graphical_item)
                        curr_graphical_item = GraphicalItem(state)
                    elif p.command.number=='37':
                        state.in_region=False
                        if curr_graphical_item.items:
                            self.graphical_items.append(curr_graphical_item)
                        curr_graphical_item = GraphicalItem(state)
                
                elif isinstance(p.command,commands.SetCurrentAperture):
                    state.aperture = p.command.ident
                
                elif isinstance(p.command, commands.ObjectAttributes):
                    if p.command.name=='.P':
                        state.pin_name = p.command.values
                    if p.command.name=='.N':
                        state.net_name = p.command.values
                    if p.command.name=='.C':
                        state.comp_name = p.command.values
                
                elif isinstance(p.command, commands.DeleteAttributes):
                    if p.command.name=='.P' or p.command.name is None:
                        state.pin_name = None
                    if p.command.name=='.N' or p.command.name is None:
                        state.net_name = None
                    if p.command.name=='.C' or p.command.name is None:
                        state.comp_name = None
                    
                    if p.command.name is None:
                        curr_aperture_attrs = {}
                    elif p.command.name in curr_aperture_attrs:
                        del curr_aperture_attrs[p.command.name]
                        
                    
                elif isinstance(p.command, commands.GraphicalOperation):
                    if curr_graphical_item is None:
                        curr_graphical_item = GraphicalItem(state)
                    elif not state.check(curr_graphical_item.state):
                        if curr_graphical_item.items:
                            if state.in_region:
                                print("?? new item while in region")
                            
                            self.graphical_items.append(curr_graphical_item)
                            
                        curr_graphical_item = GraphicalItem(state)
                    
                    curr_graphical_item.add(plotting_mode, p.command)
                
                elif isinstance(p.command, commands.Comment):
                    self.comments.append(p.command.comment)
                
                
                elif isinstance(p.command, commands.EndOfFile):
                    if curr_graphical_item and curr_graphical_item.items:
                        self.graphical_items.append(curr_graphical_item)
                    
                else:
                    print('missing', p.command)
    
    def make_gerber_from_parts(self):
        result = fileformat.PartsList()
        #header
        for k,v in self.file_attributes.items():
            result.add(commands.FileAttributes('TF', k, v), True)
        
        result.add(commands.FormatSpec('FS', 4), True)
        result.add(commands.Units('MO',True), True)
        
        result.add(commands.LoadPolarity('LP', 'D'), True)
        result.add(commands.PlotStateCommand('G', '01'))
        
        #aperture macros
        result.add(commands.Comment('G04', " APERTURE LIST"))
        result.add(commands.Comment('G04', " Aperture macros list"))
        
        for k,v in sorted(self.aperture_macros.items()):
            result.add(commands.ApertureMacro('AM', k, v.macro_body), True)
        
        result.add(commands.Comment('G04', " Aperture macros list end"))
        for k,v in sorted(self.apertures.items()):
            if v.attributes:
                for p,q in sorted(v.attributes.items()):
                    result.add(commands.ApertureAttributes('TA',p,q),True)
                    
            result.add(commands.ApertureDefinition('AD', k, v.name, v.params), True)
            if v.attributes:
                result.add(commands.DeleteAttributes('TD'),True)
        
        result.add(commands.Comment('G04', " APERTURE END LIST"))
        
        curr_plot_mode='l'
        curr_state = State()
        curr_state.polarity='D'
        
        for gi in sorted(self.graphical_items, key=lambda p: p.state.aperture):
            if gi.state.aperture != curr_state.aperture:
                result.add(commands.SetCurrentAperture('D', gi.state.aperture))
                curr_state.aperture=gi.state.aperture
            if gi.state.polarity != curr_state.polarity:
                result.add(commands.LoadPolarity('LP', gi.state.polarity),True)
                curr_state.polarity=gi.state.polarity
            
            #if gi.state.mirroring != curr_state.mirroring:
            #    result.add(commands.LoadMirroring('LM', gi.state.mirroring))
            #    curr_state.polarity=gi.state.mirroring
            
            #if gi.state.rotation != curr_state.rotation:
            #    result.add(commands.LoadRotation('LR', gi.state.rotation))
            #    curr_state.rotation=gi.state.rotation
            
            #if gi.state.scaling != curr_state.scaling:
            #    result.add(commands.LoadScaling('LS', gi.state.scaling))
            #    curr_state.scaling=gi.state.scaling
            
            
            
            if gi.state.pin_name:
                result.add(commands.ObjectAttributes('TF', '.P', gi.state.pin_name),True)
            if gi.state.net_name:
                result.add(commands.ObjectAttributes('TF', '.P', gi.state.net_name),True)    
            if gi.state.comp_name:
                result.add(commands.ObjectAttributes('TF', '.C', gi.state.comp_name),True)
            
            if gi.state.in_region:
                result.add(commands.RegionStateCommand('G', '36'))
                result.add(copy.deepcopy(gi.items[0][1]))
                result.add(commands.PlotStateCommand('G', '01'))
                for p,q in gi.items[1:]:
                    if p!='l':
                        raise Exception("!!")
                    result.add(copy.deepcopy(q))
                result.add(commands.RegionStateCommand('G', '37'))
            else:
                for p,q in gi.items:
                    if p!=curr_plot_mode:
                        if p=='l':
                            result.add(commands.PlotStateCommand('G', '01'))
                        elif p=='c':
                            result.add(commands.PlotStateCommand('G', '02'))
                            result.add(commands.PlotStateCommand('G', '75'))
                        elif p=='a':
                            result.add(commands.PlotStateCommand('G', '03'))
                            result.add(commands.PlotStateCommand('G', '75'))
                        curr_plot_mode=p
                    result.add(copy.deepcopy(q))
                
            if gi.state.pin_name or gi.state.net_name or gi.state.comp_name:
                result.add(commands.DeleteAttributes('TD'),True)
        
        
        if curr_state.polarity != 'D':
            result.add(commands.LoadPolarity('LP', 'D'),True)
        
        #if curr_state.mirroring != 'N':
        #    result.add(commands.LoadMirroring('LM', 'N'),True)
        
        #if curr_state.rotation != None:
        #    result.add(commands.LoadRotation('LR', get_num('0')),True)
        
        #if curr_state.scaling != None:
        #    result.add(commands.LoadScaling('LS', get_num('0')),True)
        
        result.add(commands.EndOfFile('M02'))
        
        return result
        
        
        
        
    

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
                








    


