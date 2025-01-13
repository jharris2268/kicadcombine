from .gerberparse import GerberFile, combine_all
from .drillformat import DrillFile
from .sourcedesign import SourceDesign
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
    
    

    
def main():
    #print("main")
    if 'demo' in sys.argv:
        parts = demo()
        dimensions(parts)
        
        AA = [['33063_boost', 2.5, 0], ['33063_invert', 50.5, 0], ['r1283_power', 0, 21], ['ap3372s_usbpd', 50.5, 21]]

        silks = [[1,100,50,100,95],[1,50,70,150,70]]
        combined_parts=combine_all(parts, AA, 'combined_board/combined_board', [50,50,150,95], silks)
        
        a,b='combined_board','combined_board'
        combined= SourceDesign(a,b,combined_parts)
        
        
        if not __name__ == "__main__":
            return parts, combined
    
    elif len(sys.argv)>1:
        
        for n in sys.argv[1:]:
            
            
            gf=GerberFile.from_file(n)
            print(f"{n}: {len(gf.parts)} parts")
            
            
            output=[]
            for x in gf.parts:
                print("  ",x,end='')
                if x.command:
                    print("    ",repr(x.command), str(x.command)[:60].replace("\n"," "))
                
                if isinstance(x, Newline):
                    output.append('\n')
                elif isinstance(x, Percent):
                    output.append(f"%{x.command}%")
                else:
                    output.append(str(x.command))
            
            output_str="".join(output)
            print("input == output? ", gf.input_str==output_str)
            
            for a,b in zip(gf.input_str.split("\n"),output_str.split("\n")):
                print("%s %-50.50s | %-50.50s" % (' ' if a==b else '*', a,b))
            
    else:
        run_gui()
        
        
        
        

