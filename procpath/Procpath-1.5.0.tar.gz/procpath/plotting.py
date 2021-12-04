import collections
import itertools
import math
import tempfile
from functools import partial
from typing import Dict, List

import pygal.formatters
import pygal.style


__all__ = 'decimate', 'moving_average', 'plot'


def get_line_distance(p0: tuple, p1: tuple, p2: tuple) -> float:
    """
    Return the distance from p0 to the line formed by p1 and p2.

    Points are represented by 2-tuples.
    """

    if p1 == p2:
        return math.hypot(p1[0] - p0[0], p1[1] - p0[1])

    slope_nom = p2[1] - p1[1]
    slope_denom = p2[0] - p1[0]

    return (
        abs(slope_nom * p0[0] - slope_denom * p0[1] + p2[0] * p1[1] - p2[1] * p1[0])
        / math.hypot(slope_denom, slope_nom)
    )


def decimate(points, epsilon: float) -> list:
    """
    Decimate given poly-line using Ramer-Douglas-Peucker algorithm.

    It reduces the points to a simplified version that loses detail,
    but retains its peaks.
    """

    if len(points) < 3:
        return points

    dist_iter = map(partial(get_line_distance, p1=points[0], p2=points[-1]), points[1:-1])
    max_index, max_value = max(enumerate(dist_iter, start=1), key=lambda v: v[1])

    if max_value > epsilon:
        return (
            decimate(points[:max_index + 1], epsilon)[:-1]
            + decimate(points[max_index:], epsilon)
        )
    else:
        return [points[0], points[-1]]


def moving_average(iterable, n: int):
    """
    Moving average generator function.

    https://docs.python.org/3/library/collections.html#deque-recipes
    """

    it = iter(iterable)
    d = collections.deque(itertools.islice(it, n - 1))
    d.appendleft(0)
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / n


def plot(
    pid_series_list: List[Dict[int, List[float]]],
    queries: list,
    plot_file: str,
    *,
    title: str = None,
    style: str = None,
    formatter: str = None,
    share_y_axis: bool = False,
    logarithmic: bool = False,
):
    assert pid_series_list and len(pid_series_list) == len(queries)
    assert share_y_axis or len(pid_series_list) <= 2

    if not title:
        if share_y_axis:
            title = '; '.join(f'{i}. {q.title}' for i, q in enumerate(queries, start=1))
        elif len(queries) == 1:
            title = queries[0].title
        else:
            title = f'{queries[0].title} vs {queries[1].title}'

    with tempfile.NamedTemporaryFile('w') as f:
        f.write(_pygal_js)
        f.flush()

        datetimeline = pygal.DateTimeLine(
            width=912,
            height=684,
            show_dots=False,
            logarithmic=logarithmic,
            x_label_rotation=35,
            title=title,
            value_formatter=getattr(pygal.formatters, formatter or 'human_readable'),
            style=getattr(pygal.style, style or 'DefaultStyle'),
            js=[f'file://{f.name}'],  # embed "pygal-tooltips.min.js"
        )

        for i, (query, pid_series) in enumerate(zip(queries, pid_series_list)):
            for pid, points in pid_series.items():
                datetimeline.add(
                    '{name} {pid}'.format(pid=pid, name=query.name or f'№{i + 1}'),
                    points,
                    secondary=not share_y_axis and bool(i),
                )

        datetimeline.render_to_file(plot_file)


