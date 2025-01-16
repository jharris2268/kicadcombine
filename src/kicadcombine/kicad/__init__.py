import pcbnew
import kikit.panelize as pnl
import kikit.substrate as subs

import os.path
import shapely as shp
import shapely.ops as sop
from math import sin, cos, pi
import numpy as np

from .boardoutline import find_board_outline_polygon, iter_pairs

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
            
        

    

class SourceFile:
    def __init__(self, name, path):
        self.name=name
        self.path=path
        self.board = pcbnew.LoadBoard(path)
        
        self.board_outline, self.offset = find_board_outline_polygon(self.board)
        self.bounds=Bounds(self.board_outline.bounds)
    
    
    @property
    def width(self):
        return self.bounds.width
    
    @property
    def height(self):
        return self.bounds.height
        
    @property
    def has_f_paste(self):
        return True
    
    @property
    def num_copper_layers(self):
        return self.board.GetCopperLayerCount()
    
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


def find_board_outline_tight(source_files, pattern, lines):
    
    polys = []
    holes = []
    
    for srcn, x_pos, y_pos,angle in pattern:
        src = source_files[srcn]
        poly = src.get_board_outline(x_pos, y_pos, angle)
        polys.append(no_holes(poly))
        holes.extend(shp.Polygon(intr) for intr in poly.interiors)
    
    board_poly = fill_gaps(polys)
    
    if holes:
        board_poly = board_poly.difference(shp.unary_union(holes))
    
    return board_poly


def prepare_panel(source_files, pattern, lines, output_file, bake_text=False, return_all=False):
    boxes = [source_files[src].bounds.normalize().rotate(angle).translate(x_pos,y_pos) for src,x_pos,y_pos,angle in pattern]
    for i,bx in enumerate(boxes):
        for j,bx2 in enumerate(boxes):
            if j<=i:
                continue
            
            if bx.overlaps(bx2):
                print(f"ERROR: [{i} {pattern[i][0]}] {bx} overlaps [{j} {pattern[j][0]} {bx2}")
        
    pp = pnl.Panel(output_file)
    
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
        
    board_poly = find_board_outline_tight(source_files, pattern, lines)
#        poly = src.get_board_outline(x_pos, y_pos, angle)
#        polys.append(no_holes(poly))
#        holes.extend(shp.Polygon(intr) for intr in poly.interiors)
    
#    board_poly = fill_gaps(polys)
    
#    if holes:
#        board_poly = board_poly.difference(shp.unary_union(holes))
    
    #board_poly_int = shp.Polygon([[(x+20)*1_000_000, (y+20)*1_000_000] for x,y in board_poly.exterior.coords])
    board_poly_int = sop.transform(lambda x,y: ((x+20)*1_000_000, (y+20)*1_000_000), board_poly)
    
    
    pp.appendSubstrate(board_poly_int)
    
    #print('handle lines?')
    
    for w,sx,sy,ex,ey in lines:
        if sx is None: sx=board_poly.bounds[0]
        if sy is None: sy=board_poly.bounds[1]
        if ex is None: ex=board_poly.bounds[2]
        if ey is None: ey=board_poly.bounds[3]
        add_line(pp.board, x0=sx,y0=sy,x1=ex,y1=ey, layers=[pcbnew.F_SilkS, pcbnew.B_SilkS], width=w)
    
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

def is_straight(a, b):
    return abs(a.x-b.x)<0.001 or abs(a.y-b.y)<0.001
        
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
        
        if is_straight(p0,q1) and is_straight(p1,q1):
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
        
    
    
