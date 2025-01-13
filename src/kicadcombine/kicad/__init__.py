import pcbnew
import kikit.panelize as pnl
import kikit.substrate as subs

import os.path
import shapely as shp
import shapely.ops as sop
from math import sin, cos, pi
import numpy as np



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
    
    
        
    

class SourceFile:
    def __init__(self, name, path):
        self.name=name
        self.path=path
        self.board = pcbnew.LoadBoard(path)
        
        self.board_outline, self.offset = find_board_outline_polygon(self.board)
        self.bounds=Bounds(self.board_outline.bounds)
    
    def get_board_outline(self, x_pos, y_pos, angle):
        poly = self.board_outline
        if angle:
            if angle == 90:
                poly = sop.transform(lambda x,y: [y,x], poly)
            elif angle == 180:
                max_x, max_y = self.bounds.max_x, self.bounds.max_y
                poly = sop.transform(lambda x,y: [max_x-x,max_y-y], poly)
            elif angle in (-90,270):
                max_x, max_y = self.bounds.max_x, self.bounds.max_y
                poly = sop.transform(lambda x,y: [max_y-y,max_x-x], poly)
            else:
                raise Exception("angle must be 0,90,180 or 270 degrees")
        
        return sop.transform(lambda x,y: [x+x_pos, y+y_pos], poly)
    
    def __repr__(self):
        return f"SourceFile[{self.name}: {self.bounds.width:0.1f}mm x {self.bounds.height:0.1f}mm]"
        


def get_kicad_pcb(dir):
    count=0
    if not os.path.exists(dir):
        raise Exception(f"path {dir} does not exist")


    
    if os.path.isdir(dir):
    
        for a,b,cc in os.walk(dir):
            for c in cc:
                d,e=os.path.splitext(c)
                if e=='.kicad_pcb':
                    yield d, os.path.join(a,c)
                    count+=1
    else:   
        a,c=os.path.split(dir)
        d,e=os.path.splitext(c)
        if e=='.kicad_pcb':
            yield d, dir
            count+=1
        else:
            raise Exception(f"expected {dir} to have extension .kicad_pcb")
        
        
    if not count:
        raise Exception(f"no kicad_pcb files in {dir}")
        
def get_source_files(dirs):
    result={}
    for d in dirs:
        for x,y in get_kicad_pcb(d):
            result[x] = SourceFile(x, y)
            print(result[x])
    return result

def make_vec(x, y):
    return pcbnew.VECTOR2I( int(x*1_000_000+0.5), int(y*1_000_000+0.5))
    

def add_line(board, x0, y0, x1, y1, layers, width):
    
    for lyr in layers:
        line = pcbnew.PCB_SHAPE()
        line.SetStart(make_vec(x0+20, y0+20))
        line.SetEnd(make_vec(x1+20, y1+20))
        line.SetLayer(lyr)
        line.SetWidth(width*1_000_000)
        board.Add(line)
    
    
def iter_polygons(geom):
    if geom.geom_type == 'Polygon':
        yield geom
    elif geom.geom_type == 'MultiPolygon':
        for p in geom.geoms:
            yield p
    elif geom.geom_type == 'GeometryCollection':
        for g in geom.geoms:
            for p in iter_polygons(g):
                yield p
    else:
        raise Exception(f"unexpected geometry f{geom}")
    
    

