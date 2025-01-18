import pcbnew
import kikit.panelize as pnl
import kikit.substrate as subs

import os.path
import shapely as shp
import shapely.ops as sop
from math import sin, cos, pi
import numpy as np

from .boardoutline import find_board_outline_polygon
from .mergeboardoutline import find_board_outline_tight, make_vec

from .silkscreenline import SilkscreenLine
from .placements import Placement
from .sourcedesign import SourceDesign, open_source_designs
from .serialize import serialize_panel, deserialize_panel, SerializeError


from kicadcombine.utils import sha256_digest

class Panel:
    def __init__(self):
        
        self.source_designs = {}
        self._placements = {}
        self.silkscreen_lines = []
        
        self.other_params_init()
    
    def other_params_init(self):
        self.board_size_type = 'box'
        self.board_width=0
        self.board_height=0
        self.board_polygon = shp.GeometryCollection()
        self.spacing=1
        self.output_filename = None
        self.bake_text=False
        
        self.next_placement=0
    
    def clear(self, clear_source_designs=False):
        
        if clear_source_designs:
            self.source_designs.clear()
        self._placements.clear()
        self.silkscreen_lines.clear()
        self.other_params_init()
        
    
    def open_source_designs(self, dirs):
        if isinstance(dirs, str):
            dirs = [dirs]
        
        duplicates = open_source_designs(self.source_designs, dirs)
        if duplicates:
            raise Exception("have %d duplicate source designs?: %s" % '; '.join(a for a,b in duplicates))
        
    
    def check_placements(self):
        self.update_board_polygon()
        
        errors = []
        for i,pl1 in enumerate(self.placements):
            if not self.board_polygon.contains(pl1.board_outline):
                errors.append(('boundary', board, pl1))
            for j,pl2 in enumerate(self.placements):
                if j<=i: continue
                
                if pl1.board_outline.overlaps(pl2.board_outline):
                    errors.append(('overlap', pl1, pl2))
        
        return errors
    
    def update_board_polygon(self):
        if self.board_size_type=='box':
            self.board_width=max(p.x_max for p in self.placements) if self.placements else 0
            self.board_height=max(p.y_max for p in self.placements) if self.placements else 0
            self.board_polygon = shp.box(0,0,self.board_width, self.board_height)
        elif self.board_size_type=='specify':
            self.board_polygon = shp.box(0,0,self.board_width, self.board_height)
        elif self.board_size_type=='tight':
            self.board_polygon = find_board_outline_tight(self.placements)
            self.board_width, self.board_height=self.board_polygon.bounds[2:]
        else:
            raise Exception(f"unexpected board_size_type {self.board_size_type}")
    
    def get_placement(self, idx):
        return self._placements.get(idx)
    
    @property
    def placements(self):
        return [q for p,q in sorted(self._placements.items())]
    
    def add_placement(self, design, x_pos, y_pos, angle=0):
        
        placement = Placement(
                self.next_placement,
                self.source_designs[design],
                x_pos,
                y_pos,
                angle
            )
        self._placements[self.next_placement] = placement
        self.next_placement+=1
        return placement
    
    def add_placement_location(self, design, location, angle, with_line):
        x,y=0,0
        if len(self.placements)>0:
            if location=='right':
                x = self.placements[-1].x_max+self.spacing
                y = self.placements[-1].y_pos
            elif location=='below':
                x = self.placements[-1].x_pos
                y = self.placements[-1].y_max+self.spacing
            
            elif location=='new_column':
                x = max(p.x_max for p in self.placements)+self.spacing
                y = min(p.y_pos for p in self.placements)
                
            elif location=='new_row':
                x = min(p.x_pos for p in self.placements)
                y = max(p.y_max for p in self.placements)+self.spacing
                
                
        placement=self.add_placement(design, x, y, angle)
        
        if with_line:
            if location=='right' and x>0:
                placement.silkscreen_line=self.add_silkscreen_line_vertical(placement.x_pos-self.spacing/2, placement.y_pos, placement.y_max)
            elif location=='below' and y>0:
                placement.silkscreen_line=self.add_silkscreen_line_horizontal(placement.y_pos-self.spacing/2, placement.x_pos, placement.x_max)
            elif location=='new_column' and x>0:
                placement.silkscreen_line=self.add_silkscreen_line_vertical(self, placement.x_pos-self.spacing/2)
            elif location=='new_row' and y>0:
                placement.silkscreen_line=self.add_silkscreen_line_horizontal(placement.y_pos-self.spacing/2)
                
            
        return placement
    
    def remove_placement(self, idx):
        line=self._placements[idx].silkscreen_line
        self._placements.pop(idx)
        if not line is None:
            self.silkscreen_lines.remove(line)
        
    def remove_source_design(self, name):
        sd = self.source_designs[name]
        pp = [p for p,q in self._placements.items() if q.design==sd]
        for p in pp:
            self._placements.pop(p)
        
        return pp
        
    
    
    def add_silkscreen_line(self, x0, y0, x1, y1, width=None):
        self.silkscreen_lines.append(
            SilkscreenLine(
                self,
                x0,
                y0,
                x1,
                y1,
                width
            )
        )
        return self.silkscreen_lines[-1]
    def add_silkscreen_line_vertical(self, x_pos, y0=None, y1=None, width=None):
        self.silkscreen_lines.append(
            SilkscreenLine(
                self,
                x_pos,
                y0,
                x_pos,
                y1,
                width
            )
        )
        return self.silkscreen_lines[-1]
    def add_silkscreen_line_horizontal(self, y_pos, x0=None, x1=None, width=None):
        self.silkscreen_lines.append(
            SilkscreenLine(
                self,
                x0,
                y_pos,
                x1,
                y_pos,
                width
            )
        )
        return self.silkscreen_lines[-1]
        
    def prepare_panel(self):
        
        errors = self.check_placements()
        if errors:
            raise Exception(
                "have %d board placement errors\n%s" % (
                    len(errors),
                    "\n".join("%s %s %s" % (a,b,c) for a,b,c in errors)
                ))
                
        
        pp = pnl.Panel(self.output_filename)
        
        for src, x_pos, y_pos,angle in self.placements:
            #print(f"adding {srcn} @ {x_pos} {y_pos}")   
            
            src_bounds=src.bounds.rotate(angle)
            pos_vec = make_vec(x_pos+20+src_bounds.center_x, y_pos+20+src_bounds.center_y)
            pp.appendBoard(
                src.path,
                pos_vec,
                rotationAngle=pcbnew.EDA_ANGLE(angle),
                origin=pnl.Origin.Center,
                tolerance=50_000,
                inheritDrc=False,
                bakeText=self.bake_text)


        board_poly_int = sop.transform(lambda x,y: ((x+20)*1_000_000, (y+20)*1_000_000), self.board_polygon)
        
        
        pp.appendSubstrate(board_poly_int)
        
        for ln in self.silkscreen_lines:
            ln.add_to_board(pp.board)
            
            
        pp.save()
    
    def serialize(self, filename):
        serialize_panel(self, filename)
        
    def deserialize(self, filename, allow_changes):
        
        deserialize_panel(self, filename, allow_changes)
        
     

