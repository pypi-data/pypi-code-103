#!/usr/bin/env python3
import web,sys,os,socket
from os import path
import re
from pathlib import Path
from io import BytesIO
from .. import yxsfile
from .. import encrypt
from urllib.parse import quote,unquote
# from base64 import b64encode,b64decode
# sys.argv.append('8088')
#这是一个基于web.py的文件服务器
urls = (   
    '/file_downloader/.*','download',
    '/player_/.*','player',
    '/.*','FileSystem')
file_render=web.template.render('.',cache=False)
global_text_suffix=set(['.html','.js','.css'])
def generate_html(body,dirname):
    def write_element(urlt,namet):
        fs3 = '     <li><a href="{i}">{j}</a></li>\n'
        fimage = '<img src="{i}" border="0"><br>'
        for ftyp in ('.jpg','.jpeg','.png','.webp'):
            if urlt.endswith(ftyp):
                ft = fimage.format(i = urlt)
                break 
        else:
            ft = fs3.format(i=urlt,j=namet)
        return ft
    html_string1 = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>

<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html" />
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="description" content="" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=0, minimum-scale=1.0, maximum-scale=1.0">
<style>
.showimg img{
background-size:contain|cover;
width:100%;
height: auto;
}   
</style>   
'''
    fs1 = '<title>Directory listing for /{dirname}/</title>'
    html_string2='''</head>

<script>
    function change(){  
        document.getElementById("file_name").value=document.getElementById("file_content").value;  
    }  
</script>
<body>
'''
    fs2 = '<h1>Directory listing for /{dirname}/</h1>'
    html_string3 = '''<hr>
<form method="post"  enctype="multipart/form-data">
    <div class="showimg">  
        <button type="button" class="btn btn-primary" id="select_file"  
                onclick="file_content.click();">Scan file  
        </button>  
        <input type="file" class="form-control" id="file_content" name="file_content"  
               style="display: none;" onchange="change();">  
        <input type="text" class="form-control" id="file_name" name="file_name"  
               readonly="readonly" onclick="file_content.click(); ">  
        <input type="submit" value="Submit file" />
    </div>  
</form>
</hr>
<hr>
<form method="post"  enctype="multipart/form-data">
    <div class="showimg">  
        <input type="submit" value="Submit file" /></br>
        <ul>
    '''
        # $for i,j in body:
    # fs3 = '     <label><input name="{i}" type="checkbox" value=""/><a href="{i}">{j}</a></label> </br>\n'
    
    html_string4='''    </ul>
