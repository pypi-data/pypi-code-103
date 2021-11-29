def eval_curve(curves,name,input):
    c = curves[name]
    x = min(c['max_x'],max(c['min_x'],input[0]))
    if c['type']=='Quadratic':
        out = c['a0'] + c['a1']*x + c['a2']*x**2
    elif c['type']== 'Cubic':
        out = c['a0'] + c['a1']*x + c['a2']*x**2 + c['a3']*x**3
    elif c['type']=='Biquadratic':
        y = min(c['max_y'],max(c['min_y'],input[1]))
        out = c['a0'] + c['a1']*x + c['a2']*x**2 + c['b1']*y + c['b2']*y**2 + c['ab']*x*y
    elif c['type']=='Bicubic':
        y = min(c['max_y'],max(c['min_y'],input[1]))
        out = c['a0'] + c['a1']*x + c['a2']*x**2 + c['a3']*x**3 + c['b1']*y + c['b2']*y**2 + c['b3']*y**3 + c['ab']*x*y + c['aab']*x**2*y + c['abb']*x*y**2
    elif c['type']=='ChillerPartLoadWithLift':
        y = min(c['max_y'],max(c['min_y'],input[1]))
        z = input[2]
        out = c['a0'] + c['a1']*x + c['a2']*x**2 + c['a3']*x**3 + c['b1']*y + c['b2']*y**2 + c['b3']*y**3 + c['ab']*x*y + c['aab']*x**2*y + c['abb']*x*y**2 + c['aabb']*x**2*y**2 + c['cb3']*z*y**3
    return out