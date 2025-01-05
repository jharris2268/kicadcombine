from .utils import num_str, num_str_null, num_repr



class Comment:
    def __init__(self, type, comment):
        self.type=type
        self.comment=comment
    def __str__(self):
        return "%s %s*" % (self.type, self.comment)
    
    def __repr__(self):
        return f"Comment[{self.type} {self.comment}]" 

class Units:
    def __init__(self, type, units_mm):
        self.type=type
        self.units_mm=units_mm
    
    def __str__(self):
        return "%s%s*" % (self.type, 'MM' if self.units_mm else 'IN')

    def __repr__(self):
        return f"Units[{self.type} units_mm={self.units_mm}]" 

class FormatSpec:
    def __init__(self, type, num_digits):
        self.type=type
        self.num_digits=num_digits
    
    def __str__(self):
        return f"{self.type}LAX{self.num_digits}6Y{self.num_digits}6*"
    
    def __repr__(self):
        return f"FormatSpec[{self.type} num_digits={self.num_digits}]" 




class ApertureDefinition:
    def __init__(self, type, ident, template_name, template_params):
        self.type=type
        self.ident=ident
        self.template_name=template_name
        self.template_params=template_params
    
    def __str__(self):
        return f"{self.type}{self.ident}{self.template_name},{'X'.join(num_str(i,p) for i,p in self.template_params)}*"
    
    def __repr__(self):
        return f"ApertureDefinition[{self.type} ident={self.ident} template_name={self.template_name} {len(self.template_params)} params]"


class ApertureMacro:
    def __init__(self, type, macro_name, macro_body):
        self.type=type
        self.macro_name=macro_name
        self.macro_body=macro_body
        
    
    def __str__(self):
        return f"{self.type}{self.macro_name}*\n{self.macro_body}*"
    
    def __repr__(self):
        return f"ApertureMacro[{self.type} macro_name='{self.macro_name}' [{len(self.macro_body)} {repr(self.macro_body[:40])}{'...' if len(self.macro_body)>40 else ''}]"

class SetCurrentAperture:
    def __init__(self, type, ident):
        self.type=type
        self.ident=ident
    
    def __str__(self):
        return f"{self.type}{self.ident}*"
    def __repr__(self):
        return f"SetCurrentAperture[{self.type} ident={self.ident}]"


class PlotStateCommand:
    def __init__(self, type, number):
        self.type=type
        self.number=number
    
    def __str__(self):
        return f"{self.type}{self.number}*"
    def __repr__(self):
        return f"PlotStateCommand[{self.type} number={self.number}]"


class RegionStateCommand:
    def __init__(self, type, number):
        self.type=type
        self.number=number
    
    def __str__(self):
        return f"{self.type}{self.number}*"
    def __repr__(self):
        return f"RegionStateCommand[{self.type} number={self.number}]"


class GraphicalOperation:
    
    def __init__(self, type, x, y, i, j):
        self.type=type
        self.x, self.y, self.i, self.j = x,y,i,j
    
    def __str__(self):
        x_s='X%d' % self.x if self.x is not None else ''
        y_s='Y%d' % self.y if self.y is not None else ''
        i_s='I%d' % self.i if self.i is not None else ''
        j_s='J%d' % self.j if self.j is not None else ''
        return f"{x_s}{y_s}{i_s}{j_s}{self.type}*"
        
    def __repr__(self):
        return f"GraphicalOperation[{self.type} x={self.x} y={self.y} i={self.i} j={self.j}]"
        
        

class LoadPolarity:
    def __init__(self, type, polarity):
        self.type=type
        self.polarity=polarity
    
    def __str__(self):
        return f"{self.type}{self.polarity}*"
    def __repr__(self):
        return f"LoadPolarity[{self.type} polarity={self.polarity}]"
        
class LoadMirroring:
    def __init__(self, type, mirroring):
        self.type=type
        self.mirroring=mirroring
    
    def __str__(self):
        return f"{self.type}{self.mirroring}*"
    def __repr__(self):
        return f"LoadMirroring[{self.type} mirroring={self.mirroring}]"        
    
class LoadRotation:
    def __init__(self, type, rotation):
        self.type=type
        self.rotation=rotation
    
    def __str__(self):
        return f"{self.type}{num_str_null(self.rotation)}*"
    def __repr__(self):
        return f"LoadRotation[{self.type} rotation={num_repr(self.rotation)}]"


class LoadScaling:
    def __init__(self, type, scaling):
        self.type=type
        self.scaling=scaling
    
    def __str__(self):
        return f"{self.type}{num_str_null(self.scaling)}*"
    def __repr__(self):
        return f"LoadScaling[{self.type} scaling={num_repr(self.scaling)}]"


class BlockAperture:
    def __init__(self, type, block):
        self.type=type
        self.block=block
        
    
    def __str__(self):
        return f"{self.type}{self.block or ''}*"
    
    def __repr__(self):
        return f"BlockAperture[{self.type} block='{self.block}']"

class StepRepeat:
    def __init__(self, type, x, y, i, j):
        self.type=type
        self.x,self.y,self.i,self.j=x,y,i,j
        
    def __str__(self):
        return f"SR{num_str_null('X',self.x)}{num_str_null('Y',self.y)}{num_str_null('I',self.x)}{num_str_null('J',self.x)}*"
    
    def __repr__(self):
        return f"StepRepeat[{self.type} x={num_repr(self.x)} y={num_repr(self.y)} i={num_repr(self.i)} j={num_repr(self.j)}]"


class EndOfFile:
    def __init__(self, type):
        self.type=type
        
    def __str__(self):
        return f"{self.type}*"
    
    def __repr__(self):
        return f"EndOfFile[{self.type}]"
        
        
class FileAttributes:
    def __init__(self, type, name, values):
        self.type=type
        self.name=name
        self.values=values
    
    def __str__(self):
        return f"{self.type}{self.name},{self.values}*"
    
    def __repr__(self):
        return f"FileAttributes[{self.type} name={self.name} values={self.values}]"

class ApertureAttributes:
    def __init__(self, type, name, values):
        self.type=type
        self.name=name
        self.values=values
    
    def __str__(self):
        return f"{self.type}{self.name},{self.values}*"
    
    def __repr__(self):
        return f"ApertureAttributes[{self.type} name={self.name} values={self.values}]"
        
class ObjectAttributes:
    def __init__(self, type, name, values):
        self.type=type
        self.name=name
        self.values=values
    
    def __str__(self):
        return f"{self.type}{self.name},{self.values}*"
    
    def __repr__(self):
        return f"ObjectAttributes[{self.type} name={self.name} values={self.values}]"

class DeleteAttributes:
    def __init__(self, type, name=None):
        self.type=type
        self.name=name
        
    
    def __str__(self):
        return f"{self.type}{self.name or ''}*"
    
    def __repr__(self):
        return f"DeleteAttributes[{self.type} name={self.name}]"


