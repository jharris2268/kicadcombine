from .gerber import GerberFile, combine_all
from .gerber.drillformat import DrillFile
from .gerber.sourcedesign import SourceDesign

from .kicad import get_source_files, prepare_panel

import wx
from .gui import run_gui
import sys, os


def get_parts(x, prfx):
    result={}
    for f in os.listdir(prfx):
        fn=os.path.join(prfx, f)
        if f[-3]=='g':
            name = f[len(x)+1:-4]
            gerber=GerberFile.from_file(fn)
            result[name]=gerber
        elif f[-3:]=='drl':
            name = f[len(x)+1:-4]
            drills=DrillFile.from_file(fn)
            if drills.units != 'METRIC':
                raise Exception(f"expected drill file {fn} to be metric units")
            result[name]=drills
    return result


def demo(show_summary=False, show_cmds=False):
    result = {}
    for m in ('misc/small_boards',
            'misc/other_small_boards',
            'pi_pico/pico_siggen/hardware/panels/gerbers/'
            '6502-boards/rom-adaptor-smd/gerbers/'):
    
        for a,b,c in os.path.tree(m):
            if any(is_gerber_file(f) for f in c):
                
                sd = SourceDesign.from_path(a)
                if show_summary:
                    print(f"  {k}: {len(sd.parts)} parts")
                if show_cmds:
                    for x in sd.parts:
                        if x.command:
                            print("    ",repr(x.command), str(x.command)[:60].replace("\n"," "))
                result[sd.name] = sd
    return result
    

def demo_old(show_summary=False, show_cmds=False):
    
    #prfxs=['misc/gerber_expr/gerbers/',
    #       'misc/misc_boards_20241217/gerbers/']
    
    
    result = {}
    for x in os.listdir('misc/small_boards'):
        if os.path.exists('misc/small_boards/'+x+'/gerbers'):
            
            sd = SourceDesign.from_path('misc/small_boards/'+x+'/gerbers')
            if show_summary:
                print(f"  {k}: {len(sd.parts)} parts")
            if show_cmds:
                for x in sd.parts:
                    if x.command:
                        print("    ",repr(x.command), str(x.command)[:60].replace("\n"," "))
            result[sd.name] = sd
    
    return result

def dimensions(parts):
    
    max_len = max(len(k) for k,v in parts.items())
    dims = {}
    print(f"{' '*max_len} |   left |    top |  width | height")    
    for _,sd in sorted(parts.items()):
        
        print(f"{sd.name+' '*(max_len-len(sd.name))} | {sd.left:6.1f} | {sd.top:6.1f} | {sd.width:6.1f} | {sd.height:6.1f}")
    


DESIGN = [
    #board,             x-pos,  y-pos,  angle
    ['33063_boost',     2,      0,      0],
    ['33063_invert',    50,     0,      0],
    ['r1283_power',     4,      21,     0],
    ['ap3372s_usbpd',   50,     21,     0],
    ['panels',          6,      45,     0],
]

LINES = [
    #width, sx,     sy,     ex,     ey
    [1,     None,   20.5,   None,   20.5],
    [1,     None,   None,   49.5,   44.5],
    [10,    49.5,   0       49.5,   44.5],
]
    
def main():
    #print("main")
    if 'gerberdemo' in sys.argv:
        parts = demo()
        dimensions(parts)
        
        combined_parts=combine_all(parts, DESIGN, 'combined_board/from_gerber/combined_board', None, None, LINES)
        
        a,b='combined_board','combined_board/from_gerber/'
        combined= SourceDesign(a,b,combined_parts)
        
        
        if not __name__ == "__main__":
            return parts, combined
    
    elif 'kicaddemo' in sys.argv:
        source_files = get_source_files([
            'misc/small_boards',
            'misc/other_small_boards',
            'pi_pico/pico_siggen/hardware/panels/panels.kicad_pcb'
            '6502-boards/rom-adaptor-smd/rom-adaptor-smd.kicad_pcb'        
        ])
        
        
        prepare_panel(source_files, DESIGN, LINES, 'combined_board/combined_board.kicad_pcb')
        
        
            
    else:
        run_gui()
        
        
        
        

