
from .kicad import Panel
from .gui import run_gui



    


DESIGN = [
    #board,             x-pos,  y-pos,  angle
    ['33063_boost',     2,      0,      0],
    ['33063_invert',    50,     0,      0],
    ['ap3372s_usbpd',   4,      21,     0],
    ['r1283_power',     50,     21,     0],
    ['panels',          6,      45,     0],
]

LINES = [
    #sx,     sy,     ex,     ey,    width, 
    [None,   20.5,   None,   20.5,  None],
    [None,   44.5,   None,   44.5,  None],
    [49.5,   0,      49.5,   44.5,  None],
]

EXAMPLE_LOCATIONS = [
    '/home/james/elec/misc/small_boards',
    '/home/james/elec/misc/other_small_boards',
    '/home/james/elec/pi_pico/pico_siggen/hardware/panels/panels.kicad_pcb',
    
]

def main():

    
    if 'kicaddemo' in sys.argv:
        
        panel = kicad.Panel()
        panel.open_source_designs(EXAMPLE_LOCATIONS)
        for n,xp,yp,a in DESIGN:
            panel.add_placement(n, xp, yp, a)
        for sx,sy,ex,ey,w in LINES:
            panel.add_silkscreen_line(sx, sy, ex,ey, w)
        
        panel.output_filename = 'combined_board/combined_board.kicad_pcb'
        panel.board_size_type = 'tight'
        
        panel.prepare_panel()
        
        
            
    else:
        design=None
        if len(sys.argv)>2:
            design=sys.argv[2]
        run_gui(design)
        
        
        
        

