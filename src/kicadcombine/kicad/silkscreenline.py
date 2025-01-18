import pcbnew
from .mergeboardoutline import make_vec
import shapely as shp

def none_or_float(x):
    try:
        return float(x)
    except:
        return None

class SilkscreenLine:
    
    @classmethod
    def vertical(Self, parent, x_pos, y0=None, y1=None, width=None):
        if x_pos is None:
            raise Exception("!!")
        w=width or parent.spacing
        return Self(parent, x_pos-w/2, y0, x_pos-w/2, y1, width)
    
    @classmethod
    def horizontal(Self, parent, y_pos, x0=None, x1=None, width=None):
        if y_pos is None:
            raise Exception("!!")
        w=width or parent.spacing
        return Self(parent, x0, y_pos-w/2, x1, y_pos-w/2, width)
    
    
    def __init__(self, parent, x0, y0, x1, y1, width):
        self.parent=parent
        self.x0, self.y0, self.x1, self.y1, self.width = x0, y0, x1, y1, width
        
    def get_value(self, i):
        if i==0: return 'left' if self.x0 is None else '%5.1f' % self.x0
        if i==1: return 'bottom' if self.y0 is None else '%5.1f' % self.y0
        if i==2: return 'right' if self.x1 is None else '%5.1f' % self.x1
        if i==3: return 'top' if self.y1 is None else '%5.1f' % self.y1
        if i==4: return 'default' if self.width is None else '%5.1f' % self.width
    
    def set_value(self, i, val):
        if i==0: self.x0=none_or_float(val)
        if i==1: self.y0=none_or_float(val)
        if i==2: self.x1=none_or_float(val)
        if i==3: self.y1=none_or_float(val)
        if i==4: self.width=none_or_float(val)
    
    def __getitem__(self, i):
        if i==0: return 0 if self.x0 is None else self.x0
        if i==1: return 0 if self.y0 is None else self.y0
        if i==2: return self.parent.board_width if self.x1 is None else self.x1
        if i==3: return self.parent.board_height if self.y1 is None else self.y1
        if i==4: return self.parent.spacing if self.width is None else self.width
    
    def tuple(self):
        return (self[0],self[1],self[2],self[3],self[4])
    
    def __len__(self):
        return 5
    
    def get_start(self):
        return (
            0 if self.x0 is None else self.x0,
            0 if self.y0 is None else self.y0)
    
    def get_end(self):
        return (
            self.parent.board_width if self.x1 is None else self.x1,
            self.parent.board_height if self.y1 is None else self.y1)
    
    @property
    def polygon(self):
        return shp.LineString([self.get_start(), self.get_end()]).buffer(self.get_width()/2)
        
    def get_width(self):
        if self.width is None:
            return self.parent.spacing
        return self.width
        
        
    
    def add_to_board(self, board, layers=[pcbnew.F_SilkS, pcbnew.B_SilkS]):
        for lyr in layers:
            line = pcbnew.PCB_SHAPE()
            line.SetStart(make_vec(self[0]+20, self[1]+20))
            line.SetEnd(make_vec(self[2]+20, self[3]+20))
            line.SetLayer(lyr)
            line.SetWidth(int(self[4]*1_000_000+0.5))
            board.Add(line)
    
