class Percent:
    @staticmethod
    def from_cmd(pos, cmd):
        res = Percent(pos,0,str(cmd),cmd)
        res.end = pos + len(str(res))
        return res
    
    def __init__(self, start, end, str, command=None):
        self.start=start
        self.end=end
        self.str=str
        
        self.command=command
        
    
    def __str__(self):
        return '%%%s%%' % self.str
        
    def __repr__(self):
        return "Percent[%6d %4d %s%s]" % (self.start, len(self.str), self.str[:40],'...' if len(self.str)>40 else '')

class Newline:
    def __init__(self, start):
        self.start=start
        self.command=None
        
        
    def __str__(self):
        return '\n'
        
    def __repr__(self):
        return "Newline[%6d]" % (self.start, )

class Line:
    @staticmethod
    def from_cmd(pos, cmd):
        res = Line(pos,0,str(cmd),cmd)
        res.end = pos + len(str(res))
        return res
        
    def __init__(self, start, end, str, command=None):
        self.start=start
        self.end=end
        self.str=str
        
        self.command = command
    
    def __str__(self):
        return '%s' % self.str
    
    def __repr__(self):
        return "Line[%6d %4d %s%s]" % (self.start, len(self.str), self.str[:40],'...' if len(self.str)>40 else '')


class PartsList:
    def __init__(self):
        self.parts=[]
        self.pos=0
        
    def add(self, cmd, percent=False):
        if self.parts:
            self.parts.append(Newline(self.pos))
            self.pos+=1
        
        if percent:
            self.parts.append(Percent.from_cmd(self.pos, cmd))
            self.pos=self.parts[-1].end
        
        else:
            self.parts.append(Line.from_cmd(self.pos, cmd))
            self.pos=self.parts[-1].end
    
    def to_str(self):
        return "".join(str(p) for p in self.parts)
        
def iter_parts(input_str):
    
        
    idx=0
    
    while idx < len(input_str):
        
        if input_str[idx]=='%':
            end=input_str.find('%', idx+1)
            if end==-1:
                raise Exception('EOF')
            part_str=input_str[idx+1:end]
            
            yield Percent(idx, end, part_str)
            idx = end+1
            
            
        elif input_str[idx]=='\n':
            yield Newline(idx)
            idx+=1
            
        else:
            end=input_str.find('\n', idx)
            if end==-1:
                raise Exception('EOF')
            part_str=input_str[idx:end]
            yield Line(idx, end, part_str)
            idx=end
