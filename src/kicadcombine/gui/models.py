import wx.dataview as dv
import wx



    
    
class SourceDesignModel(dv.PyDataViewModel):
    def __init__(self, parent):
        super().__init__()
        self.parent=parent
        self.source_designs=parent.panel.source_designs
        
        
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


COLORS = ['red','green','blue']
def get_color(idx):
    return COLORS[idx % len(COLORS)]

class PlacementsModel(dv.PyDataViewModel):
    def __init__(self, parent):
        super().__init__()
        
        self.parent=parent
        self.panel = parent.panel
        
        
    def GetChildren(self, parent, children):
        for i in sorted(self.panel._placements):
            children.append(self.ObjectToItem(i))
        
        return len(self.panel._placements)
    
    def GetColumnCount(self):
        return 7
    
    def GetValue(self, item, col):
        idx=self.ItemToObject(item)
        obj=self.panel.get_placement(idx)
        if col == 0:
            return '%s_%d' % (get_color(obj.idx), obj.idx)
        if col==1:
            return '%s_%s' % (get_color(obj.idx), obj.design.name)
        if col==2:
            return "%5.1f" % obj.x_pos
        if col==3:
            return "%5.1f" % obj.y_pos
        if col==4:
            return "%d" % obj.angle
        if col==5:
            return "%5.1f" % obj.x_max
        if col==6:
            return "%5.1f" % obj.y_max
        if col==7:
            if any((not obj is other) and obj.overlaps(other) for other in self.panel.placements):
                return 'OVERLAP'
            elif self.parent.panel.board_size_type=='specify' and self.parent.panel.board_polygon:
                if not obj.within(self.parent.panel.board_polygon):
                    return 'OVERHANGS BOARD'
        return ''
              
    
    def SetValue(self, value, item, col):
        #print("SetValue", value, item, col)
        idx=self.ItemToObject(item)
        placement=self.panel.get_placement(idx)
        if col==2:
            placement.update(x_pos = float(value))
        elif col==3:
            placement.update(y_pos = float(value))
        elif col==4:
            if not value in ('0','90','180','270'):
                raise Exception("wrong value for angle")
            placement.update(angle = float(value))
            
        
        self.parent.update_board_size()
        return True
        
        
    def IsContainer(self, item):
        return False
    
    def GetParent(self, item):
        return dv.DataViewItem(None)
    
    
none_or_val_to_string = lambda x: 'none' if x is None else '%5.1f' % x

class SilkscreenLineModel(dv.PyDataViewModel):
    
    def __init__(self, parent):
        super().__init__()
        self.parent=parent
        self.lines = parent.panel.silkscreen_lines
    
    def GetChildren(self, parent, children):
        for i in range(len(self.lines)):
            children.append(self.ObjectToItem(i))
        return len(self.lines)
    def GetColumnCount(self):
        return 5
    
    def GetValue(self, item, col):
        idx=self.ItemToObject(item)
        obj=self.lines[idx]
        
        if col==0:
            return 'left' if obj.x0 is None else '%5.1f' % obj.x0
        if col==1:
            return 'top' if obj.y0 is None else '%5.1f' % obj.y0
        if col==2:
            return 'right' if obj.x1 is None else '%5.1f' % obj.x1
        if col==3:
            return 'bottom' if obj.y1 is None else '%5.1f' % obj.y1
        if col==4:
            return 'default' if obj.width is None else '%5.1f' % obj.width
        
        return ''
    
    def SetValue(self, value, item, col):
        idx=self.ItemToObject(item)
        
        obj=self.lines[idx]
        
        
        
        obj.set_value(col, value)
        self.parent.update_board_size()
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
            cc=wx.ColourDatabase().Find(color)
            cc2=wx.Colour(cc.GetRed(), cc.GetGreen(), cc.GetBlue(), 160)
            pen = wx.Pen(cc)            
            brush = wx.Brush(cc2)
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
