import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import wx
import descartes as dct

class PreviewPanel:
    def __init__(self, parent):
        self.parent=parent
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.grid()
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-10,10)
        self.ax.set_ylim(10,-10)
        
        self.ax.invert_yaxis()
        self.canvas = FigureCanvas(self.parent.preview_panel, -1, self.figure)
                
        

    
    def draw(self):
        
        while self.ax.patches:
            self.ax.patches[0].remove()
        while self.ax.lines:
            self.ax.lines[0].remove()    
        while self.ax.texts:
            self.ax.texts[0].remove()
            
        for placement in self.parent.placements:
            
            self.ax.add_patch(dct.PolygonPatch(placement.board_outline, fc=placement.color, alpha=0.7))
            xy = placement.board_outline.centroid
            self.ax.text(xy.x, xy.y, "%d" % placement.idx, c='k')
        
        for line in self.parent.silkscreen_lines:
            self.ax.add_patch(dct.PolygonPatch(line.polygon, fc='y'))
        
        if self.parent.board_polygon:
            bo = self.parent.board_polygon.boundary
            if bo.geom_type=='LineString':
                self.ax.plot(bo.xy[0], bo.xy[1], c='k', lw=1)
            elif bo.geom_type=='MultiLineString':
                for bop in bo.geoms:
                    self.ax.plot(bop.xy[0], bop.xy[1], c='k', lw=1)
        
        self.ax.set_xlim(-10, self.parent.board_width+10)
        self.ax.set_ylim(self.parent.board_height+10, -10)
        
        self.canvas.draw()