# Original content of this script is embedded to make SVGs work offline
# https://kozea.github.io/pygal.js/2.0.x/pygal-tooltips.min.js
#
# Copyright © 2015 Florian Mounier Kozea LGPLv3
_pygal_js = (
    '/*! pygal.js           2015-10-30 */\n'
    r'(function(){var a,b,c,d,e,f,g,h,i,j,k;i="http://www.w3.org/2000/svg",k="http://www'
    r'.w3.org/1999/xlink",a=function(a,b){return null==b&&(b=null),b=b||document,Array.p'
    r'rototype.slice.call(b.querySelectorAll(a),0).filter(function(a){return a!==b})},e='
    r'function(a,b){return(a.matches||a.matchesSelector||a.msMatchesSelector||a.mozMatch'
    r'esSelector||a.webkitMatchesSelector||a.oMatchesSelector).call(a,b)},h=function(a,b'
    r'){return null==b&&(b=null),Array.prototype.filter.call(a.parentElement.children,fu'
    r'nction(c){return c!==a&&(!b||e(c,b))})},Array.prototype.one=function(){return this'
    r'.length>0&&this[0]||{}},f=5,j=null,g=/translate\((\d+)[ ,]+(\d+)\)/,b=function(a){'
    r'return(g.exec(a.getAttribute("transform"))||[]).slice(1).map(function(a){return+a}'
    r')},c=function(c){var d,g,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,A,B,C,D,E,F,G,H;for(a("svg"'
    r',c).length?(o=a("svg",c).one(),q=o.parentElement,g=o.viewBox.baseVal,d=q.getBBox()'
    r',w=function(a){return(a-g.x)/g.width*d.width},x=function(a){return(a-g.y)/g.height'
    r'*d.height}):w=x=function(a){return a},null!=(null!=(E=window.pygal)?E.config:void '
    r'0)?null!=window.pygal.config.no_prefix?l=window.pygal.config:(u=c.id.replace("char'
    r't-",""),l=window.pygal.config[u]):l=window.config,s=null,n=a(".graph").one(),t=a("'
    r'.tooltip",c).one(),F=a(".reactive",c),y=0,B=F.length;B>y;y++)m=F[y],m.addEventList'
    r'ener("mouseenter",function(a){return function(){return a.classList.add("active")}}'
    r'(m)),m.addEventListener("mouseleave",function(a){return function(){return a.classL'
    r'ist.remove("active")}}(m));for(G=a(".activate-serie",c),z=0,C=G.length;C>z;z++)m=G'
    r'[z],p=m.id.replace("activate-serie-",""),m.addEventListener("mouseenter",function('
    r'b){return function(){var d,e,f,g,h,i,j,k;for(i=a(".serie-"+b+" .reactive",c),e=0,g'
    r'=i.length;g>e;e++)d=i[e],d.classList.add("active");for(j=a(".serie-"+b+" .showable'
    r'",c),k=[],f=0,h=j.length;h>f;f++)d=j[f],k.push(d.classList.add("shown"));return k}'
    r'}(p)),m.addEventListener("mouseleave",function(b){return function(){var d,e,f,g,h,'
    r'i,j,k;for(i=a(".serie-"+b+" .reactive",c),e=0,g=i.length;g>e;e++)d=i[e],d.classLis'
    r't.remove("active");for(j=a(".serie-"+b+" .showable",c),k=[],f=0,h=j.length;h>f;f++'
    r')d=j[f],k.push(d.classList.remove("shown"));return k}}(p)),m.addEventListener("cli'
    r'ck",function(b,d){return function(){var e,f,g,h,i,j,k,l,m,n,o;for(g=a("rect",b).on'
    r'e(),h=""!==g.style.fill,g.style.fill=h?"":"transparent",m=a(".serie-"+d+" .reactiv'
    r'e",c),i=0,k=m.length;k>i;i++)f=m[i],f.style.display=h?"":"none";for(n=a(".text-ove'
    r'rlay .serie-"+d,c),o=[],j=0,l=n.length;l>j;j++)e=n[j],o.push(e.style.display=h?"":'
    r'"none");return o}}(m,p));for(H=a(".tooltip-trigger",c),A=0,D=H.length;D>A;A++)m=H['
    r'A],m.addEventListener("mouseenter",function(a){return function(){return s=r(a)}}(m'
    r'));return t.addEventListener("mouseenter",function(){return null!=s?s.classList.ad'
    r'd("active"):void 0}),t.addEventListener("mouseleave",function(){return null!=s?s.c'
    r'lassList.remove("active"):void 0}),c.addEventListener("mouseleave",function(){retu'
    r'rn j&&clearTimeout(j),v(0)}),n.addEventListener("mousemove",function(a){return!j&&'
    r'e(a.target,".background")?v(1e3):void 0}),r=function(c){var d,e,g,m,n,o,p,r,s,u,v,'
    r'y,z,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,$,_;for(clearTimeout(j),j='
    r'null,t.style.opacity=1,t.style.display="",G=a("g.text",t).one(),C=a("rect",t).one('
    r'),G.innerHTML="",v=h(c,".label").one().textContent,N=h(c,".x_label").one().textCon'
    r'tent,J=h(c,".value").one().textContent,O=h(c,".xlink").one().textContent,D=null,q='
    r'c,I=[];q&&(I.push(q),!q.classList.contains("series"));)q=q.parentElement;if(q)for('
    r'X=q.classList,R=0,S=X.length;S>R;R++)if(g=X[R],0===g.indexOf("serie-")){D=+g.repla'
    r'ce("serie-","");break}for(y=null,null!==D&&(y=l.legends[D]),o=0,u=[[v,"label"]],Y='
    r'J.split("\n"),r=V=0,T=Y.length;T>V;r=++V)E=Y[r],u.push([E,"value-"+r]);for(l.toolt'
    r'ip_fancy_mode&&(u.push([O,"xlink"]),u.unshift([N,"x_label"]),u.unshift([y,"legend"'
    r'])),H={},W=0,U=u.length;U>W;W++)Z=u[W],s=Z[0],z=Z[1],s&&(F=document.createElementN'
    r'S(i,"text"),F.textContent=s,F.setAttribute("x",f),F.setAttribute("dy",o),F.classLi'
    r'st.add(0===z.indexOf("value")?"value":z),0===z.indexOf("value")&&l.tooltip_fancy_m'
    r'ode&&F.classList.add("color-"+D),"xlink"===z?(d=document.createElementNS(i,"a"),d.'
    r'setAttributeNS(k,"href",s),d.textContent=void 0,d.appendChild(F),F.textContent="Li'
    r'nk >",G.appendChild(d)):G.appendChild(F),o+=F.getBBox().height+f/2,e=f,void 0!==F.'
    r'style.dominantBaseline?F.style.dominantBaseline="text-before-edge":e+=.8*F.getBBox'
    r'().height,F.setAttribute("y",e),H[z]=F);return K=G.getBBox().width+2*f,p=G.getBBox'
    r'().height+2*f,C.setAttribute("width",K),C.setAttribute("height",p),H.value&&H.valu'
    r'e.setAttribute("dx",(K-H.value.getBBox().width)/2-f),H.x_label&&H.x_label.setAttri'
    r'bute("dx",K-H.x_label.getBBox().width-2*f),H.xlink&&H.xlink.setAttribute("dx",K-H.'
    r'xlink.getBBox().width-2*f),M=h(c,".x").one(),Q=h(c,".y").one(),L=parseInt(M.textCo'
    r'ntent),M.classList.contains("centered")?L-=K/2:M.classList.contains("left")?L-=K:M'
    r'.classList.contains("auto")&&(L=w(c.getBBox().x+c.getBBox().width/2)-K/2),P=parseI'
    r'nt(Q.textContent),Q.classList.contains("centered")?P-=p/2:Q.classList.contains("to'
    r'p")?P-=p:Q.classList.contains("auto")&&(P=x(c.getBBox().y+c.getBBox().height/2)-p/'
    r'2),$=b(t.parentElement),A=$[0],B=$[1],L+K+A>l.width&&(L=l.width-K-A),P+p+B>l.heigh'
    r't&&(P=l.height-p-B),0>L+A&&(L=-A),0>P+B&&(P=-B),_=b(t),m=_[0],n=_[1],m===L&&n===P?'
    r'c:(t.setAttribute("transform","translate("+L+" "+P+")"),c)},v=function(a){return j'
    r'=setTimeout(function(){return t.style.display="none",t.style.opacity=0,null!=s&&s.'
    r'classList.remove("active"),j=null},a)}},d=function(){var b,d,e,f,g;if(d=a(".pygal-'
    r'chart"),d.length){for(g=[],e=0,f=d.length;f>e;e++)b=d[e],g.push(c(b));return g}},"'
    r'loading"!==document.readyState?d():document.addEventListener("DOMContentLoaded",fu'
    r'nction(){return d()}),window.pygal=window.pygal||{},window.pygal.init=c,window.pyg'
    r'al.init_svg=d}).call(this);'
)
