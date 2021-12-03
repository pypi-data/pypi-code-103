"""
  Dépendances :
    OpenSSL (génération d'une clé privée et d'un certificat)
    
  Si le certificat (et la clé) SSL n'est pas donné dans le paramètre de configuration server/ssl_cert_file (et server/ssl_key_file)
    un certificat temporaire est généré
"""
from .Configuration import Configuration
from .CryptoTools import CryptoTools
import os
import ssl
import time
from http.server import HTTPServer
from .server import Server
from socketserver import ThreadingMixIn
import threading

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    

if __name__ == '__main__':
    
    conf = Configuration.read_configuration('fedclient.cnf')
    host = conf['server']['host']
    port = int(conf['server']['port'])

    # On est passé en ThreadedHTTPServer et non en HTTPServer à cause de problèmes de connexion en mode incognito (https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/BaseHTTPServer/index.html)
    httpd = ThreadedHTTPServer((host, port), Server)
    # Pour s'assurer que Ctrl-C fonctionne (https://blog.sverrirs.com/2016/11/simple-http-webserver-python.html)
    httpd.daemon_threads = True
    httpd.ssl_params = {}
    
    # SSL
    httpd.secure = False
    if Configuration.is_on(conf['server']['ssl']):
    
      httpd.secure = True
      conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
      
      if conf['server'].get('ssl_cert_file') is None:
        CryptoTools.generate_temp_certificate(conf)
        httpd.ssl_params['key_temp_files'] = True

      context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
      context.load_cert_chain(certfile=conf_dir+'/'+conf['server']['ssl_cert_file'], keyfile=conf_dir+'/'+conf['server']['ssl_key_file'])
      
      httpd.ssl_params['server_private_key'] = conf['server']['ssl_key_file']
      httpd.ssl_params['server_certificate'] = conf['server']['ssl_cert_file']
      
      httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
      
    scheme = 'http'
    if httpd.secure:
      scheme = 'https'
    print(time.asctime(), 'Server UP - %s:%s' % (scheme+'://'+host, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (scheme+'://'+host, port))
    
    if httpd.ssl_params.get('key_temp_files'):
      os.unlink(conf_dir+'/'+conf['server']['ssl_key_file'])
      os.unlink(conf_dir+'/'+conf['server']['ssl_cert_file'])