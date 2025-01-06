import re, os.path, numbers, copy


from . import commands
from . import fileformat
from .parsecommand import read_command

from .utils import next_name, Bounds

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
                        
            if b.op=='D02':
                if curr:
                    shapes.append(('r' if self.state.in_region else 'l', curr))
                    curr=[]
            
            if a=='l':
                curr.append((a, (b.x or 0)*0.000001, (b.y or 0)*-0.000001))
            else:
                curr.append((a, (b.x or 0)*0.000001, (b.y or 0)*-0.000001, (b.i or 0)*-0.000001, (b.j or 0)*-0.000001))
            if b.op=='D03':
                shapes.append(('p',curr[0]))
                curr=[]
        if curr:
            shapes.append(('r' if self.state.in_region else 'l', curr))
        return shapes
        
    
    def merge(self, aperture_renames, x_offset=0, y_offset=0):
        
        new_item = GraphicalItem(self.state)
        new_item.state.aperture = aperture_renames[self.state.aperture]
        
        for a,b in self.items:
            nb = commands.GraphicalOperation(
                b.op,
                b.x + x_offset,
                b.y + y_offset,
                b.i,
                b.j
            )   
            new_item.add(a,nb)
        return new_item
        
        
        
    
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
    
    def __eq__(self, other):
        return (self.params == other.params) and (self.name == other.name) and (self.attributes == other.attributes)
        

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
        
        self.num_merged=0
    
    
    def base_parts(self):
        
        #before first aperturemacro / aperture defn, last item        
        res = []
        for p in self.parts:
            
            if p.command and isinstance(p.command, commands.Comment) and p.command.comment=="APERTURE LIST":
                print("found last line", p)
                break
            res.append(p)
        res.extend(self.parts[-2:])
        return res
    
    
    def find_bounds(self):
        bounds=Bounds()
        
        for gi in self.graphical_items:
            for a,b in gi.items:
                bounds.expand(b.x, b.y)
        
        return bounds
        
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
                    if p.command.command=='G01':
                        plotting_mode='l' #linear
                    elif p.command.command=='G02':
                        plotting_mode='c' #clockwise
                    elif p.command.command=='G03':
                        plotting_mode='a' #anticlockwise / counterclockwise
                    elif p.command.command=='G75':
                        if not plotting_mode in ('c', 'a'):
                            print('PlotStateCommand[G75] when not in clockwise / counterclockwise arc mode?')
                
                elif isinstance(p.command, commands.ApertureAttributes):
                    curr_aperture_attrs[p.command.name]=p.command.values
                
                elif isinstance(p.command, commands.ApertureMacro):
                    self.aperture_macros[p.command.macro_name]=p.command
                elif isinstance(p.command, commands.ApertureDefinition):
                    self.apertures[p.command.ident]=Aperture(dict(curr_aperture_attrs.items()), p.command.template_name, p.command.template_params)
                
                elif isinstance(p.command, commands.RegionStateCommand):
                    if p.command.command=='G36':
                        state.in_region=True
                        if curr_graphical_item.items:
                            self.graphical_items.append(curr_graphical_item)
                        curr_graphical_item = GraphicalItem(state)
                    elif p.command.command=='G37':
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
                    
    
    def translate_parts(self, x_offset, y_offset):
        
        for gi in self.graphical_items:
            for a,b in gi.items:
                if b.x is not None:
                    b.x += x_offset
                if b.y is not None:
                    b.y += y_offset
    
    
    def combine_aperture_macro(self, other, suffix):
        
        for curr_name, curr_macro in self.aperture_macros.items():
            if other.macro_body == curr_macro.macro_body:
                #found
                return curr_name
        
        
        new_name = other.macro_name
        if other.macro_name in self.aperture_macros:
            #name alread used
            new_name +=  suffix
        
        new_macro = commands.ApertureMacro(new_name, other.macro_body)
        self.aperture_macros[new_name] = new_macro
        return new_name
        
    def combine_aperture(self, other_ident, other, macro_renames):
        
        for curr_ident, curr_aperture in self.apertures.items():
            
            if curr_aperture == other:
                if not other.name in macro_renames or macro_renames[other.name]==other.name:
                    #found
                    return curr_ident
        
        new_ident = other_ident
        if new_ident in self.apertures:
            new_ident = next_name(self.apertures, 'D')
            if new_ident in self.apertures:
                raise Exception("!!")
        new_aperture = Aperture(other.attributes, macro_renames.get(other.name, other.name), other.params)
        self.apertures[new_ident] = new_aperture
                
        return new_ident
                
    def check_compatible(self, other):
        if not other.units == self.units:
            raise Exception("units different")
        if not other.num_digits == self.num_digits:
            raise Exception("num_digits different")
        for k in (".SameCoordinates", ".FileFunction", ".FilePolarity"):
            if not other.file_attributes.get(k) == self.file_attributes.get(k):
                raise Exception("file attribute {k} different")
            
        return True
    
    
    def merge_gerberfile(self, other, x_offset, y_offset):
        
        self.check_compatible(other)
        
        merged_suffix = "_merged_%02d" % (self.num_merged+1)
        
        macro_translate = {}
        aperture_translate = {}
        
        for nn, macro in other.aperture_macros.items():
            macro_translate[nn] = self.combine_aperture_macro(macro, merged_suffix)
            
        
        
        for nn, aperture in other.apertures.items():
            aperture_translate[nn] = self.combine_aperture(nn, aperture, macro_translate)
        
        for item in other.graphical_items:
            new_item = item.merge(aperture_translate, x_offset, y_offset)
            self.graphical_items.append(new_item)
        
        self.num_merged+=1
            
    def save(self, filename):
        output = self.make_gerber_from_parts()
        with open(filename, 'w') as output_file:
            output_file.write(output_str)
            
    
    
    def make_gerber_from_parts(self):
        result = fileformat.PartsList()
        #header
        for k,v in self.file_attributes.items():
            result.add(commands.FileAttributes(k, v), True)
        
        result.add(commands.FormatSpec(4), True)
        result.add(commands.Units(True), True)
        
        result.add(commands.LoadPolarity('D'), True)
        result.add(commands.PlotStateCommand('G01'))
        
        #aperture macros
        result.add(commands.Comment("APERTURE LIST"))
        result.add(commands.Comment("Aperture macros list"))
        
        for k,v in sorted(self.aperture_macros.items()):
            result.add(commands.ApertureMacro(k, v.macro_body), True)
        
        result.add(commands.Comment("Aperture macros list end"))
        for k,v in sorted(self.apertures.items()):
            if v.attributes:
                for p,q in sorted(v.attributes.items()):
                    result.add(commands.ApertureAttributes(p,q),True)
                    
            result.add(commands.ApertureDefinition(k, v.name, v.params), True)
            if v.attributes:
                result.add(commands.DeleteAttributes(),True)
        
        result.add(commands.Comment("APERTURE END LIST"))
        
        curr_plot_mode='l'
        curr_state = State()
        curr_state.polarity='D'
        
        for gi in sorted(self.graphical_items, key=lambda p: p.state.aperture):
            if gi.state.aperture != curr_state.aperture:
                result.add(commands.SetCurrentAperture(gi.state.aperture))
                curr_state.aperture=gi.state.aperture
            if gi.state.polarity != curr_state.polarity:
                result.add(commands.LoadPolarity(gi.state.polarity),True)
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
                result.add(commands.ObjectAttributes('.P', gi.state.pin_name),True)
            if gi.state.net_name:
                result.add(commands.ObjectAttributes('.N', gi.state.net_name),True)    
            if gi.state.comp_name:
                result.add(commands.ObjectAttributes('.C', gi.state.comp_name),True)
            
            if gi.state.in_region:
                result.add(commands.RegionStateCommand('G36'))
                result.add(copy.deepcopy(gi.items[0][1]))
                result.add(commands.PlotStateCommand('G01'))
                for p,q in gi.items[1:]:
                    if p!='l':
                        raise Exception("!!")
                    result.add(copy.deepcopy(q))
                result.add(commands.RegionStateCommand('G37'))
            else:
                for p,q in gi.items:
                    if p!=curr_plot_mode:
                        if p=='l':
                            result.add(commands.PlotStateCommand('G01'))
                        elif p=='c':
                            result.add(commands.PlotStateCommand('G02'))
                            result.add(commands.PlotStateCommand('G75'))
                        elif p=='a':
                            result.add(commands.PlotStateCommand('G03'))
                            result.add(commands.PlotStateCommand('G75'))
                        curr_plot_mode=p
                    result.add(copy.deepcopy(q))
                
            if gi.state.pin_name or gi.state.net_name or gi.state.comp_name:
                result.add(commands.DeleteAttributes(),True)
        
        
        if curr_state.polarity != 'D':
            result.add(commands.LoadPolarity('D'),True)
        
        
        
        result.add(commands.EndOfFile())
            
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
            
            op = pt.command.op
            x = None if pt.command.x is None else pt.command.x + x_offset
            y = None if pt.command.y is None else pt.command.y + y_offset
            i = pt.command.i
            j = pt.command.j
            
            new_command = GraphicalOperation(op, x, y, i, j)
            new_command_str = str(new_command)
            new_part = Line(pos, pos+len(new_command_str), new_command_str, new_command)
            new_parts.append(new_part)
    
    
    return new_parts
                

