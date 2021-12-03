from .BaseServer import BaseServer
from .BaseServer import AduneoError
from .Configuration import Configuration
from .CryptoTools import CryptoTools
from .Help import Help
from .OIDCClientAdmin import OIDCClientAdmin
from .OIDCClientAdminGuide import OIDCClientAdminGuide
from .OIDCClientLogin import OIDCClientLogin
from .OIDCClientLogout import OIDCClientLogout
from .SAMLClientAdmin import SAMLClientAdmin
from .SAMLClientLogin import SAMLClientLogin
from .SAMLClientLogout import SAMLClientLogout
import base64
import datetime
import html
import http.cookies
import jwcrypto.jwt
import os
import requests
import traceback
import urllib.parse
import uuid


class Server(BaseServer):

  conf = Configuration.read_configuration('fedclient.cnf')


  def __init__(self, request, client_address, server): 
    
    self.row_number = 0  # pour l'affichage des tableaux de résultat
    super().__init__(request, client_address, server)


  def do_HEAD(self):
    return

    
  def do_GET(self):
  
    print(self.path)
    
    self.check_session()
    
    if self.path == '/favicon.ico':
      self.send_image('favicon.png')
    elif self.path.startswith('/images/') and self.path.endswith('.png'):
      self.send_static('images', self.path[8:])
    elif self.path.startswith('/css/') and self.path.endswith('.css'):
      self.send_static('css', self.path[5:])
    elif self.path.startswith('/javascript/') and self.path.endswith('.js'):
      self.send_static('javascript', self.path[12:])
    else:
  
      url_items = urllib.parse.urlparse(self.path)
      method_name = 'get' + url_items.path.replace('/', '_')
      
      if (method_name in dir(self)):
        eval('self.'+method_name+'()')
      else:
        self.send_page('404 !', code=404)
      
    
  def do_POST(self):
  
    print(self.path)
    
    # On ne crée pas la session si elle n'existe pas à cause du problème SameSite SAML
    #   De toute façon si on accède à l'application par un premier POST, ce n'est pas normal
    self.check_session(create_session=False)
    self.parse_post()
  
    url_items = urllib.parse.urlparse(self.path)
    method_name = 'post' + url_items.path.replace('/', '_')
    
    if (method_name in dir(self)):
      eval('self.'+method_name+'()')
    else:
      self.send_page('404 !')

    
  def get_(self):

    """
    homepage
    
    mpham 27/01/2021 - 28/02/2021
    """
  
    self.add_content("""
      <script>
      function authOIDC(spId) {
        location.href = '/oidc/client/preparerequest?id='+oidcId
      }
      function removeOIDC(rpId, name) {
        if (confirm("Remove OIDC client "+name+'?')) {
          location.href = '/oidc/client/removeclient?id='+rpId;
        }
      }
      function authSAML(spId) {
        location.href = '/saml/client/preparerequest?id='+oidcId
      }
      function removeSAML(spId, name) {
        if (confirm("Remove SAML SP "+name+'?')) {
          location.href = '/saml/client/removeclient?id='+spId;
        }
      }
      </script>
      <div>
      <span><a href="/oidc/client/modifyclient" class="button">Add OIDC Client</a></span>
      <span><a href="/saml/client/modifyclient" class="button">Add SAML SP</a></span>
      </div>

      <h2>OpenID Connect Clients (Relaying Parties)</h2>
    """)
    
    for rp_id in Server.conf['oidc_clients']:
      rp = Server.conf['oidc_clients'][rp_id]
      self.add_content('<div class="idpList">')
      self.add_content('<span style="cursor: pointer; min-height: 100%; display: inline-flex; align-items: center;" onclick="authOIDC(\''+html.escape(rp_id)+'\')">'+html.escape(rp['name'])+'</span>')
      self.add_content('<span>')
      if (self.is_logged('oidc_client_'+rp_id)):
        self.add_content('<span style="heigth: 100%; display: inline-block; vertical-align: middle;"><img src="/images/logged.png" /></span>')
      self.add_content('<span><a href="/oidc/client/preparerequest?id='+html.escape(rp_id)+'" class="middlebutton">Login</a></span>')
      self.add_content('<span><a href="/oidc/client/preparelogoutrequest?id='+html.escape(rp_id)+'" class="middlebutton">Logout</a></span>')
      self.add_content('<span><a href="/oidc/client/modifyclient?id='+html.escape(rp_id)+'" class="middlebutton">Config</a></span>')
      self.add_content('<span class="middlebutton" onclick="removeOIDC(\''+html.escape(rp_id)+'\', \''+rp['name']+'\')">Remove</span>')
      self.add_content('</span>')
      self.add_content('</div>')

    self.add_content('<h2>SAML Service Providers</h2>')
    for sp_id in Server.conf['saml_clients']:
      sp = Server.conf['saml_clients'][sp_id]
      self.add_content('<div class="idpList">')
      self.add_content('<span style="cursor: pointer; min-height: 100%; display: inline-flex; align-items: center;" onclick="authSAML(\''+html.escape(sp_id)+'\')">'+html.escape(sp['name'])+'</span>')
      self.add_content('<span>')
      if (self.is_logged('saml_client_'+sp_id)):
        self.add_content('<span style="heigth: 100%; display: inline-block; vertical-align: middle;"><img src="/images/logged.png" /></span>')
      self.add_content('<span><a href="/saml/client/preparerequest?id='+html.escape(sp_id)+'" class="middlebutton">Login</a></span>')
      self.add_content('<span><a href="/saml/client/preparelogoutrequest?id='+html.escape(sp_id)+'" class="middlebutton">Logout</a></span>')
      self.add_content('<span><a href="/saml/client/modifyclient?id='+html.escape(sp_id)+'" class="middlebutton">Config</a></span>')
      self.add_content('<span class="middlebutton" onclick="removeSAML(\''+html.escape(sp_id)+'\', \''+sp['name']+'\')">Remove</span>')
      self.add_content('</span>')
      self.add_content('</div>')
    
    self.send_page()


  def get_help(self):
  
    """
    Retourne les rubriques d'aide sous forme de JSON
      "header": "..."
      "content" : "...'
      
    mpham 13/04/2021
    """
    
    help_handler = Help(self)

    try:
      help_handler.send_help()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_oidc_client_preparerequest(self):

    """
    Prépare la requête d'authentification OIDC
      
    mpham 05/03/2021
    """

    oidc_client_login = OIDCClientLogin(self)
    
    try:
      oidc_client_login.prepare_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_oidc_client_sendrequest(self):

    """
    Récupère les informations saisies dans /oidc/client/preparerequest pour les mettre dans la session
      (avec le state comme clé)
    Redirige vers l'IdP grâce à la requête générée dans /oidc/client/preparerequest et placée dans le paramètre authentication_request
      
    mpham 05/03/2021
    """

    oidc_client_login = OIDCClientLogin(self)
    
    try:
      oidc_client_login.send_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_oidc_client_callback(self):

    """
    Retour d'authentification
    
    mpham 05/03/2021
    """

    oidc_client_login = OIDCClientLogin(self)
    
    try:
      oidc_client_login.callback()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_oidc_client_preparelogoutrequest(self):

    """
      Prépare la requête de déconnexion OIDC
      
      mpham 01/03/2021
    """

    oidc_logout = OIDCClientLogout(self)
    
    try:
      oidc_logout.prepare_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_oidc_client_sendlogoutrequest(self):
    
    """
    Récupère les informations saisies dans /oidc/preparelogoutrequest pour les mettre dans la session
      (avec le state comme clé)
    Redirige vers l'IdP grâce à la requête générée dans /oidc/preparelogoutrequest et placée dans le paramètre logout_request
    
    mpham 01/03/2021
    """

    oidc_logout = OIDCClientLogout(self)

    try:
      oidc_logout.send_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_oidc_client_logoutcallback(self):

    oidc_logout = OIDCClientLogout(self)

    try:
      oidc_logout.callback()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_oidc_client_modifyclient(self):

    oidc_client_admin = OIDCClientAdmin(self)

    try:
      oidc_client_admin.display()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_oidc_client_modifyclient(self):

    oidc_client_admin = OIDCClientAdmin(self)

    try:
      oidc_client_admin.modify()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_oidc_client_modifyclient_guide(self):

    oidc_client_admin = OIDCClientAdminGuide(self)

    try:
      oidc_client_admin.display()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_oidc_client_modifyclient_guide(self):

    oidc_client_admin = OIDCClientAdminGuide(self)

    try:
      oidc_client_admin.modify()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)
    
    
  def get_oidc_client_removeclient(self):
    
    """
    Supprime un client OpenID Connect
    
    mpham 28/12/2021
    """

    oidc_client_admin = OIDCClientAdmin(self)

    try:
      oidc_client_admin.remove()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)
      
    
  def get_saml_client_preparerequest(self):

    """
      Prépare la requête d'authentification SAML
      
      mpham 02/03/2021
    """

    saml_client_login = SAMLClientLogin(self)
    
    try:
      saml_client_login.prepare_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_saml_client_sendrequest(self):

    """
      Envoie la requête d'authentification SAML
      
      mpham 04/03/2021
    """
    
    saml_client_login = SAMLClientLogin(self)
    
    try:
      saml_client_login.send_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_saml_client_acs(self):

    """
      réceptionne la réponse SAML
      
      mpham 02/03/2021
    """
    
    saml_client_login = SAMLClientLogin(self)
    
    try:
      saml_client_login.authcallback()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_saml_client_preparelogoutrequest(self):

    """
      Prépare la requête de déconnexion SAML
      
      mpham 11/03/2021
    """

    saml_logout = SAMLClientLogout(self)
    
    try:
      saml_logout.prepare_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_saml_client_sendlogoutrequest(self):
    
    """
    Récupère les informations saisies dans /saml/client/preparelogoutrequest pour les mettre dans la session
      (avec le state comme clé)
    Redirige vers l'IdP grâce à la requête générée dans /saml/client/preparelogoutrequest et placée dans le paramètre logout_request
    
    mpham 11/03/2021
    """

    saml_logout = SAMLClientLogout(self)

    try:
      saml_logout.send_request()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_saml_client_logoutcallback(self):

    saml_logout = SAMLClientLogout(self)

    try:
      saml_logout.callback()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_saml_client_modifyclient(self):


    saml_client_admin = SAMLClientAdmin(self)

    try:
      saml_client_admin.display()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def post_saml_client_modifyclient(self):


    saml_client_admin = SAMLClientAdmin(self)

    try:
      saml_client_admin.modify()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_saml_client_removeclient(self):
    
    """
    Supprime un client SAML
    
    mpham 06/03/2021
    """

    saml_client_admin = SAMLClientAdmin(self)

    try:
      saml_client_admin.remove()
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)


  def get_downloadservercertificate(self):
    
    """
    Retourne le certificat du serveur (utilisé pour le SSL)
    """
    
    certificate_filename = self.server.ssl_params.get('server_certificate')
    if certificate_filename is None:
      send_page('Certificate not configured', code=400, clear_buffer=True)
      return
    
    download_filename = certificate_filename
    if download_filename.startswith('temp_'):
      download_filename = 'aduneo.crt'
    
    certificate_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf', certificate_filename)

    self.send_response(200)
    self.send_header('Content-type', 'application/x-pem-file')
    self.send_header('Content-disposition', 'filename='+download_filename)
    self.end_headers()
    
    in_file = open(certificate_path, 'rb')
    while chunk := in_file.read(1024):
      self.wfile.write(chunk)
    in_file.close()


  def get_generatecertificate(self):
  
    """
    Génère un biclé, un certificat autosigné avec la clé publique et retourne clé privée et certificat en format PEM
    """
  
    try:
      (private_key, certificate) = CryptoTools.generate_key_self_signed()
      json_result = {"private_key": private_key, "certificate": certificate}
      self.send_json(json_result)
    except AduneoError as error:
      self.send_page(str(error), clear_buffer=True)
    
    
  def get_tpl(self):  
    self.send_template('test.html', titre='Ceci est un titre', nom='Jean Moulin')
   
  