import shapely as shp

box_overlaps = lambda A,B: A[2]>B[0] and A[3]>B[1] and B[2]>A[0] and B[3]>A[1]
box_contains = lambda A, B: B[0]>=A[0] and B[1]>=A[1] and B[2]<=A[2] and B[3]<=A[3]

            
class Placement:
    def __init__(self, idx, design, x_pos=0, y_pos=0, angle=0):
        self.idx=idx
        self.design=design
        self.x_pos=x_pos
        self.y_pos=y_pos
        self.angle=angle
        
        self.silkscreen_line=None
        self.calc_board_outline()
        
    @property
    def x_max(self):
        return self.x_pos + (self.design.width if self.angle in (0,180) else self.design.height)
    
    @property
    def y_max(self):
        return self.y_pos + (self.design.width if self.angle in (90,270) else self.design.height)
        
    @property
    def box(self):
        return (self.x_pos, self.y_pos, self.x_max, self.y_max)
        
    def overlaps(self, other):
        return box_overlaps(self.box, other.box if hasattr(other, 'box') else other )
        
    
    
    def __len__(self):
        return 4
    
    def __getitem__(self, i):      
        
        if i==0: return self.design
        elif i==1: return self.x_pos
        elif i==2: return self.y_pos
        elif i==3: return self.angle
        raise IndexError()

    def update(self, x_pos=None, y_pos=None, angle=None):
        if not x_pos is None:
            self.x_pos=x_pos
        if not y_pos is None:
            self.y_pos=y_pos
        if not angle is None:
            self.angle=angle
        self.calc_board_outline()

    def calc_board_outline(self):
        self.board_outline = self.design.get_board_outline(self.x_pos, self.y_pos, self.angle)

    

    def within(self, other):
        if isinstance(other, shp.Polygon):
            return other.contains(self.board_outline)
        else:
            return box_contains(other, self.box)
