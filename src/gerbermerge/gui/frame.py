# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-5-gc2f65a65)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview

import gettext
_ = gettext.gettext

###########################################################################
## Class GerberMergeFrameBase
###########################################################################

class GerberMergeFrameBase ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1264,999 ), style = wx.DEFAULT_FRAME_STYLE|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.m_menu1 = wx.Menu()
        self.open_menuitem = wx.MenuItem( self.m_menu1, wx.ID_ANY, _(u"Open"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.Append( self.open_menuitem )

        self.save_menuitem = wx.MenuItem( self.m_menu1, wx.ID_ANY, _(u"Save"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.Append( self.save_menuitem )

        self.m_menu1.AppendSeparator()

        self.exit_menuitem = wx.MenuItem( self.m_menu1, wx.ID_ANY, _(u"Exit"), wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.Append( self.exit_menuitem )

        self.m_menubar1.Append( self.m_menu1, _(u"File") )

        self.SetMenuBar( self.m_menubar1 )

        gbSizer1 = wx.GridBagSizer( 0, 0 )
        gbSizer1.SetFlexibleDirection( wx.BOTH )
        gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.source_designs_view = wx.dataview.DataViewCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.source_designs_view, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 5 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, _(u"Source Designs"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText27.Wrap( -1 )

        gbSizer1.Add( self.m_staticText27, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 5 ), wx.ALL, 5 )

        self.add_sourcedesign_row = wx.Button( self, wx.ID_ANY, _(u"Import Source Design"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_sourcedesign_row, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.add_to_row = wx.Button( self, wx.ID_ANY, _(u"Add To Placements"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_to_row, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_button5 = wx.Button( self, wx.ID_ANY, _(u"Delete Source Designs"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.m_button5, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline1, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 5 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, _(u"Board width"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText25.Wrap( -1 )

        gbSizer1.Add( self.m_staticText25, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.board_height_entry = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.board_height_entry, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, _(u"height"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText26.Wrap( -1 )

        gbSizer1.Add( self.m_staticText26, wx.GBPosition( 4, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.board_width_entry = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.board_width_entry, wx.GBPosition( 4, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline2, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 5 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, _(u"Placements"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText28.Wrap( -1 )

        gbSizer1.Add( self.m_staticText28, wx.GBPosition( 6, 0 ), wx.GBSpan( 1, 5 ), wx.ALL, 5 )

        self.placements_view = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_ROW_LINES )
        gbSizer1.Add( self.placements_view, wx.GBPosition( 7, 0 ), wx.GBSpan( 1, 5 ), wx.ALL|wx.EXPAND, 5 )

        self.m_button6 = wx.Button( self, wx.ID_ANY, _(u"Delete Placements"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.m_button6, wx.GBPosition( 8, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline3, wx.GBPosition( 9, 0 ), wx.GBSpan( 1, 5 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText29 = wx.StaticText( self, wx.ID_ANY, _(u"Silkscreen Lines"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText29.Wrap( -1 )

        gbSizer1.Add( self.m_staticText29, wx.GBPosition( 10, 0 ), wx.GBSpan( 1, 5 ), wx.ALL, 5 )

        self.silkscreen_lines_view = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_ROW_LINES )
        gbSizer1.Add( self.silkscreen_lines_view, wx.GBPosition( 11, 0 ), wx.GBSpan( 1, 5 ), wx.ALL|wx.EXPAND, 5 )

        self.add_silkscreenline_row = wx.Button( self, wx.ID_ANY, _(u"Add Row"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_silkscreenline_row, wx.GBPosition( 12, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline4, wx.GBPosition( 9, 7 ), wx.GBSpan( 1, 3 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, _(u"Output"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText30.Wrap( -1 )

        gbSizer1.Add( self.m_staticText30, wx.GBPosition( 10, 7 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.output_filename_entry = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.output_filename_entry, wx.GBPosition( 11, 7 ), wx.GBSpan( 1, 5 ), wx.ALL, 5 )

        self.call_merge = wx.Button( self, wx.ID_ANY, _(u"Merge"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.call_merge, wx.GBPosition( 12, 7 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        self.m_staticline5.SetMaxSize( wx.Size( 5,-1 ) )

        gbSizer1.Add( self.m_staticline5, wx.GBPosition( 0, 6 ), wx.GBSpan( 16, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, _(u"Preview"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )

        gbSizer1.Add( self.m_staticText7, wx.GBPosition( 0, 7 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )

        self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_bitmap1.SetMinSize( wx.Size( 300,300 ) )

        gbSizer1.Add( self.m_bitmap1, wx.GBPosition( 1, 7 ), wx.GBSpan( 8, 3 ), wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 5 )


        gbSizer1.AddGrowableCol( 4 )
        gbSizer1.AddGrowableCol( 6 )
        gbSizer1.AddGrowableRow( 1 )
        gbSizer1.AddGrowableRow( 7 )
        gbSizer1.AddGrowableRow( 11 )

        self.SetSizer( gbSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


