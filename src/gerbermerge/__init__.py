from .gerberparse import GerberFile
import sys, os

def demo(show_summary=False, show_cmds=False):
    
    #prfxs=['misc/gerber_expr/gerbers/',
    #       'misc/misc_boards_20241217/gerbers/']
    
    prfxs = [(yy,zz) for yy,zz in [(x,'misc/small_boards/'+x+'/gerbers') for x in os.listdir('misc/small_boards')] if os.path.exists(zz)]
    
    
    get_parts=lambda x, prfx: dict((f[len(x)+1:-4], GerberFile.from_file(os.path.join(prfx, f))) for f in os.listdir(prfx) if f[-3]=='g')

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
        return parts, dims
        