def prepare_panel(source_files, pattern, lines, output_file, bake_text=False, return_all=False):
    boxes = [source_files[src].bounds.normalize().rotate(angle).translate(x_pos,y_pos) for src,x_pos,y_pos,angle in pattern]
    for i,bx in enumerate(boxes):
        for j,bx2 in enumerate(boxes):
            if j<=i:
                continue
            
            if bx.overlaps(bx2):
                print(f"ERROR: [{i} {pattern[i][0]}] {bx} overlaps [{j} {pattern[j][0]} {bx2}")
        
    pp = pnl.Panel(output_file)
    polys = []
    for srcn, x_pos, y_pos,angle in pattern:
        print(f"adding {srcn} @ {x_pos} {y_pos}")   
        src = source_files[srcn]
        src_bounds=src.bounds.rotate(angle)
        pos_vec = make_vec(x_pos+20+src_bounds.center_x, y_pos+20+src_bounds.center_y)
        pp.appendBoard(
            src.path,
            pos_vec,
            rotationAngle=pcbnew.EDA_ANGLE(angle),
            origin=pnl.Origin.Center,
            tolerance=50_000,
            inheritDrc=False,
            bakeText=bake_text)
        
        
        poly = src.get_board_outline(x_pos, y_pos, angle)
        polys.append(no_holes(poly))
    
    
    board_poly = fill_gaps(polys)
    
    if False:
    
        line_polys = [shp.LineString([[a,b],[c,d]]).buffer(0.5, cap_style='flat') for a,b,c,d in lines]
        
        initial_board_poly = shp.unary_union(polys+line_polys)
        
        board_poly = None
        if initial_board_poly.geom_type == 'Polygon':
            board_poly = no_holes(initial_board_poly)
        else:
            board_poly = fill_gaps(list(iter_polygons(initial_board_poly)))
    
    board_poly_int = shp.Polygon([[(x+20)*1_000_000, (y+20)*1_000_000] for x,y in board_poly.exterior.coords])
    pp.appendSubstrate(board_poly_int)
    
    #print('handle lines?')
    for a,b,c,d in lines:
        add_line(pp.board, x0=a,y0=b,x1=c,y1=d, layers=[pcbnew.F_SilkS, pcbnew.B_SilkS], width=1)
    
    pp.save()
    if return_all:
        return {'panel': pp, 'polys': polys, 'board_poly': board_poly, 'board_poly_int': board_poly_int}
    
    return pp
    
def no_holes(poly):
    if poly.geom_type=='MultiPolygon':
        return sop.unary_union([no_holes(p) for p in poly.geoms])
    if poly.geom_type != 'Polygon':
        raise Exception("not a polygon")
    
    return shp.Polygon(poly.exterior)

def iter_points(line):
    if line.geom_type == 'MultiLineString':
        for ll in line.geoms:
            for p in iter_points(ll):
                yield p
        return
    
    if line.geom_type != 'LineString':
        raise Exception("not a linestring")
    
    for x,y in line.coords:
        yield shp.Point(x,y)

def find_closest(line, point):
    if line.geom_type == 'MultiLineString':
        pds = [find_closest(l, point) for l in line.geoms]
        p,d=min(pds, key=lambda s: s[1])
        return p,d
    
    x = line.project(point)
    p = line.interpolate(x)
    d = line.distance(point)
    return p,d


def join_poly(left, right, max_gap=5):
    boundary_left = left.boundary
    boundary_right = right.boundary
    result=[]
        
    for (p0,p1) in iter_pairs(iter_points(boundary_left)):
                    
        q0,d0 = find_closest(boundary_right, p0)
        q1,d1 = find_closest(boundary_right, p1)
        
        if d0 < max_gap and d1 < max_gap:
            #add polygon from four points
            result.append(shp.Polygon([p0,p1,q1,q0,p0]))

    for (p0,p1) in iter_pairs(iter_points(boundary_right)):
        q0,d0 = find_closest(boundary_left, p0)
        q1,d1 = find_closest(boundary_left, p1)
        
        if d0 < max_gap and d1 < max_gap:
            #add polygon from four points
            result.append(shp.Polygon([p0,p1,q1,q0,p0]))
    return result
    

def fill_gaps(polys, max_gap=5):
    if len(polys)==0:
        raise Exception("no polys")
    if len(polys)==1:
        return no_holes(polys[0])
        
    result_poly = [no_holes(polys[0])]
    
    
    for poly in polys[1:]:
        new_part = no_holes(poly)
        existing =shp.unary_union(result_poly)
        
        
        extra_parts=join_poly(new_part, existing)
        #print(filled.area, result_poly_joined.area, len(new_parts))
        
        result_poly.append(new_part)
        result_poly.extend(extra_parts)
        
            
    return no_holes(shp.unary_union(result_poly))            
        
    
    
