import wx
import wx.dataview as dv

from .frame import GerberMergeFrameBase
from kicadcombine.gerber.sourcedesign import check_for_gerber_files, SourceDesign

import os.path

class SourceDesignModel(dv.PyDataViewModel):
    def __init__(self, source_designs):
        super().__init__()
        self.source_designs=source_designs
        self.selected=set([])
        
    def GetChildren(self, parent, children):
        for k in sorted(self.source_designs):
            children.append(self.ObjectToItem(k))
        
        return len(self.source_designs)
    
    def GetColumnCount(self):
        return 7
    
    def GetValue(self, item, col):
        name=self.ItemToObject(item)
        obj = self.source_designs[name]
        if col==0:
            return obj.name
        elif col==1:
            return "%d" % obj.num_copper_layers
        elif col==2:
            return 'y' if obj.has_edge_cuts else 'n'
        elif col==3:
            return 'y' if obj.has_f_paste else 'n'
        elif col==4:
            return "%0.1f" % obj.width
        elif col==5:
            return "%0.1f" % obj.height
        elif col==6:
            return name in self.selected
    
    def SetValue(self, value, item, col):
        name=self.ItemToObject(item)
        if value:
            self.selected.add(name)
        else:
            if name in self.selected:
                self.selected.remove(name)
        print('selected',self.selected)
    def IsContainer(self, item):
        return False
    
    def GetParent(self, item):
        return dv.DataViewItem(None)
            

class GerberMergeFrame(GerberMergeFrameBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.Bind(wx.EVT_MENU, self.on_open, self.open_menuitem)
        self.Bind(wx.EVT_MENU, self.on_save, self.save_menuitem)        
        self.Bind(wx.EVT_MENU, self.on_exit,  self.exit_menuitem)
        
        self.Bind(wx.EVT_BUTTON, self.on_add_sourcedesign_row, self.add_sourcedesign_row)
        
        self.source_designs = {}
        
        self.placements = []
        self.silkscreen_lines = []

            
        self.source_designs_view.AppendTextColumn('Source Design',0)
        self.source_designs_view.AppendTextColumn('Num Cu Lyrs',1)
        self.source_designs_view.AppendTextColumn('Edge Cuts?',2)
        self.source_designs_view.AppendTextColumn('F_Paste?',3)
        self.source_designs_view.AppendTextColumn('Width',4)
        self.source_designs_view.AppendTextColumn('Height',5)
        self.source_designs_view.AppendToggleColumn('Delete',6, dv.DATAVIEW_CELL_ACTIVATABLE)
        
        self.source_designs_model=SourceDesignModel(self.source_designs)
        self.source_designs_view.AssociateModel(self.source_designs_model)
        self.source_designs_model.DecRef()
        
    
    def on_open(self, evt):
        pass
    
    def on_save(self, evt):
        pass
        
    def on_exit(self, evt):
        self.Close(True)
    
    def on_add_sourcedesign_row(self, evt):
        
        with wx.DirDialog(self,
            "Open Gerber file directory",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
            defaultPath = '/home/james/elec/misc/'            
            ) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = dirDialog.GetPath()
            
            self.add_source_design(pathname)
            
    def add_source_design(self, pathname):
        print("add_sourcedesign", pathname)
        if not check_for_gerber_files(pathname):
                
            if os.path.exists(os.path.join(pathname, 'gerbers')):
                return self.add_source_design(os.path.join(pathname, 'gerbers'))            
        
            wx.MessageBox(f"did not find any gerber files in {pathname}")
            return
        
        
        sd = SourceDesign.from_path(pathname)
        self.source_designs[sd.name] = sd
        
        self.source_designs_model.Cleared()
        
        
        #self.source_designs_view.AppendItem([
        #    sd.name,
        #    '%d' % sd.num_copper_layers,
        #    'y' if sd.has_edge_cuts else 'n',
        #    'y' if sd.has_f_paste else 'n',
        #    "%0.1f" % sd.width,
        #    "%0.1f" % sd.height,
        #    False
        #])
        
        
        
    
    
    
            
            

def run_gui():
    app=wx.App()
    frame=GerberMergeFrame(None)
    frame.Show()
    
    app.MainLoop()