</div>  
</form>
</hr>
</body>
</html>
'''
    html_bytes = BytesIO()
    html_bytes.write(html_string1.encode('utf8'))
    html_bytes.write(fs1.format(dirname = dirname).encode('utf8'))
    html_bytes.write(html_string2.encode('utf8'))
    html_bytes.write(fs2.format(dirname = dirname).encode('utf8'))
    html_bytes.write(html_string3.encode('utf8'))
    a = [write_element(i,j) for i,j in body]
    html_bytes.write(''.join(a).encode('utf8'))
    html_bytes.write(html_string4.encode('utf8'))
    length = html_bytes.tell()
    html_bytes.seek(0,0)
    web.header('Content-Type','text/html')
    web.header('Content-Length',str(length))
    return html_bytes


def encode(url):
    return quote(url)
    # return url
    # return b64encode(url.encode('utf8')).decode('utf8')
def decode(url):
    return unquote(url)
    # return url
    # return b64decode(url.encode()).decode('utf8')
class FileSystem:
    def GET(self,*d):
        url=web.url()
        hp  = web.input()
        url=decode(url)
        url = '.'+url
        url_path = Path(url)
        if url_path.is_dir():
            p=url
            if p[-1] != '/':
                raise web.seeother(url[1:]+'/')
        else:
            if url.endswith('mp4') or url.endswith('mpxs'):
                if not hp:
                    raise web.seeother('/player_/auto'+encode(url)+'?first=ok')
                else:
                    web.seeother('/file_downloader/x'+encode(url))
            return send_file(url)
        x=os.listdir(p)
        index_file = url_path / 'index.html'
        if index_file.is_file():
            return send_file(str(index_file))
        a=[]
        for i in x:
            filename=p+i
            if path.isfile(filename):
                a.append([i,i])
            else:
                a.append([i+os.sep,i+os.sep])
        a.sort(key=lambda x:x[1][-1])
        for i in a:
            i[0]=encode(i[0])
        return generate_html(a,url_path.name)
        # return file_render.file(a,path.split(p[:-1])[1])

def send_file(filename):
    pre_suffix = Path(filename).suffix
    if not path.exists(filename):
        if filename.endswith('.vtt'):
            p = Path(filename).with_suffix('.mpxs')
            if p.is_symlink():
                p = p.resolve()
            dn = yxsfile.yxsFile(p).decode_filename()
            filename = yxsfile.yxsFile(dn.with_suffix('.vtt')).encode_filename()
        else:
            return None
    ct = web.ctx.env.get('CONTENT_TYPE')
    fp = open(filename,'rb')
    offset = 0
    length0 = path.getsize(filename)
    if ct is None:
        suffix = Path(filename).suffix.lower()
        if suffix == '.html':
            ct = 'text/html'
        elif suffix == '.js':
            ct = 'text/javascript'
        elif suffix == '.css':
            ct = 'text/css'
        elif pre_suffix == '.vtt':
            ct = 'text'
            offset=2048
            fp.read(2048)
        elif suffix == '.mp4':
            ct = 'video/mp4'
        elif suffix == '.mpxs':
            ct = 'video/mp4'
            fp.read(2048)
            offset = 2048
        elif suffix == '.jpxs':
            ct = 'application/octet-stream'
            fp.read(2048)
            offset = 2048
        else:
            ct = 'application/octet-stream'
        if suffix in global_text_suffix:
            data = fp.read()
            fp = BytesIO()
            if data[:10] == b'SP_ENCRYPT':
                data = encrypt.b64decode(data[10:],passwd=encrypt.get_default_passwd())
            offset = length0 - len(data)
            fp.write(data)
            fp.seek(0,0)
    web.header('Content-Type',ct)
    web.header('Content-Length',str(length0-offset))
    return fp
    

def download_file(fp,length,file_name='package',hrange = None):
    BUF_SIZE=1024*1024*2
    try:
        ct = web.ctx.env.get('CONTENT_TYPE')
        offset = 0
        if ct is None:
            suffix = Path(file_name).suffix.lower()
            if suffix == '.html':
                ct = 'text/html'
            elif suffix == '.js':
                ct = 'text/javascript'
            elif suffix == '.css':
                ct = 'text/css'
            elif suffix == '.mp4':
                ct = 'video/mp4'
            elif suffix == '.mpxs':
                ct = 'video/mp4'
                offset = 2048
            else:
                ct = 'application/octet-stream'
        
        web.header('Content-Type',ct)
        # 下载则加以下head
        # web.header('Content-disposition', 'attachment; filename={name}'.format(name=quote(file_name)))
        
        # Content-Range: bytes 2293762-3342338/145108958
        start = 0
        if hrange:
            web.ctx.status = '206 PartialContent'
            hrange = hrange[6:].split('-')
            ipos = int(hrange[0])
            fp.seek(ipos+offset,0)
            start = ipos
            # if len(hrange) == 2 and hrange[1]:
            #     BUF_SIZE = int(hrange[1]) - ipos
        fs = 'bytes {}-{}/{}'
        # print(206,'HTTP_RANGE',hrange)
        while True:
            
            c = fp.read(BUF_SIZE)
            if c:
                end = start + len(c)-1
                web.header('Content-Range',fs.format(start,end,length-offset))
                start = end
                yield c
            else:
                web.header('Content-Range',fs.format(start,start,length-offset))
                yield   b''
                break
        
    except Exception as err:
        print(err)
        yield 'Error'
    finally:
        if fp:
            fp.close()
class player:
    player_html = '''<video controls autoplay>
    <source src="{mp4}?play=ok"  type="video/mp4" />
    <track  kind="subtitles" srclang="zh-cn" src="{vtt}" default>
</video>'''
    def GET(self):
        url=web.url()
        hp = web.input()
        file_name=decode(url)[13:]
        if file_name.startswith('./'):file_name = file_name[1:]
        if file_name[0] != '/':file_name = '/'+file_name
        if 'first' in hp:
            html_string1 = self.player_html.format(mp4=file_name,vtt=Path(file_name).with_suffix('.vtt'))
            html_bytes = BytesIO()
            html_bytes.write(html_string1.encode('utf8'))
            length = html_bytes.tell()
            html_bytes.seek(0,0)
            web.header('Content-Type','text/html')
            web.header('Content-Length',str(length))
            return html_bytes
        else:
            web.seeother('/file_downloader/x'+encode(file_name))
 
        

class download:
    def GET(self):
        url=web.url()[18:]
        file_name=decode(url)
        f = open(file_name, "rb")
        length=path.getsize(file_name)
        hrange = web.ctx.env.get('HTTP_RANGE',None)
        for i in download_file(f,length,path.basename(file_name),hrange=hrange):
            yield i
            if hrange:
                break
def getip():
    out = os.popen("ifconfig").read()
    k = re.findall('(?<=inet) +\\d+\\.\\d+\\.\\d+\\.\\d+',out)
    ips = [i.lstrip() for i in k]
    ips = [i for i in ips if i!='127.0.0.1']
    if ips:
        return ' '.join(ips)
    else:
        return socket.gethostbyname(socket.gethostname())
def main(port,ssl):
    x=getip()
    print('本机ip：{ip}'.format(ip=x))
    sys.argv = sys.argv[:1]
    if port:
        sys.argv.append(str(port))
    if ssl:
        from cheroot.server import HTTPServer
        from cheroot.ssl.builtin import BuiltinSSLAdapter
        yxspkg_rc = Path.home() /'.yxspkg'/'.ssl'
        crt = yxspkg_rc/ 'yxs_server.crt'
        key = yxspkg_rc/ 'yxs_server.key'
        if not crt.exists() or not key.exists():
            print('The files yxs_server.crt or yxs_server.key are not fond in {}'.format(yxspkg_rc))
        HTTPServer.ssl_adapter = BuiltinSSLAdapter(
            certificate=crt, 
            private_key=key)
    app=web.application(urls, globals ())
    app.run()
if __name__ == '__main__': 
    main(8080,False)
    
    
