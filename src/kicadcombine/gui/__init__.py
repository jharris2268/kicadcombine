import wx
import wx.dataview as dv

from .frame import KicadCombineFrameBase
from .preview import PreviewPanel
from .models import *

#from kicadcombine.gerber.sourcedesign import check_for_gerber_files, SourceDesign
from kicadcombine.kicad import get_source_files, find_board_outline_tight, prepare_panel
import kicadcombine

import shapely as shp
import os.path, json

box_overlaps = lambda A,B: A[2]>B[0] and A[3]>B[1] and B[2]>A[0] and B[3]>A[1]
box_contains = lambda A, B: B[0]>=A[0] and B[1]>=A[1] and B[2]<=A[2] and B[3]<=A[3]

            
class Placement:
    def __init__(self, idx, design, x_pos=0, y_pos=0, angle=0):
        self.idx=idx
        self.color = COLORS[idx % len(COLORS)]
        self.design=design
        self.x_pos=x_pos
        self.y_pos=y_pos
        self.angle=angle
        
        
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
        
    def set_value(self, col, val):
        if col==2:
            self.x_pos = float(val)
        elif col==3:
            self.y_pos = float(val)
        elif col==4:
            if not val in ('0','90','180','270'):
                raise Exception("wrong value for angle")
            self.angle = int(val)
        self.calc_board_outline()
    def get_value(self, col):
        if col==0:
            return f"{self.color}_{self.idx}"
        elif col==1:
            return f"{self.color}_{self.design.name}"
        elif col==2:
            return "%5.1f" % self.x_pos
        elif col==3:
            return "%5.1f" % self.y_pos
        elif col==4:
            return "%d" % self.angle
        elif col==5:
            return "%5.1f" % self.x_max
        elif col==6:
            return "%5.1f" % self.y_max
    
    
    def __len__(self):
        return 4
    
    def __getitem__(self, i):      
        
        if i==0: return self.design.name
        elif i==1: return self.x_pos
        elif i==2: return self.y_pos
        elif i==3: return self.angle

    def tuple(self):
        return (self[0],self[1],self[2],self[3])

    def calc_board_outline(self):
        self.board_outline = self.design.get_board_outline(self.x_pos, self.y_pos, self.angle)

    

    def within(self, other):
        if isinstance(other, shp.Polygon):
            return other.contains(self.board_outline)
        else:
            return box_contains(other, self.box)


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
        

COLORS = ['red','green','blue']


