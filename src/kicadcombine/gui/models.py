import wx.dataview as dv
import wx


    
    
class SourceDesignModel(dv.PyDataViewModel):
    def __init__(self, source_designs):
        super().__init__()
        self.source_designs=source_designs
        
        
    def GetChildren(self, parent, children):
        for k in sorted(self.source_designs):
            children.append(self.ObjectToItem(k))
        
        return len(self.source_designs)
    
    def GetColumnCount(self):
        return 6
    
    def GetValue(self, item, col):
        name=self.ItemToObject(item)
        obj = self.source_designs[name]
        if col==0:
            return obj.name
        elif col==1:
            return "%d" % obj.num_copper_layers
        elif col==2:
            #return 'y' if obj.has_edge_cuts else 'n'
            return 'y'
        elif col==3:
            return 'y' if obj.has_f_paste else 'n'
        elif col==4:
            return "%0.1f" % obj.width
        elif col==5:
            return "%0.1f" % obj.height
        #elif col==6:
        #    return name in self.selected
    
    def SetValue(self, value, item, col):
        return True
        
    def IsContainer(self, item):
        return False
    
    def GetParent(self, item):
        return dv.DataViewItem(None)


class PlacementsModel(dv.PyDataViewModel):
    def __init__(self, parent, placements):
        super().__init__()
        
        self.parent=parent
        self.placements = placements
        
        
    def GetChildren(self, parent, children):
        for i in range(len(self.placements)):
            children.append(self.ObjectToItem(i))
        
        return len(self.placements)
    
    def GetColumnCount(self):
        return 7
    
    def GetValue(self, item, col):
        idx=self.ItemToObject(item)
        obj=self.placements[idx]
        if col < 7:
            return obj.get_value(col)
        else:
            if any((not obj is other) and obj.overlaps(other) for other in self.placements):
                return 'OVERLAP'
            elif self.parent.board_size_type=='specify' and self.parent.board_polygon:
                if not obj.within(self.parent.board_polygon):
                    return 'OVERHANGS BOARD'
        return ''
              
        #elif col==4:
        #    return idx in self.selected
    
    def SetValue(self, value, item, col):
        #print("SetValue", value, item, col)
        idx=self.ItemToObject(item)
        
        if col in (2,3,4):
            self.placements[idx].set_value(col,value)
        
        self.parent.update_board_size()
        return True
    def IsContainer(self, item):
        return False
    
    def GetParent(self, item):
        return dv.DataViewItem(None)
    
class SilkscreenLineModel(dv.PyDataViewModel):
    
    def __init__(self, parent, lines):
        super().__init__()
        self.parent=parent
        self.lines = lines
    
    def GetChildren(self, parent, children):
        for i in range(len(self.lines)):
            children.append(self.ObjectToItem(i))
        return len(self.lines)
    def GetColumnCount(self):
        return 5
    
    def GetValue(self, item, col):
        idx=self.ItemToObject(item)
        obj=self.lines[idx]
        return obj.get_value(col)
    
    def SetValue(self, value, item, col):
        idx=self.ItemToObject(item)
        obj=self.lines[idx]
        
        obj.set_value(col, value)
        return True
    def IsContainer(self, item):
        return False
    
    def GetParent(self, item):
        return dv.DataViewItem(None)
    

class BackgroundColorDataViewRenderer(dv.DataViewCustomRenderer):
    def __init__(self, colors, width):
        super().__init__()
        
        self.pens={}
        for color in colors:
            pen = wx.Pen(wx.ColourDatabase().Find(color))
            brush = wx.Brush(wx.ColourDatabase().Find(color))
            self.pens[color]=(pen,brush)
        #self.pens = dict((color, (pen,brush)) for color in colors)
        self.width=width
    
    def SetValue(self, value):
        self.value = value
        return True

    def GetValue(self):
        return self.value

    def GetSize(self):
        return wx.Size(self.width,30)
        
    def Render(self, rect, dc, state):
        curr_pen=dc.GetPen()
        curr_brush = dc.GetBrush()
        
        split = self.value.find("_")
        color = self.value[:split]
        text = self.value[split+1:]
        pen, brush = self.pens[color]
        #print(color,pen.GetColour(),brush.GetColour(),self.value)
        dc.SetPen(pen)
        dc.SetBrush(brush)
        dc.DrawRectangle(rect)
        
        dc.SetPen(curr_pen)
        dc.SetBrush(curr_brush)
        
        self.RenderText(text,
                        4,   # x-offset, to compensate for the rounded rectangles
                        rect,
                        dc,
                        state # wxDataViewCellRenderState flags
                        )
        
        return True
         
    
    

class TextCtrlDataViewRenderer(dv.DataViewCustomRenderer):
    
    def __init__(self, col, width, *args, **kw):
        super().__init__(*args, **kw)
        #self.col=col
        self.width=width
        self.value = None

    def SetValue(self, value):
        self.value = value
        return True

    def GetValue(self):
        return self.value

    def GetSize(self):
        return wx.Size(self.width,30)
        


    def Render(self, rect, dc, state):
        
        self.RenderText(self.value,
                        4,   # x-offset, to compensate for the rounded rectangles
                        rect,
                        dc,
                        state # wxDataViewCellRenderState flags
                        )
        return True


    
    def HasEditorCtrl(self):
        return True


    def CreateEditorCtrl(self, parent, labelRect, value):
       
        ctrl = wx.TextCtrl(parent,
                           value=value,
                           pos=labelRect.Position,
                           size=labelRect.Size)

        # select the text and put the caret at the end
        ctrl.SetInsertionPointEnd()
        ctrl.SelectAll()

        return ctrl


    def GetValueFromEditorCtrl(self, editor):
        value = editor.GetValue()
        return value
