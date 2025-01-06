from .utils import num_str, num_str_null, num_repr



class Comment:
    def __init__(self, comment):
        self.comment=comment
    def __str__(self):
        return f"G04 {self.comment}*"
    
    def __repr__(self):
        return f"Comment[{self.comment}]" 

class Units:
    def __init__(self, units_mm):
        self.units_mm=units_mm
    
    def __str__(self):
        return 'MOMM*' if self.units_mm else 'MOIN*'

    def __repr__(self):
        return f"Units[units_mm={self.units_mm}]" 

class FormatSpec:
    def __init__(self, num_digits):
        
        self.num_digits=num_digits
    
    def __str__(self):
        return f"FSLAX{self.num_digits}6Y{self.num_digits}6*"
    
    def __repr__(self):
        return f"FormatSpec[num_digits={self.num_digits}]" 




class ApertureDefinition:
    def __init__(self, ident, template_name, template_params):
        
        self.ident=ident
        self.template_name=template_name
        self.template_params=template_params
    
    def __str__(self):
        return f"AD{self.ident}{self.template_name},{'X'.join(num_str(i,p) for i,p in self.template_params)}*"
    
    def __repr__(self):
        return f"ApertureDefinition[ident={self.ident} template_name={self.template_name} {len(self.template_params)} params]"


class ApertureMacro:
    def __init__(self, macro_name, macro_body):
        
        self.macro_name=macro_name
        self.macro_body=macro_body
        
    
    def __str__(self):
        return f"AM{self.macro_name}*\n{self.macro_body}*"
    
    def __repr__(self):
        return f"ApertureMacro[macro_name='{self.macro_name}' [{len(self.macro_body)} {repr(self.macro_body[:40])}{'...' if len(self.macro_body)>40 else ''}]"

class SetCurrentAperture:
    def __init__(self, ident):
        self.ident=ident
    
    def __str__(self):
        return f"{self.ident}*"
    def __repr__(self):
        return f"SetCurrentAperture[ident={self.ident}]"


class PlotStateCommand:
    def __init__(self, command):
        
        self.command=command
    
    def __str__(self):
        return f"{self.command}*"
    def __repr__(self):
        return f"PlotStateCommand[{self.command}]"


class RegionStateCommand:
    def __init__(self, command):
        
        self.command=command
    
    def __str__(self):
        return f"{self.command}*"
    def __repr__(self):
        return f"RegionStateCommand[{self.command}]"


class GraphicalOperation:
    
    def __init__(self, op, x, y, i, j):
        self.op=op
        self.x, self.y, self.i, self.j = x,y,i,j
    
    def __str__(self):
        x_s='X%d' % self.x if self.x is not None else ''
        y_s='Y%d' % self.y if self.y is not None else ''
        i_s='I%d' % self.i if self.i is not None else ''
        j_s='J%d' % self.j if self.j is not None else ''
        return f"{x_s}{y_s}{i_s}{j_s}{self.op}*"
        
    def __repr__(self):
        return f"GraphicalOperation[{self.op} x={self.x} y={self.y} i={self.i} j={self.j}]"
        
        

class LoadPolarity:
    def __init__(self, polarity):
        self.polarity=polarity
    
    def __str__(self):
        return f"LP{self.polarity}*"
    def __repr__(self):
        return f"LoadPolarity[polarity={self.polarity}]"
        
class LoadMirroring:
    def __init__(self, mirroring):
        self.mirroring=mirroring
    
    def __str__(self):
        return f"LM{self.mirroring}*"
    def __repr__(self):
        return f"LoadMirroring[mirroring={self.mirroring}]"        
    
class LoadRotation:
    def __init__(self, rotation):
        
        self.rotation=rotation
    
    def __str__(self):
        return f"LR{num_str_null(self.rotation)}*"
    def __repr__(self):
        return f"LoadRotation[rotation={num_repr(self.rotation)}]"


class LoadScaling:
    def __init__(self, scaling):
        self.scaling=scaling
    
    def __str__(self):
        return f"LS{num_str_null(self.scaling)}*"
    def __repr__(self):
        return f"LoadScaling[scaling={num_repr(self.scaling)}]"

## blockaperture and steprepeat not used by kicad?
# class BlockAperture:
    # def __init__(self, type, block):
        # self.type=type
        # self.block=block
        
    
    # def __str__(self):
        # return f"{self.type}{self.block or ''}*"
    
    # def __repr__(self):
        # return f"BlockAperture[{self.type} block='{self.block}']"

# class StepRepeat:
    # def __init__(self, type, x, y, i, j):
        # self.type=type
        # self.x,self.y,self.i,self.j=x,y,i,j
        
    # def __str__(self):
        # return f"SR{num_str_null('X',self.x)}{num_str_null('Y',self.y)}{num_str_null('I',self.x)}{num_str_null('J',self.x)}*"
    
    # def __repr__(self):
        # return f"StepRepeat[{self.type} x={num_repr(self.x)} y={num_repr(self.y)} i={num_repr(self.i)} j={num_repr(self.j)}]"


class EndOfFile:
    def __init__(self):
        pass
        
    def __str__(self):
        return f"M02*"
    
    def __repr__(self):
        return f"EndOfFile[]"
        
        
class FileAttributes:
    def __init__(self, name, values):
        
        self.name=name
        self.values=values
    
    def __str__(self):
        return f"TF{self.name},{self.values}*"
    
    def __repr__(self):
        return f"FileAttributes[name={self.name} values={self.values}]"

class ApertureAttributes:
    def __init__(self, name, values):
        
        self.name=name
        self.values=values
    
    def __str__(self):
        return f"TA{self.name},{self.values}*"
    
    def __repr__(self):
        return f"ApertureAttributes[name={self.name} values={self.values}]"
        
class ObjectAttributes:
    def __init__(self, name, values):
        
        self.name=name
        self.values=values
    
    def __str__(self):
        return f"TO{self.name},{self.values}*"
    
    def __repr__(self):
        return f"ObjectAttributes[name={self.name} values={self.values}]"

class DeleteAttributes:
    def __init__(self, name=None):
        
        self.name=name
        
    def __str__(self):
        return f"TD{self.name or ''}*"
    
    def __repr__(self):
        return f"DeleteAttributes[name={self.name}]"


