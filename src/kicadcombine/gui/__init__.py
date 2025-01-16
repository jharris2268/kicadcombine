import wx
import wx.dataview as dv

from .frame import KicadCombineFrameBase
from .preview import PreviewPanel
from .models import *

#from kicadcombine.gerber.sourcedesign import check_for_gerber_files, SourceDesign
from kicadcombine.kicad import get_source_files, find_board_outline_tight
import kicadcombine

import shapely as shp
import os.path

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
        if i==0: return self.x0
        if i==1: return self.y0
        if i==2: return self.x1
        if i==3: return self.y1
        if i==4: return self.width
    
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
        
        self.Bind(wx.EVT_MENU, self.on_open, self.open_menuitem)
        self.Bind(wx.EVT_MENU, self.on_save, self.save_menuitem)        
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
            if c in (1,2):
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
        
    
    def on_open(self, evt):
        pass
    
    def on_save(self, evt):
        pass
        
    def on_exit(self, evt):
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
        
        new_source_designs = get_source_files([pathname])
                
        self.source_designs.update(new_source_designs)
        
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
                #print(self.placements, self.board_width, self.board_height)
            elif self.board_size_type == 'tight':
                self.board_polygon = find_board_outline_tight(self.source_designs, self.placements, [])
                self.board_width, self.board.height = self.board_polygon.bounds[2:]
            
            self.board_width_entry.ChangeValue("%0.2f" % (round(self.board_width+0.00499999, 2),))
            self.board_height_entry.ChangeValue("%0.2f" % (round(self.board_height+0.00499999, 2),))
            
        self.board_area_label.SetLabel("area: %0.2f mm²" % self.board_polygon.area)
        self.placements_model.Cleared()
        
        self.preview.draw()
    
    def on_delete_placement(self, evt):
        selections = self.placements_view.GetSelections()
        
        items=[self.placements_model.ItemToObject(i) for i in selections]
        print("remove placements", items)
        for i in sitems:
            self.placements.pop(self.placements.index(i))
        
        self.placements_model.Cleared()
    
    def on_delete_source_design(self, evt):
        selections = self.source_designs_view.GetSelections()
        
        items=[self.source_designs_model.ItemToObject(i) for i in selections]
        print("remove source_designs", items)
        for i in items:
            self.source_designs.pop(i)
        
        self.source_designs_model.Cleared()    
        
        
def run_gui():
    app=wx.App()
    frame=KicadCombineFrame(None)
    for loc in kicadcombine.EXAMPLE_LOCATIONS:
        frame.add_source_design(loc)
    
    
    frame.Show()
    
    app.MainLoop()
