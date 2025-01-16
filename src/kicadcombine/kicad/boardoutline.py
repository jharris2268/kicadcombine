import shapely as shp
import shapely.ops as sop

from math import sin, cos, pi
import numpy as np

import pcbnew


class Line:
    
    @staticmethod
    def lines_from_rect(rect):
        a,b,c,d = rect.GetStartX(),rect.GetStartY(),rect.GetEndX(),rect.GetEndY()
        return [Line(seg=None,start=[a,b],end=[c,b]),
                Line(seg=None,start=[c,b],end=[c,d]),
                Line(seg=None,start=[c,d],end=[a,d]),
                Line(seg=None,start=[a,d],end=[a,b])]
    
    def __init__(self, seg, start=None,end=None):
        if start is None and not seg is None:
            self.start_x, self.start_y = seg.GetStartX()/1_000_000, seg.GetStartY()/1_000_000
            self.end_x, self.end_y = seg.GetEndX()/1_000_000, seg.GetEndY()/1_000_000
        elif seg is None and not start is None and not start is None:
            self.start_x, self.start_y = start[0]/1_000_000,start[1]/1_000_000
            self.end_x, self.end_y = end[0]/1_000_000,end[1]/1_000_000
        else:
            raise Exception("specify seg OR start and end")
    
    @property
    def start(self):
        return (self.start_x, self.start_y)
    
    @property
    def end(self):
        return (self.end_x, self.end_y)
    
    def shape(self, ns=None):
        return shp.LineString([[self.start_x,self.start_y], [self.end_x, self.end_y]])

class Arc:
    def __init__(self, seg):
        self.start_x, self.start_y = seg.GetStartX()/1_000_000, seg.GetStartY()/1_000_000
        self.end_x, self.end_y = seg.GetEndX()/1_000_000, seg.GetEndY()/1_000_000
        
        self.start_angle = seg.GetArcAngleStart().AsDegrees()
        self.arc_angle = seg.GetArcAngle().AsDegrees()
        self.radius = seg.GetRadius()/1_000_000
        if abs(self.interp_x(self.arc_angle) - self.end_x)>0.001:
            print(f"?? interp_x({self.arc_angle}) {self.interp_x(self.arc_angle)}!={self.end_x}")
        if abs(self.interp_y(self.arc_angle)-self.end_y)>0.001:
            print(f"?? interp_y({self.arc_angle}) {self.interp_y(self.arc_angle)}!={self.end_y}")
    
    @property
    def start(self):
        return (self.start_x, self.start_y)
    
    @property
    def end(self):
        return (self.end_x, self.end_y)
    
    def interp_x(self, a):
        return self.start_x + self.radius * (
            cos( (self.start_angle + a) * pi / 180) - 
            cos( (self.start_angle) * pi / 180))
    
    def interp_y(self, a):
        return self.start_y + self.radius * (
            sin( (self.start_angle + a) * pi / 180) - 
            sin( (self.start_angle) * pi / 180))
    
    def shape(self, ns=None):
        ii = np.linspace(0, self.arc_angle, ns or 15)
        return shp.LineString([[self.interp_x(i),self.interp_y(i)] for i in ii])

class Rect:
    def __init__(self, seg):
        self.left, self.top = seg.GetStartX()/1_000_000, seg.GetStartY()/1_000_000
        self.right, self.bottom = seg.GetEndX()/1_000_000, seg.GetEndY()/1_000_000
        
    
    @property
    def start(self):
        return (self.left, self.top)
    
    @property
    def end(self):
        return (self.left, self.top)
    
    def shape(self, ns=None):
        return shp.box(self.left, self.top, self.right, self.bottom).boundary

       
def iter_pairs(itr):
    prev=None
    for i in itr:
        if prev is None:
            pass
        else:
            yield (prev, i)
        prev=i


def find_shape(shapes, a, b):
    for s in shapes:
        if (s.start == a) and (s.end == b):
            return (s, 'f')
        elif (s.start == b) and (s.end == a):
            return (s, 'b')
    
    return None
            
            
def make_shapes(board,split_rect=True):
    shapes = []
    for drawing in board.Drawings():
        if drawing.GetLayer()==pcbnew.Edge_Cuts and drawing.Type()==5:
            if drawing.ShowShape() == 'Line':
                shapes.append(Line(drawing))
            elif drawing.ShowShape() == 'Arc':
                shapes.append(Arc(drawing))
            elif drawing.ShowShape() == 'Rect':
                if split_rect:
                    shapes.extend(Line.lines_from_rect(drawing))
                else:
                    shapes.append(Rect(drawing))
            else:
                print(f"?? {drawing}")
        
    return shapes

def find_board_outline_polygon(board, ns=None):
    
    shapes=make_shapes(board)
    polygon = make_polygon(shapes, ns)
    
    min_x, min_y, _, _ = polygon.bounds
    polygon_translated = sop.transform(lambda x,y: [x-min_x, y-min_y], polygon)
    
    return polygon_translated, [min_x, min_y]

def make_polygon(shapes, ns=None):
    polygon = shp.polygonize([s.shape(ns) for s in shapes])
    
    if polygon.geom_type=='Polygon':
        return polygon
    elif polygon.geom_type=='GeometryCollection':
        if len(polygon.geoms)==0:
            raise Exception("no outline?")
        
        return max(polygon.geoms, key=lambda x: x.area)
        
        
        
    else:
        raise Exception("??")
    
    return None


def find_board_outline_parts(board):
    
    shapes=make_shapes(board)
    polygon = make_polygon(shapes, 2)
    
    
    exterior_rev = [find_shape(shapes, a,b) for a,b in iter_pairs(polygon.exterior.coords)]
    interiors_rev = [[find_shape(shapes, a, b) for a,b in iter_pairs(ii.coords)] for ii in polygon.interiors]
    
    exterior = [(a,'b' if b=='f' else 'f') for a,b in reversed(exterior_rev)]
    
    interiors = [[(a,'b' if b=='f' else 'f') for a,b in reversed(ii)] for ii in interiors_rev]
    
    
    return polygon.bounds, exterior, interiors
    
    
        
