from .gerberparse import GerberFile, combine_all
from .drillformat import DrillFile
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
    
    prfxs = [(yy,zz) for yy,zz in [(x,'misc/small_boards/'+x+'/gerbers') for x in os.listdir('misc/small_boards')] if os.path.exists(zz)]
    
    
    #get_parts=lambda x, prfx: dict((f[len(x)+1:-4], GerberFile.from_file(os.path.join(prfx, f))) for f in os.listdir(prfx) if f[-3]=='g')

    all_parts={}

    for nn,pp in prfxs:
        print(f"{nn}: {pp}:")
        qq=get_parts(nn,pp)
    
        for k,v in qq.items():
            if show_summary:
                print(f"  {k}: {len(v.parts)} parts")
            if show_cmds:
                for x in v.parts:
                    if x.command:
                        print("    ",repr(x.command), str(x.command)[:60].replace("\n"," "))
                    
        all_parts[nn]=qq
    return all_parts

def dimensions(parts):
    
    max_len = max(len(k) for k,v in parts.items())
    dims = {}
    print(f"{' '*max_len} |   left |    top |  width | height")    
    for k,v in sorted(parts.items()):
        a,b,c,d = v['Edge_Cuts'].find_bounds()
        left=a/1_000_000
        top=-d/1_000_000
        width=(c-a)/1_000_000
        height=(d-b)/1_000_000
        dims[k] = [left,top,width,height]
        print(f"{k+' '*(max_len-len(k))} | {left:6.1f} | {top:6.1f} | {width:6.1f} | {height:6.1f}")
    return dims
    

    
def main():
    print("main")
    if len(sys.argv)>1:
        
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
        parts = demo()
        dims = dimensions(parts)
        
        AA = [['33063_boost', 2.5, 0], ['33063_invert', 50.5, 0], ['r1283_power', 0, 21], ['ap3372s_usbpd', 50.5, 21]]

        silks = [[1,100,50,100,95],[1,50,70,150,70]]
        combined=combine_all(parts, AA, 'combined_board/combined_board', [50,50,150,95], silks)
        
        if not __name__ == "__main__":
            return parts, dims,combined
        

