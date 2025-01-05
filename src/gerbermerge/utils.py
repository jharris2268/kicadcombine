get_num=lambda x: ('f',float(x)) if '.' in x else ('i', int(x))

num_str=lambda i,p: '%d' % p if i=='i' else '%0.6f' % p
num_str_null=lambda w, x: '' if x is None else "%s%s" % (w,num_str(*x))

num_repr=lambda x: '' if x is None else "%s %s" % (x[0],x[1])