class KicadCombineFrame(KicadCombineFrameBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.Bind(wx.EVT_MENU, self.on_load_design, self.open_menuitem)
        self.Bind(wx.EVT_MENU, self.on_save_design, self.save_menuitem)        
        self.Bind(wx.EVT_MENU, self.on_exit,  self.exit_menuitem)
        
        self.Bind(wx.EVT_BUTTON, self.on_add_sourcedesign_row_one, self.add_sourcedesign_row_one)
        self.Bind(wx.EVT_BUTTON, self.on_add_sourcedesign_row_many, self.add_sourcedesign_row_many)
        
        self.Bind(wx.EVT_BUTTON, self.on_add_to_placements_right, self.add_to_placements_right)
        self.Bind(wx.EVT_BUTTON, self.on_add_to_placements_below, self.add_to_placements_below)
        self.Bind(wx.EVT_BUTTON, self.on_add_to_placements_new_row, self.add_to_placements_new_row)
        self.Bind(wx.EVT_BUTTON, self.on_add_to_placements_new_column, self.add_to_placements_new_column)
        
                
        self.Bind(wx.EVT_RADIOBUTTON, self.on_board_size_radio_specify, self.board_size_radio_specify)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_board_size_radio_tight, self.board_size_radio_tight)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_board_size_radio_fit, self.board_size_radio_fit)
        
        self.Bind(wx.EVT_TEXT, self.update_board_size, self.board_width_entry)
        self.Bind(wx.EVT_TEXT, self.update_board_size, self.board_height_entry)
        
        self.Bind(wx.EVT_BUTTON, self.on_delete_placement, self.delete_placement)
        self.Bind(wx.EVT_BUTTON, self.on_delete_source_design, self.delete_source_design)
        
        self.Bind(wx.EVT_BUTTON, self.on_set_ouput_filename, self.set_ouput_filename_button)
        self.Bind(wx.EVT_BUTTON, self.on_make_panel, self.make_panel_button)
        
        self.source_designs = {}
        self.placements = []
        self.silkscreen_lines = []
        
        self.board_size_type = 'fit'
        self.board_width=0
        self.board_height=0
        self.board_polygon = shp.GeometryCollection()
        
        self.source_designs_view.AppendTextColumn('Source Design',0)
        self.source_designs_view.AppendTextColumn('Num Cu Lyrs',1)
        self.source_designs_view.AppendTextColumn('Edge Cuts?',2)
        self.source_designs_view.AppendTextColumn('F_Paste?',3)
        self.source_designs_view.AppendTextColumn('Width',4)
        self.source_designs_view.AppendTextColumn('Height',5)
        #self.source_designs_view.AppendToggleColumn('Select',6, dv.DATAVIEW_CELL_ACTIVATABLE)
        
        self.source_designs_model=SourceDesignModel(self.source_designs)
        self.source_designs_view.AssociateModel(self.source_designs_model)
        self.source_designs_model.DecRef()
        
        #self.placements_view.AppendTextColumn('Source Design',0)
        
        
        for l,c in zip(('#', 'Source Design'), (0,1)):
            r=BackgroundColorDataViewRenderer(COLORS,120)
            column = dv.DataViewColumn('Source Design', r, c, width=120)
            self.placements_view.AppendColumn(column)
        
        for l,c in zip(('X pos','Y pos', 'Angle'), (2,3,4)):
            renderer=None
            if c in (2,3):
                renderer = TextCtrlDataViewRenderer(c, 120, mode=dv.DATAVIEW_CELL_EDITABLE)
            else:
                renderer = dv.DataViewChoiceRenderer(['0','90','180','270'],mode=dv.DATAVIEW_CELL_EDITABLE)
            
            column = dv.DataViewColumn(l, renderer, c, width=120)
            #column.Alignment = wx.ALIGN_RIGHT
            self.placements_view.AppendColumn(column)
        
        self.placements_view.AppendTextColumn('X max', 5)
        self.placements_view.AppendTextColumn('Y max', 6)
        self.placements_view.AppendTextColumn('Overlaps', 7)
        
        self.placements_model=PlacementsModel(self, self.placements)
        self.placements_view.AssociateModel(self.placements_model)
        self.placements_model.DecRef()
        
        
        self.silkscreen_lines = []
        self.silkscreen_lines_model=SilkscreenLineModel(self, self.silkscreen_lines)
        
        
        for l,c in zip(('Start X', 'Start Y', 'End X', 'End Y', 'Width'),(0,1,2,3,4)):
            renderer = TextCtrlDataViewRenderer(c, 120, mode=dv.DATAVIEW_CELL_EDITABLE)
            column = dv.DataViewColumn(l, renderer, c, width=120)
            self.silkscreen_lines_view.AppendColumn(column)
        
        self.silkscreen_lines_view.AssociateModel(self.silkscreen_lines_model)
        self.silkscreen_lines_model.DecRef()
            
                
        self.spacing=1
        
        self.preview = PreviewPanel(self)
        
        self.output_filename = None
        
    
        
    def on_exit(self, evt):
        if len(self.placements)>0:
            
            save = wx.MessageDialog(self, f"Save Design?", "Save Design", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION).ShowModal()
            if save==wx.ID_CANCEL:
                return
            elif save==wx.ID_YES:
            
                self.on_save_design(evt)        
            
        
        self.Close(True)
    
    def on_add_sourcedesign_row_many(self, evt):
        
        with wx.DirDialog(self,
            "Open all kicad_pcb under directory",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
            defaultPath = '/home/james/elec/misc/'            
            ) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = dirDialog.GetPath()
            
            self.add_source_design(pathname)
    
    def on_add_sourcedesign_row_one(self, evt):
        
        with wx.FileDialog(self,
            "Open kicad_pcb",
            style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST,
            defaultDir = '/home/james/elec/misc/',
            wildcard="kicad_pcb files (*.kicad_pcb)|*.kicad_pcb"      
            ) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            
            self.add_source_design(pathname)
            
    def add_source_design(self, pathname):
        print("add_sourcedesign", pathname)
        
        new_source_designs, duplicates = get_source_files([pathname])
        for x,y in new_source_designs.items():
            if x in self.source_designs:
                duplicates.append((x,y))
            else:
                self.source_designs[x]=y
        if duplicates:
            wx.MessageDialog(self,
                "%d duplicated source designs:\n%s" % (len(duplicates), '\n'.join(str(y) for x,y in duplicates)),
                "Duplicated source designs",
                wx.CANCEL | wx.ICON_WARNING
            ).ShowModal()
        self.source_designs_model.Cleared()
    
    
    def on_add_to_placements_right(self, evt):
        self.add_placement('right')
    
    def on_add_to_placements_below(self, evt):
        self.add_placement('below')
    
    def on_add_to_placements_new_row(self, evt):
        self.add_placement('new_row')
    
    def on_add_to_placements_new_column(self, evt):
        self.add_placement('new_column')
    
    def add_placement(self, location):
        
        #print(self.source_designs_model.selected)
        selections = self.source_designs_view.GetSelections()
        
        items=[self.source_designs_model.ItemToObject(i) for i in selections]
        
        
        angle = int(self.add_placement_angle.GetString(self.add_placement_angle.Selection))
        
        #print('on_add_to_placements',selections, items, location)
        
        
        for item in items:
            sd=self.source_designs[item]
            
            x, y = 0, 0
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
                    
                    
            placement=Placement(len(self.placements), sd, x, y, angle)
            
            self.placements.append(placement)
            if self.with_lines_checkbox.IsChecked():
                if location=='right' and x>0:
                    self.silkscreen_lines.append(SilkscreenLine.vertical(self, placement.x_pos, placement.y_pos, placement.y_max))
                elif location=='below' and y>0:
                    self.silkscreen_lines.append(SilkscreenLine.horizontal(self, placement.y_pos, placement.x_pos, placement.x_max))
                elif location=='new_column' and x>0:
                    self.silkscreen_lines.append(SilkscreenLine.vertical(self, placement.x_pos))
                elif location=='new_row' and y>0:
                    self.silkscreen_lines.append(SilkscreenLine.horizontal(self, placement.y_pos))
                    
        
        self.silkscreen_lines_model.Cleared()
        self.placements_model.Cleared()
        
        if len(self.placements)>1:
            item = self.placements_model.ObjectToItem(len(self.placements)-1)
            self.placements_view.EnsureVisible(item)
        
        
        self.update_board_size()
        
        
    
    def on_board_size_radio_specify(self, evt):
        #print('on_board_size_radio'), evt, evt.GetClientData(), evt.GetString(), evt.GetInt())
        self.board_size_type='specify'
        self.update_board_size()
    
    def on_board_size_radio_fit(self, evt):
        #print('on_board_size_radio'), evt, evt.GetClientData(), evt.GetString(), evt.GetInt())
        self.board_size_type='fit'
        self.update_board_size()
        
    def on_board_size_radio_tight(self, evt):
        #print('on_board_size_radio'), evt, evt.GetClientData(), evt.GetString(), evt.GetInt())
        self.board_size_type='tight'
        self.update_board_size()
    
    def update_board_size(self, evt=None):
        if self.board_size_type == 'specify':
            self.board_width_entry.SetWindowStyle(0)#wx.TE_READONLY)
            self.board_height_entry.SetWindowStyle(0)#wx.TE_READONLY)
            
            self.board_width = float(self.board_width_entry.GetValue() or 0)
            self.board_height = float(self.board_height_entry.GetValue() or 0)
            self.board_polygon = shp.box(0,0,self.board_width, self.board_height)
            
            holes = [shp.Polygon(interior) for pl in self.placements for interior in pl.board_outline.interiors]
            if holes:
                self.board_polygon = self.board_polygon.difference(shp.unary_union(holes))
            
        else:
            self.board_width_entry.SetWindowStyle(wx.TE_READONLY)
            self.board_height_entry.SetWindowStyle(wx.TE_READONLY)
            
            
            if not self.placements:
                self.board_width = 0
                self.board_height = 0
                self.board_polygon = shp.GeometryCollection()
            elif self.board_size_type == 'fit':
                self.board_width = max(p.x_max for p in self.placements)
                self.board_height = max(p.y_max for p in self.placements)
                self.board_polygon = shp.box(0,0,self.board_width, self.board_height)
                
                holes = [shp.Polygon(interior) for pl in self.placements for interior in pl.board_outline.interiors]
                if holes:
                    self.board_polygon = self.board_polygon.difference(shp.unary_union(holes))
                
                #print(self.placements, self.board_width, self.board_height)
            elif self.board_size_type == 'tight':
                self.board_polygon = find_board_outline_tight(self.source_designs, [p.tuple() for p in self.placements], [])
                self.board_width, self.board_height = self.board_polygon.bounds[2:]
            
            self.board_width_entry.ChangeValue("%0.2f" % (round(self.board_width+0.00499999, 2),))
            self.board_height_entry.ChangeValue("%0.2f" % (round(self.board_height+0.00499999, 2),))
            
        self.board_area_label.SetLabel("area: %0.2f mm²" % self.board_polygon.area)
        self.placements_model.Cleared()
        
        self.preview.draw()
    
    def on_delete_placement(self, evt):
        selections = self.placements_view.GetSelections()
        
        items=[self.placements_model.ItemToObject(i) for i in selections]
        print("remove placements", items)
        for i in reversed(sorted(items)):
            self.placements.pop(i)
        
        self.placements_model.Cleared()
    
    def on_delete_source_design(self, evt):
        selections = self.source_designs_view.GetSelections()
        
        items=[self.source_designs_model.ItemToObject(i) for i in selections]
        print("remove source_designs", items)
        for i in items:
            self.source_designs.pop(i)
        
        self.source_designs_model.Cleared()    
    
    def on_save_design(self, evt):
        with wx.FileDialog(self,
            "Save design json file",
            style=wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE,
            defaultDir = '/home/james/elec/misc/',
            wildcard="design json files (*.json)|*.json"
            ) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            self.save_design(pathname)
    
    def save_design(self, pathname):
        
        a,b=os.path.splitext(pathname)
        if b=='':
            pathname = pathname+'.json'
        
        elif b != '.json':
            wx.MessageDialog(self, f"design file should have extension '.json'", "Wrong Extension", wx.CANCEL | wx.ICON_ERROR).ShowModal()
            return
        
        design = {
            'type': 'kicadcombine_design', 
            'source_designs': [],
            'placements': [],
            'silkscreen_lines': [],
            'output_filename': self.output_filename,
            'board_size': None
        }
        sds=set()
        for placement in self.placements:
            if not placement.design.name in sds:
                design['source_designs'].append({
                    'name': placement.design.name, 
                    'path': placement.design.path,
                    'checksum': placement.design.checksum,
                    'width': placement.design.width,
                    'height': placement.design.height,
                })
            design['placements'].append({
                'source_design': placement.design.name,
                'x_pos': placement.x_pos,
                'y_pos': placement.y_pos,
                'angle': placement.angle
            })
        for line in self.silkscreen_lines:
            design['silkscreen_lines'].append({
                'x0': line.x0,
                'y0': line.y0,
                'x1': line.x1,
                'y1': line.y1,
                'width': line.width
            })
        
        if self.board_size_type == 'specify':
            design['board_size'] = ['specify', self.board_width, self.board_height]
        else:
            design['board_size'] = [self.board_size_type, None, None]
        
        json.dump(design, open(pathname, 'w'), indent=4)
    
    def on_load_design(self, evt):
        with wx.FileDialog(self,
            "Load design json file",
            style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST,
            defaultDir = '/home/james/elec/misc/',
            wildcard="design json files (*.json)|*.json"
            ) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            self.load_design(pathname)
    
    
    def load_design(self, pathname):
        
        if not os.path.exists(pathname):
            wx.MessageDialog(self, f"path {pathname} does not exist", "Error", wx.OK | wx.ICON_ERROR).ShowModal()
            return
            
        design=None
        try:
            design = json.load(open(pathname))
        except:
            wx.MessageDialog(self, f"file {pathname} not a json file", "Error", wx.OK | wx.ICON_ERROR).ShowModal()
            return
        
        wrong_format = lambda: wx.MessageDialog(self, f"file {pathname} not a kicadcombine json file", "Error", wx.OK | wx.ICON_ERROR).ShowModal()
        
        if not ('type' in design and 'source_designs' in design
                and 'placements' in design and 'silkscreen_lines' in design
                and 'board_size' in design and 'output_filename' in design):
            wrong_format()
            return 
        if not design['type']=='kicadcombine_design':
            wrong_format()
            return
        
        new_source_designs={}
        new_placements=[]
        new_silkscreen_lines=[]
        
        for sd in design['source_designs']:
            if not ('name' in sd and 'path' in sd and 'checksum' in sd and 'width' in sd and 'height' in sd):
                wrong_format()
                return
            if sd['name'] in self.source_designs:
                existing_sd = self.source_designs[sd['name']]
                
                if not sd['checksum']==existing_sd.checksum:
                    size_same = sd['height']==existing_sd.height and sd['width']==existing_sd.width
                
                    response = wx.MessageDialog(self, 
                        f"Source Design {sd['name']} changed, size {'same' if size_same else 'different'}. Continue?",
                        f"Source Design changed",
                        wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION).ShowModal()
                    if response != wx.ID_YES:
                        return
                
            else:
                if not os.path.exists(sd['path']):
                    wx.MessageDialog(self, f"file {pathname} not a kicadcombine json file", "Error", wx.OK | wx.ICON_ERROR).ShowModal()
                    
                nsd = SourceDesign(sd['name'],sd['path'])
                if sd['checksum'] != nsd.checksum:
                    size_same = sd['height']==nsd.height and sd['width']==nsd.width
                
                    response = wx.MessageDialog(self, 
                        f"Source Design {sd['name']} changed, size {'same' if size_same else 'different'}. Continue?",
                        f"Source Design changed",
                        wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION).ShowModal()
                    if response != wx.ID_YES:
                        return
                new_source_designs[nsd.name]=nsd
            
        for pl in design['placements']:
            if not ('source_design' in pl and 'x_pos' in pl and 'y_pos' in pl and 'angle' in pl):
                wrong_format()
                return
            
            pl_design=self.source_designs.get(pl['source_design'])
            if not pl_design:
                pl_design=new_source_designs.get(pl['source_design'])
            if not pl_design:
                wx.MessageDialog(self, f"Source Design {pl['source_design']} not specified", "Error", wx.OK | wx.ICON_ERROR).ShowModal()
                return
            
            new_placements.append(Placement(len(new_placements), pl_design, pl['x_pos'], pl['y_pos'], pl['angle']))
        for ln in design['silkscreen_lines']:
            if not ('x0' in ln and 'y0' in ln and 'x1' in ln and 'y1' in ln and 'width' in ln):
                wrong_format()
                return
            new_silkscreen_lines.append(SilkscreenLine(self, ln['x0'], ln['y0'], ln['x1'], ln['y1'], ln['width']))
        
        self.board_size_type, self.board_width, self.board_height = design['board_size']
        
        for n,sd in new_source_designs.items():
            self.source_designs[n]=sd
        self.placements.clear()
        for pl in new_placements:
            self.placements.append(pl)
        self.silkscreen_lines.clear()
        for ln in new_silkscreen_lines:
            self.silkscreen_lines.append(ln)
        
        self.output_filename = design['output_filename']
        self.output_filename_entry.ChangeValue(self.output_filename or '')
        
        self.source_designs_model.Cleared()
        self.placements_model.Cleared()
        self.silkscreen_lines_model.Cleared()
        self.update_board_size()
        
        
    
    def on_set_ouput_filename(self, evt):
        with wx.FileDialog(self,
            "Set output kicad project",
            style=wx.FD_OVERWRITE_PROMPT | wx.FD_SAVE,
            defaultDir = '/home/james/elec/misc/',
            wildcard="design json files (*.kicad_pcb)|*.kicad_pcb"
            ) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return False
            
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            
            xx,c = os.path.split(pathname)
            a,b = os.path.split(xx)
            
            if b!=os.path.splitext(c)[0]:
                #create dir...
                dd=os.path.splitext(pathname)[0]
                if not os.path.exists(dd):
                    os.mkdir(dd)
                pathname = os.path.join(dd, c)
            if os.path.splitext(c)[1] == '':
                pathname=pathname + '.kicad_pcb'
            if os.path.splitext(c)[1] != '.kicad_pcb':
                wx.MessageDialog(self, f"output file should have extension '.kicad_pcb'", "Wrong Extension", wx.CANCEL | wx.ICON_ERROR).ShowModal()
                return
            self.output_filename = pathname
            self.output_filename_entry.ChangeValue(pathname)
        return True
    def on_make_panel(self, evt):
        print("calling on_make_panel")
        if not self.placements:
            wx.MessageDialog(self, f"No Placements Specifed", "No placements", wx.CANCEL | wx.ICON_WARNING).ShowModal()
            return
        
        if self.output_filename is None or not os.path.splitext(self.output_filename)[1]=='.kicad_pcb':
            if not self.on_set_ouput_filename(None):
                return
            response = wx.MessageDialog(self, f"Save to {self.output_filename}?", "Save", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION).ShowModal()
            if response != wx.ID_YES:
                return
        
        try:
            print(f"calling prepare_panel: {len(self.placements)} placements, {len(self.silkscreen_lines)} lines to {self.output_filename}")
            prepare_panel(
                self.source_designs, [p.tuple() for p in self.placements],
                [l.tuple() for l in self.silkscreen_lines], self.board_polygon,
                self.output_filename, False)
        except BaseException as ex:
            print('failed', ex)
            wx.MessageDialog(self, f"make panel failed: {str(ex)}", "Failed", wx.CANCEL | wx.ICON_ERROR).ShowModal()
            
           
        
        
            
            
            
        
        
        
def run_gui():
    app=wx.App()
    frame=KicadCombineFrame(None)
    for loc in kicadcombine.EXAMPLE_LOCATIONS:
        frame.add_source_design(loc)
    
    
    frame.Show()
    
    app.MainLoop()
