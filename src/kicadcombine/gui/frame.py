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
## Class KicadCombineFrameBase
###########################################################################

class KicadCombineFrameBase ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1600,1000 ), style = wx.DEFAULT_FRAME_STYLE|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )

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

        self.source_designs_view = wx.dataview.DataViewCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_MULTIPLE )
        gbSizer1.Add( self.source_designs_view, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 12 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, _(u"Source Designs"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText27.Wrap( -1 )

        gbSizer1.Add( self.m_staticText27, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 12 ), wx.ALL, 5 )

        self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, _(u"Import kicad_pcb"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )

        gbSizer1.Add( self.m_staticText8, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.add_sourcedesign_row_one = wx.Button( self, wx.ID_ANY, _(u"Single"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_sourcedesign_row_one, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.add_sourcedesign_row_many = wx.Button( self, wx.ID_ANY, _(u"All"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_sourcedesign_row_many, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, _(u"Add To Placements"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )

        gbSizer1.Add( self.m_staticText9, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        self.angle = wx.StaticText( self, wx.ID_ANY, _(u"Angle"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.angle.Wrap( -1 )

        bSizer3.Add( self.angle, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        add_placement_angleChoices = [ _(u"0"), _(u"90"), _(u"180"), _(u"270") ]
        self.add_placement_angle = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, add_placement_angleChoices, 0 )
        self.add_placement_angle.SetSelection( 0 )
        bSizer3.Add( self.add_placement_angle, 0, wx.ALL, 5 )

        self.add_to_placements_right = wx.Button( self, wx.ID_ANY, _(u"Add Right"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.add_to_placements_right, 0, wx.ALL, 5 )

        self.add_to_placements_below = wx.Button( self, wx.ID_ANY, _(u"Add Below"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.add_to_placements_below, 0, wx.ALL, 5 )


        gbSizer1.Add( bSizer3, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 4 ), wx.EXPAND, 5 )

        self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        gbSizer1.Add( self.m_staticline6, wx.GBPosition( 3, 5 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.add_to_placements_new_row = wx.Button( self, wx.ID_ANY, _(u"Add New Row"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_to_placements_new_row, wx.GBPosition( 3, 6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.add_to_placements_new_column = wx.Button( self, wx.ID_ANY, _(u"Add New Column"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_to_placements_new_column, wx.GBPosition( 3, 7 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline10 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        gbSizer1.Add( self.m_staticline10, wx.GBPosition( 3, 8 ), wx.GBSpan( 1, 1 ), wx.EXPAND |wx.ALL, 5 )

        self.with_lines_checkbox = wx.CheckBox( self, wx.ID_ANY, _(u"With Line"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.with_lines_checkbox.SetValue(True)
        gbSizer1.Add( self.with_lines_checkbox, wx.GBPosition( 3, 9 ), wx.GBSpan( 1, 1 ), wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        gbSizer1.Add( self.m_staticline7, wx.GBPosition( 2, 5 ), wx.GBSpan( 1, 1 ), wx.EXPAND |wx.ALL, 5 )

        self.delete_source_design = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.delete_source_design, wx.GBPosition( 2, 6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline1, wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 12 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, _(u"Board Size"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )

        gbSizer1.Add( self.m_staticText12, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        self.board_size_radio_fit = wx.RadioButton( self, wx.ID_ANY, _(u"Fit Box"), wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP )
        bSizer2.Add( self.board_size_radio_fit, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.board_size_radio_tight = wx.RadioButton( self, wx.ID_ANY, _(u"Fit Tight"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.board_size_radio_tight, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.board_size_radio_specify = wx.RadioButton( self, wx.ID_ANY, _(u"Specify"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.board_size_radio_specify, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        gbSizer1.Add( bSizer2, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 2 ), wx.EXPAND, 5 )

        self.m_staticline9 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        gbSizer1.Add( self.m_staticline9, wx.GBPosition( 5, 3 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, _(u"height"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText26.Wrap( -1 )

        bSizer1.Add( self.m_staticText26, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.board_height_entry = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        bSizer1.Add( self.board_height_entry, 0, wx.ALL, 5 )

        self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, _(u"width"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText25.Wrap( -1 )

        bSizer1.Add( self.m_staticText25, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.board_width_entry = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        bSizer1.Add( self.board_width_entry, 0, wx.ALL, 5 )

        self.board_area_label = wx.StaticText( self, wx.ID_ANY, _(u"board area"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.board_area_label.Wrap( -1 )

        bSizer1.Add( self.board_area_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        gbSizer1.Add( bSizer1, wx.GBPosition( 5, 4 ), wx.GBSpan( 1, 4 ), wx.EXPAND, 5 )

        self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        gbSizer1.Add( self.m_staticline11, wx.GBPosition( 5, 8 ), wx.GBSpan( 1, 1 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline2, wx.GBPosition( 6, 0 ), wx.GBSpan( 1, 12 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, _(u"Placements"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText28.Wrap( -1 )

        gbSizer1.Add( self.m_staticText28, wx.GBPosition( 7, 0 ), wx.GBSpan( 1, 5 ), wx.ALL, 5 )

        self.placements_view = wx.dataview.DataViewCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_MULTIPLE )
        gbSizer1.Add( self.placements_view, wx.GBPosition( 8, 0 ), wx.GBSpan( 1, 12 ), wx.ALL|wx.EXPAND, 5 )

        self.delete_placement = wx.Button( self, wx.ID_ANY, _(u"Delete"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.delete_placement, wx.GBPosition( 9, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline3, wx.GBPosition( 10, 0 ), wx.GBSpan( 1, 12 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText29 = wx.StaticText( self, wx.ID_ANY, _(u"Silkscreen Lines"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText29.Wrap( -1 )

        gbSizer1.Add( self.m_staticText29, wx.GBPosition( 11, 0 ), wx.GBSpan( 1, 5 ), wx.ALL, 5 )

        self.silkscreen_lines_view = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_MULTIPLE|wx.dataview.DV_ROW_LINES )
        gbSizer1.Add( self.silkscreen_lines_view, wx.GBPosition( 12, 0 ), wx.GBSpan( 3, 12 ), wx.ALL|wx.EXPAND, 5 )

        self.add_silkscreenline_row = wx.Button( self, wx.ID_ANY, _(u"Add Row"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.add_silkscreenline_row, wx.GBPosition( 15, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        gbSizer1.Add( self.m_staticline4, wx.GBPosition( 10, 13 ), wx.GBSpan( 1, 2 ), wx.EXPAND |wx.ALL, 5 )

        self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, _(u"Output"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText30.Wrap( -1 )

        gbSizer1.Add( self.m_staticText30, wx.GBPosition( 11, 13 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.output_filename_entry = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
        gbSizer1.Add( self.output_filename_entry, wx.GBPosition( 12, 14 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.set_ouput_filename_button = wx.Button( self, wx.ID_ANY, _(u"Set Ouput Filename"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.set_ouput_filename_button, wx.GBPosition( 12, 13 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.make_panel_button = wx.Button( self, wx.ID_ANY, _(u"Make Panel"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer1.Add( self.make_panel_button, wx.GBPosition( 13, 13 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        self.m_staticline5.SetMaxSize( wx.Size( 5,-1 ) )

        gbSizer1.Add( self.m_staticline5, wx.GBPosition( 0, 12 ), wx.GBSpan( 16, 1 ), wx.ALL|wx.EXPAND, 5 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, _(u"Preview"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )

        gbSizer1.Add( self.m_staticText7, wx.GBPosition( 0, 13 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )

        self.preview_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.preview_panel.SetMinSize( wx.Size( 600,600 ) )

        gbSizer1.Add( self.preview_panel, wx.GBPosition( 1, 13 ), wx.GBSpan( 8, 2 ), wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 5 )


        gbSizer1.AddGrowableCol( 14 )
        gbSizer1.AddGrowableRow( 1 )
        gbSizer1.AddGrowableRow( 8 )
        gbSizer1.AddGrowableRow( 13 )

        self.SetSizer( gbSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


