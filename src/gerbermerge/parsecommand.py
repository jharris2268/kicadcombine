from .commands import *
import re
from .utils import get_num


FS_re = re.compile("^FSLAX([1-6])([6])Y([1-6])([6])\*$")
AD_re = re.compile("^AD(?P<ident>D[0-9]+)(?P<template_name>\w+)\,(?P<first_param>\-?\d+(\.\d+)?)(?P<other_params>(X\-?\d+(\.\d+)?)*)\*$")
D_re=re.compile("^(?P<X>X\-?\d+)?(?P<Y>Y\-?\d+)?(?P<I>I\-?\d+)?(?P<J>J\-?\d+)?(?P<type>D0[1|2|3])\*")

SR_re=re.compile("^SR(?P<X>\d+)?(?P<Y>\d+)?(?P<I>\-?\d+(\.\d+)?)?(?P<J>\-?\d+(\.\d+)?)?\*$")


def read_command(str):
    if not str.endswith('*'):
        raise Exception("expected line/percent to end with '*': %s" % str)
    if str[:3]=='G04':
        
        return Comment('G04', str[4:-1])
    
    if str[:2]=='MO':
        if not len(str)==5:
            raise Exception("expected 'MOMM' or 'MOMM'")
        if not str[2:4] in ('MM','MI'):
            raise Exception("expected 'MOMM' or 'MOMM'")
        return Units('MO', str[2:4]=='MM')
    if str[:2]=='FS':
        if not len(str)==11:
            raise Exception("expected FS command length 11, format FSLAX{x_didgets}Y{y_didgets}")
        mm=FS_re.match(str)
        if not mm:
            raise Exception("expected FS command length 11, format FSLAX{x_digits}Y{y_digits}")
        x1,x2,y1,y2=mm.groups()
        if not (x1==y1 and x2=='6' and y2=='6'):
            raise Exception("expected FS command, equal x and y, num decimals equal 6")
        
        return FormatSpec('FS', int(x1))
    
    if str[:2]=='AD':
        if not len(str)>5:
            raise Exception("expected AD command, length >6, format AD{aperture_ident}{template_call}*")
        mm=AD_re.match(str)
        if not mm:
            raise Exception("expected AD command, length >6, format AD{aperture_ident}{template_call}*")
        
        pp = mm.groupdict()
        template_params=[get_num(pp['first_param'])]
        if pp['other_params']:
            template_params.extend(get_num(x) for x in pp['other_params'][1:].split("X"))
        
        return ApertureDefinition('AD', pp['ident'], pp['template_name'], template_params)

    if str[:2]=='AM':
        mm=re.match("^AM(\w*)\*\n", str)
        if not mm:
            raise Exception("expected AM command, length >3, format AM{macro_name}*\n{macro_body}*")
        macro_name,=mm.groups()
        macro_body = str[mm.end():-1]
        return ApertureMacro('AM', macro_name, macro_body)
    
    
    if str.endswith("D01*") or str.endswith("D02*") or str.endswith("D03*"):
        
        mm=D_re.match(str)
        if not mm:
            raise Exception("expected D01/D02/D03 command, format X{x coord}Y{y coord}I{x offset}J(y offset){type}*", str)
        
        mmd = mm.groupdict()
        
        x=int(mmd['X'][1:]) if mmd['X'] else None
        y=int(mmd['Y'][1:]) if mmd['Y'] else None
        i=int(mmd['I'][1:]) if mmd['I'] else None
        j=int(mmd['J'][1:]) if mmd['J'] else None
        
        
        return GraphicalOperation(mmd['type'], x, y, i, j)
    
        
    if str[0]=='D':
        
        mm=re.match("^D(\d+)\*$", str)
        if not mm:
            raise Exception("expected D command, length >2, format D{aperture_number >= 10}*")
        ident=int(mm.groups()[0])
        if not ident>=10:
            raise Exception("expected D command, length >2, format D{aperture_number >= 10}*")
        return SetCurrentAperture("D", ident)
    
    
    
    if str[0]=='G':
        mm=re.match("^G(\d\d)\*$", str)
        if not mm:
            raise Exception("expected G01/G02/G03/G75 command", str)
        
        number,=mm.groups()
        if number in ('01','02','03','75'):
            return PlotStateCommand('G', number)
        elif number in ('36','37'):
            return RegionStateCommand('G', number)
        else:
            raise Exception("expected G01/G02/G03/G36/G37/G75 command", str)
    
    
    
    if str[:2] == 'LP':
        
        mm=re.match("^LP([C|D])\*$", str)
        if not mm:
            raise Exception("expected LP{C | D} command", str)
        
        return LoadPolarity('LP', mm.groups()[0])
    
    if str[:2] == 'LM':
        
        mm=re.match("^LM([N|X|Y|XY])\*$", str)
        if not mm:
            raise Exception("expected LM{N | X | Y | XY} command", str)
        
        return LoadMirroring('LM', mm.groups()[0])
    
    if str[:2] == 'LR':
        
        mm=re.match("^LR(\-?\d+(.\d+)?)\*$", str)
        if not mm:
            raise Exception("expected LR{rotation} command", str)
        
        return LoadRotation('LR', get_num(mm.groups()[0]))
    
    if str[:2] == 'LS':
        
        mm=re.match("^LS(\-?\d+(.\d+)?)\*$", str)
        if not mm:
            raise Exception("expected LS{scaling} command", str)
        
        return LoadScaling('LS', get_num(mm.groups()[0]))
        
           
    
    
    if str=='M02*':
        return EndOfFile('M02')
    
    if str[:2]=='AB':
        
        mm=re.match("^AB(D\d+)?\*$", str)
        if not mm:
            raise Exception("expected AD{block number?} command", str)
        
        return BlockAperture('AB', mm.groups()[0])
    
    if str[:2]=='SR':
        mm=SR_re.match(str)
        if not mm:
            raise Exception("expected SR{X num reps?}{Y num_reps}{I offset}?{J offset}? command", str)
        
        mmd=mm.groupdict()
        x=int(mmd['X']) if mmd['X'] else None
        y=int(mmd['Y']) if mmd['Y'] else None
        i=get_num(mmd['I']) if mmd['I'] else None
        j=get_num(mmd['J']) if mmd['J'] else None
        
        
        return StepRepeat('SR', x,y,i,j)
    
    
    if str[:2]=='TF':
        
        mm=re.match("^TF(\.?\w+)\,", str)
        if not mm:
            raise Exception("expected TF{attr name},{attr values} command", str)
        
        n,=mm.groups()
        v=str[mm.end():-1]
        return FileAttributes('TF', n, v)
    
    if str[:2]=='TA':
        
        mm=re.match("^TA(\.?\w+)\,", str)
        if not mm:
            raise Exception("expected TA{attr name},{attr values} command", str)
        
        n,=mm.groups()
        v=str[mm.end():-1]
        return ApertureAttributes('TA', n, v)
    
    if str[:2]=='TO':
        
        mm=re.match("^TO(\.?\w+)\,", str)
        if not mm:
            raise Exception("expected TO{attr name},{attr values} command", str)
        
        n,=mm.groups()
        v=str[mm.end():-1]
        return ObjectAttributes('TO', n, v)
    
    if str[:2]=='TD':
        mm=re.match("^TD(\.?\w+)?\*", str)
        if not mm:
            raise Exception("expected TD{attr name} command", str)
        
        n,=mm.groups()
        
        return DeleteAttributes('TD', n)
    
    
    print("missing",str)
        
    return None
