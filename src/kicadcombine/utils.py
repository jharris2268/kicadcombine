get_num=lambda x: ('f',float(x)) if '.' in x else ('i', int(x))

num_str=lambda i,p: '%d' % p if i=='i' else '%0.6f' % p
num_str_null=lambda w, x: '' if x is None else "%s%s" % (w,num_str(*x))

num_repr=lambda x: '' if x is None else "%s %s" % (x[0],x[1])


import re

name_re = re.compile('^[A-Z][1-9][0-9]+$')
def next_name(ll, letter=None):
    
    max_val,max_int = None,0
    for l in ll:
        check = name_re.match(l)
        if not check:
            raise Exception(f"{l} not in expected form [A-Z][1-9][0-9]+")
        if letter is not None and letter != l[0]:
            raise Exception(f"{l} not in expected form {letter}[1-9][0-9]+")
        int_val = int(l[1:])
        if int_val>max_int:
            max_val=l
            max_int=int_val
    
    if not max_val:
        if not letter:
            raise Exception("??")
        else:
            return f"{letter}10"
    return "%s%d" % (max_val[0] if max_val else letter, max_int+1)
            
    
class Bounds:
    def __init__(self):
        self.min_x,self.min_y,self.max_x,self.max_y = None,None, None, None
    
    def is_empty(self):
        return self.min_x is None
    
    def expand(self, x, y):
        if self.is_empty():
            self.min_x = x
            self.min_y = y
            self.max_x = x
            self.max_y = y
            return
        
        if x < self.min_x: self.min_x = x
        if y < self.min_y: self.min_y = y
        if x > self.max_x: self.max_x = x
        if y > self.max_y: self.max_y = y
    
    def translate(self, x_offset, y_offset):
        new=Bounds()
        if self.is_empty():
            return new
        new.expand(self.min_x+x_offset,self.min_y+y_offset)
        new.expand(self.max_x+x_offset,self.max_y+y_offset)
        return new
    
    def expand_bounds(self, other):
        if other.is_empty():
            return
        if self.is_empty():
            self.min_x = other.min_x
            self.min_y = other.min_y
            self.max_x = other.max_x
            self.max_y = other.max_y
            return
        
        if other.min_x < self.min_x: self.min_x = other.min_x
        if other.min_y < self.min_y: self.min_y = other.min_y
        if other.max_x > self.max_x: self.max_x = other.max_x
        if other.max_y > self.max_y: self.max_y = other.max_y
    
    def intersects(self, other):
        if self.is_empty() or other.is_empty(): return False
        if self.min_x > other.max_x: return False
        if self.min_y > other.max_y: return False
        if other.min_x > self.max_x: return False
        if other.min_y > self.max_y: return False
        return True
    
    @property
    def width(self):
        if self.is_empty():
            return False
        return self.max_x-self.min_x
    
    @property
    def height(self):
        if self.is_empty():
            return False
        return self.max_y-self.min_y
    
    def __len__(self):
        return 4
    
    def __getitem__(self, i):
        if i<0: i+=4
        
        
        if i==0: return self.min_x
        if i==1: return self.min_y
        if i==2: return self.max_x
        if i==3: return self.max_y
        raise IndexError

