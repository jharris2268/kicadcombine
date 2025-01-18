import wx
import wx.dataview as dv

from .frame import KicadCombineFrameBase
from .preview import PreviewPanel
from .models import *

#from kicadcombine.gerber.sourcedesign import check_for_gerber_files, SourceDesign
from kicadcombine.kicad import Panel, SerializeError
import kicadcombine

import shapely as shp
import os.path, json




def none_or_float(x):
    try:
        return float(x)
    except:
        return None


        




class KicadCombineFrame(KicadCombineFrameBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
        self.bind_controls()
        self.prepare_view_columns()
        
        
        self.panel = Panel()
        
        self.source_designs_model=SourceDesignModel(self)
        self.source_designs_view.AssociateModel(self.source_designs_model)
        self.source_designs_model.DecRef()
        
        self.placements_model=PlacementsModel(self)
        self.placements_view.AssociateModel(self.placements_model)
        self.placements_model.DecRef()
        
        self.silkscreen_lines_model=SilkscreenLineModel(self)
        self.silkscreen_lines_view.AssociateModel(self.silkscreen_lines_model)
        self.silkscreen_lines_model.DecRef()
            
        self.preview = PreviewPanel(self, self.panel)

        
    def bind_controls(self):
        
        self.Bind(wx.EVT_MENU, self.on_new_design, self.new_menuitem)
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
        self.Bind(wx.EVT_RADIOBUTTON, self.on_board_size_radio_box, self.board_size_radio_box)
        
        self.Bind(wx.EVT_TEXT, self.update_board_size, self.board_width_entry)
        self.Bind(wx.EVT_TEXT, self.update_board_size, self.board_height_entry)
        
        self.Bind(wx.EVT_BUTTON, self.on_add_silkscreen_line_row, self.add_silkscreen_line_row)
        
        
        self.Bind(wx.EVT_BUTTON, self.on_delete_placement, self.delete_placement)
        self.Bind(wx.EVT_BUTTON, self.on_delete_source_design, self.delete_source_design)
        self.Bind(wx.EVT_BUTTON, self.on_delete_silkscreen_line, self.delete_silkscreen_line)
        
        self.Bind(wx.EVT_BUTTON, self.on_set_ouput_filename, self.set_ouput_filename_button)
        self.Bind(wx.EVT_BUTTON, self.on_make_panel, self.make_panel_button)
        
        
        
    
    def prepare_view_columns(self):
    
        self.source_designs_view.AppendTextColumn('Source Design',0)
        self.source_designs_view.AppendTextColumn('Num Cu Lyrs',1)
        self.source_designs_view.AppendTextColumn('Edge Cuts?',2)
        self.source_designs_view.AppendTextColumn('F_Paste?',3)
        self.source_designs_view.AppendTextColumn('Width',4)
        self.source_designs_view.AppendTextColumn('Height',5)

        
        for l,c in zip(('#', 'Source Design'), (0,1)):
            r=BackgroundColorDataViewRenderer(COLORS,120)
            column = dv.DataViewColumn(l, r, c, width=120)
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
        
        
        for l,c in zip(('Start X', 'Start Y', 'End X', 'End Y', 'Width'),(0,1,2,3,4)):
            renderer = TextCtrlDataViewRenderer(c, 120, mode=dv.DATAVIEW_CELL_EDITABLE)
            column = dv.DataViewColumn(l, renderer, c, width=120)
            self.silkscreen_lines_view.AppendColumn(column)
    
    
    def on_new_design(self, evt):
        
        if len(self.panel.placements)>0:
            
            save = wx.MessageDialog(self, f"Save Design?", "Save Design", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION).ShowModal()
            if save==wx.ID_CANCEL:
                return
            elif save==wx.ID_YES:
            
                self.on_save_design(evt)        
                
        self.panel.clear(False)
        self.placements_model.Cleared()
        self.silkscreen_lines_model.Cleared()
        self.update_board_size()
        self.output_filename_entry.ChangeValue('')
        self.set_board_size_radio()
    
    def on_exit(self, evt):
        if len(self.panel.placements)>0:
            
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
        
        
        duplicates = self.panel.open_source_designs([pathname])
        
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
        
        with_line = self.with_lines_checkbox.IsChecked()
        
        for item in items:
            
            self.panel.add_placement_location(item, location, angle, with_line)
        
        
                    
        
        self.silkscreen_lines_model.Cleared()
        self.placements_model.Cleared()
        
        if self.panel.placements:
            item = self.placements_model.ObjectToItem(self.panel.placements[-1].idx)
            self.placements_view.EnsureVisible(item)
        
        
        self.update_board_size()
    
    def on_add_silkscreen_line_row(self, evt):
        self.panel.add_silkscreen_line(None,None,None,None)
        self.silkscreen_lines_model.Cleared()
        self.update_board_size()
        
    
    def on_board_size_radio_specify(self, evt):
        #print('on_board_size_radio'), evt, evt.GetClientData(), evt.GetString(), evt.GetInt())
        self.panel.board_size_type='specify'
        self.update_board_size()
    
    def on_board_size_radio_box(self, evt):
        #print('on_board_size_radio'), evt, evt.GetClientData(), evt.GetString(), evt.GetInt())
        self.panel.board_size_type='box'
        self.update_board_size()
        
    def on_board_size_radio_tight(self, evt):
        #print('on_board_size_radio'), evt, evt.GetClientData(), evt.GetString(), evt.GetInt())
        self.panel.board_size_type='tight'
        self.update_board_size()
    
    def set_board_size_radio(self):
        if self.panel.board_size_type == 'specify':
            self.board_size_radio_specify.SetValue(True)
        elif self.panel.board_size_type == 'box':
            self.board_size_radio_box.SetValue(True)
        elif self.panel.board_size_type == 'tight':
            self.board_size_radio_tight.SetValue(True)
    
    def update_board_size(self, evt=None):
        
        self.panel.update_board_polygon()
        
        if self.panel.board_size_type == 'specify':
            self.board_width_entry.SetWindowStyle(0)#wx.TE_READONLY)
            self.board_height_entry.SetWindowStyle(0)#wx.TE_READONLY)
            
            
        else:
            self.board_width_entry.SetWindowStyle(wx.TE_READONLY)
            self.board_height_entry.SetWindowStyle(wx.TE_READONLY)
            self.board_width_entry.ChangeValue("%0.2f" % (round(self.panel.board_width+0.00499999, 2),))
            self.board_height_entry.ChangeValue("%0.2f" % (round(self.panel.board_height+0.00499999, 2),))
            
        self.board_area_label.SetLabel("area: %0.2f mm²" % self.panel.board_polygon.area)
        self.placements_model.Cleared()
        
        self.preview.draw()
    
    def on_delete_placement(self, evt):
        selections = self.placements_view.GetSelections()
        for i in selections:
            idx=self.placements_model.ItemToObject(i)
            self.panel.remove_placement(idx)
            
        self.placements_model.Cleared()
        self.silkscreen_lines_model.Cleared()
        self.update_board_size()
        
    def on_delete_source_design(self, evt):
        selections = self.source_designs_view.GetSelections()
        removed_placements=[]
        for i in selections:
            name=self.source_designs_model.ItemToObject(i)
            removed_placements.extend(self.panel.remove_source_design(name))
        
        self.source_designs_model.Cleared()    
        self.placements_model.Cleared()    
        self.silkscreen_lines_model.Cleared()
        if removed_placements:
            wx.MessageDialog(f"also removed {len(removed_placements)} placements", "Removed Placements", wx.CANCEL | wx.ICON_WARNING).ShowModal()
        self.update_board_size()
        
        
    def on_delete_silkscreen_line(self, evt):
        selections = self.silkscreen_line_view.GetSelections()
        items = [self.silkscreen_line_model.ItemToObject(i) for i in selections]
        for i in reversed(sorted(items)):
            self.panel.remove_silkscreen_line(i)            
        self.silkscreen_lines_model.Cleared()
        self.update_board_size()
        
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
            try:
                self.panel.serialize(pathname)
            except SerializeError as ex:
                wx.MessageDialog(self, ex.message, "Save Design", wx.OK | wx.ICON_ERROR).ShowModal()
    
    
    
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
            
            try:
                self.panel.deserialize(pathname, False)
            except SerializeError as ex:
                if ex.question is not None:
                    response = wx.MessageDialog(self, f"{ex.message}. {ex.question}", "Load Design", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION).ShowModal()
                    if response == wx.ID_YES:
                        try:
                            self.panel.deserialize(pathname, True)
                        except SerializeError as ex:
                            wx.MessageDialog(self, ex.message, "Load Design", wx.OK | wx.ICON_ERROR).ShowModal()
                    
                    
                else:
                    wx.MessageDialog(self, ex.message, "Load Design", wx.OK | wx.ICON_ERROR).ShowModal()
    
            
            self.output_filename_entry.ChangeValue(self.panel.output_filename or '')
        
            self.source_designs_model.Cleared()
            self.placements_model.Cleared()
            self.silkscreen_lines_model.Cleared()
            self.set_board_size_radio()
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
        if not self.panel.placements:
            wx.MessageDialog(self, f"No Placements Specifed", "No placements", wx.CANCEL | wx.ICON_WARNING).ShowModal()
            return
        
        if self.panel.output_filename is None or not os.path.splitext(self.panel.output_filename)[1]=='.kicad_pcb':
            if not self.on_set_ouput_filename(None):
                return
            response = wx.MessageDialog(self, f"Save to {self.output_filename}?", "Save", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION).ShowModal()
            if response != wx.ID_YES:
                return
        
        try:
            print(f"calling prepare_panel: {len(self.panel.placements)} placements, {len(self.panel.silkscreen_lines)} lines to {self.panel.output_filename}")
            self.panel.prepare_panel()
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