def combine_all(parts, spec, output_prfx, edge_cuts_rectangle=None, silkscreen_lines=[]):
    if not spec:
        raise Exception("no spec?")
        
    for n,_,_ in spec:
        if not n in parts:
            raise Exception(f"no {n} in parts [{parts.keys()}]")
    
    
    
    #extensions = dict((a,os.path.splitext(b.filename)[1]) for a,b in base.items())        
    #print(extensions)
    
    layer0_name, _, _ = spec[0]
    layer0 = parts[layer0_name]
    
    if len(spec)>1:
        
        for n,_,_ in spec[1:]:
            
            for k,v in layer0.items():
                if not k in parts[n]:
                    raise Exception(f"part {n} has not {k} layer")
                try:
                    v.check_compatible(parts[n][k])
                except Exception as ex:
                    raise Exception(f"part {n} layer {k} not compatible {str(ex)}")
    
    
      
    
    for lyr, ly0_gerber in layer0.items():
        output_extension = os.path.splitext(ly0_gerber.filename)[1]
        output_filename = output_prfx + '_' + lyr + output_extension
        
        base_gerber = GerberFile(output_filename, None, ly0_gerber.base_parts())
        
        if lyr=='Edge_Cuts' and edge_cuts_rectangle:
            
            base_gerber.apertures['D10'] = Aperture({'.AperFunction':'Profile'}, "C", [('f',0.05)])
            
            bounds=Bounds()
            if isinstance(edge_cuts_rectangle, list):
                bounds.expand(edge_cuts_rectange[0]*1_000_000,-edge_cuts_rectange[1]*1_000_000)
                bounds.expand(edge_cuts_rectange[2]*1_000_000,-edge_cuts_rectange[3]*1_000_000)
                
            else:
                for other_gerber_name, x_offset, y_offset in spec:
                    other_gerber = parts[other_gerber_name][lyr]
                    other_bounds = other_gerber.find_bounds().translate(x_offset*1_000_000, -y_offset*1_000_000)
                    bounds.expand_bounds(other_bounds)
            
            min_x,min_y,max_x,max_y=bounds
            gi=GraphicalItem()
            gi.state.aperture='D10'
            gi.add('l', commands.GraphicalOperation('D02', min_x, min_y, None, None))
            gi.add('l', commands.GraphicalOperation('D01', min_x, max_y, None, None))
            gi.add('l', commands.GraphicalOperation('D01', max_x, max_y, None, None))
            gi.add('l', commands.GraphicalOperation('D01', max_x, min_y, None, None))
            gi.add('l', commands.GraphicalOperation('D01', min_x, min_y, None, None))
            base_gerber.graphical_items.append(gi)
                                
            
        else:
        
            for other_gerber_name, x_offset, y_offset in spec:
                other_gerber = parts[other_gerber_name][lyr]
                base_gerber.merge_gerberfile(other_gerber, x_offset*1_000_000, -y_offset*1_000_000)
            
            
            if silkscreen_lines and lyr in ('F_Silkscreen', 'B_Silkscreen'):
                apertures={}
                
                for w, start_x, start_y, end_x, end_y in silkscreen_lines:
                    
                    if not w in apertures:
                        aper = Aperture({}, 'C', [('f', w)])
                        nn = base_gerber.combine_aperture('D10', aper, {})
                        apertures[w]=nn
                    
                    gi=GraphicalItem()
                    gi.state.aperture=apertures[w]
                    gi.add('l', commands.GraphicalOperation('D02', start_x*1_000_000, -start_y*1_000_000, None, None))
                    gi.add('l', commands.GraphicalOperation('D01', end_x*1_000_000, -end_y*1_000_000, None, None))
                    base_gerber.graphical_items.append(gi)
            
            
        output = base_gerber.make_gerber_from_parts()
        output_str = output.to_str()
        
        with open(output_filename, 'w') as output_file:
            output_file.write(output_str)
    
    
            
        
    
    
    
    
    
    






    


