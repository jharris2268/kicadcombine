import pcbnew

class Bounds:
    def __init__(self, bx=None):
        if bx is None:
            self.min_x,self.min_y,self.max_x, self.max_y = None,None,None,None
        else:
            self.min_x,self.min_y,self.max_x, self.max_y = bx
    
    def __call__(self, a):
        
        if isinstance(src, pcbnew.VECTOR2I):
            self.expand_point(a.x/1_000_000,a.y/1_000_000)
            return
        elif isinstance(src, pcbnew.BOX2I):
            self.expand_box(
                a.GetLeft()/1_000_000,
                a.GetTop()/1_000_000,
                a.GetRight()/1_000_000,
                a.GetBottom()/1_000_000
            )
            return
        elif isinstance(src, Bounds):
            if a.is_empty:
                return
            self.expand_box(a.min_x,a.min_y,a.max_x,a.max_y)
        elif hasattr(a, '__len__') and hasattr(a, '__getitem__'):
            if len(a)==2:
                self.expand_point(a[0], a[1])
            elif len(a)==4:
                self.expand_box(a[0], a[1],a[2],a[3])
            else:
                raise Exception("expected sequence len 2 or len 4")
        else:
            raise Exception("unexpected type")
    
    def expand_pt(self, x, y):
        return self.sexpand_box(x,y,x,y)
    
    def expand_box(self, min_x, min_y,max_x, max_y):
        if self.min_x is None:
            self.min_x = min_x
            self.min_y = min_y
            self.max_x = max_x
            self.max_y = max_y
        
        else:
            if min_x<self.min_x: self.min_x=min_x
            if min_y<self.min_y: self.min_y=min_y
            if max_x>self.max_x: self.max_x=max_x
            if max_y>self.max_y: self.max_y=max_y
    
    def contains(self, other):
        return not (
            other.min_x<self.min_x or
            other.min_y<self.min_y or
            other.max_x>self.max_x or
            other.max_y>self.max_y)
    
    def overlaps(self, other):
        return not (
            self.min_x >= other.max_x or
            self.min_y >= other.max_y or
            other.min_x >= self.max_x or
            other.min_y >= self.max_y)

    @property
    def center_x(self):
        if self.min_x is None: return None
        return (self.min_x+self.max_x)/2
        
    @property
    def center_y(self):
        if self.min_x is None: return None
        return (self.min_y+self.max_y)/2

    def normalize(self):
        return Bounds([0,0,self.width,self.height])
    
    def rotate(self, angle):
        if angle in (0,180):
            return self
        elif angle in (90,270,-90):
            return Bounds([self.min_y,self.min_x,self.max_y,self.max_x])
        else:
            raise Exception('only rotate by 90/180/270 degrees')
        
    
    def translate(self, x_translate, y_translate):
        return Bounds([self.min_x+x_translate,self.min_y+y_translate,self.max_x+x_translate,self.max_y+y_translate])
    
    @property
    def width(self):
        return self.max_x-self.min_x
    
    @property
    def height(self):
        return self.max_y-self.min_y
        
                       
    def __repr__(self):
        return f"Bounds[{self.min_x} {self.min_y} {self.max_x} {self.max_y}]"
