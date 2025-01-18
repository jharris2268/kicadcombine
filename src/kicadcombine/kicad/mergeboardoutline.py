
import shapely as shp, shapely.ops as sop
import pcbnew


from .boardoutline import iter_pairs

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
        
        #if is_straight(p0,q1) and is_straight(p1,q1):
        if d0 < max_gap and d1 < max_gap:
        
                #add polygon from four points
            result.append(shp.Polygon([p0,p1,q1,q0,p0]))

    for (p0,p1) in iter_pairs(iter_points(boundary_right)):
        q0,d0 = find_closest(boundary_left, p0)
        q1,d1 = find_closest(boundary_left, p1)
        
        #if is_straight(p0,q1) and is_straight(p1,q1):
        if d0 < max_gap and d1 < max_gap:
                #add polygon from four points
            result.append(shp.Polygon([p0,p1,q1,q0,p0]))
    return result
    
    
    
def join_poly_inner(left, right, max_gap=5):
    
    boundary_left = left.boundary
    boundary_right = right.boundary   
    
    result = []
    for (p0, p1) in iter_pairs(iter_points(boundary_left)):
        if boundary_right.distance(p0)>max_gap or boundary_right.distance(p1) > max_gap:
            continue
            
        q0,d0 = find_closest(boundary_right, p0)
        q1,d1 = find_closest(boundary_right, p1)
        if is_straight(p0,q1) and is_straight(p1,q1):
            if d0 < max_gap and d1 < max_gap:        
                #add polygon from four points
                result.append(shp.Polygon([p0,p1,q1,q0,p0]))
    
    return result

def join_poly_p(left, right, max_gap=5):
    return join_poly_inner(left, right,max_gap)+join_poly_inner(right,left,max_gap)

    
    
    
    
    
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


def make_vec(x, y):
    return pcbnew.VECTOR2I( int(x*1_000_000+0.5), int(y*1_000_000+0.5))
    


    
    
    
    



def find_board_outline_tight(placements):
    
    polys = []
    holes = []
    
    for pl in placements:
        poly = pl.board_outline
        polys.append(no_holes(poly))
        holes.extend(shp.Polygon(intr) for intr in poly.interiors)
    
    board_poly = fill_gaps(polys)
    
    if holes:
        board_poly = board_poly.difference(shp.unary_union(holes))
    
    return board_poly
