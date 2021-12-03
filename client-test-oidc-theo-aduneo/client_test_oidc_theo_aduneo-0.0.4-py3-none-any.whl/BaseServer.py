import html
import http.cookies
import json
import os
import urllib.parse
import uuid

from http.server import BaseHTTPRequestHandler


class BaseServer(BaseHTTPRequestHandler):

  sessions = {}

  def __init__(self, request, client_address, server): 
  
    """
    le membre sessionid contient l'identifiant de session
    il est généré dans set_session_value() (s'il n'existe pas déjà)

    Attention, ne rien mettre après super(), car ce ne sera exécuté qu'après le traitement de la page
    
    mpham 27/01/2021
    """
    
    self.top_sent = False
    self.content = ''
    self.session_id = None
    self.post_form = None
    super().__init__(request, client_address, server)
    
   
  def parse_post(self):

    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length).decode('utf-8')
    
    self.post_form = {}
    for item in post_data.split('&'):
      equalsPos = item.find('=')
      if equalsPos == -1:
        self.post_form[item] = ''
      else:
        key = urllib.parse.unquote_plus(item[:equalsPos])
        self.post_form[key] = urllib.parse.unquote_plus(item[equalsPos+1:])
        

  def add_content(self, content):

    if self.top_sent:
      page = bytes(content, "UTF-8")
      self.wfile.write(page)
    else:
      self.content += content

   
  def send_page(self, content = '', code=200, clear_buffer=False):
    
    """
    envoie une page au navigateur
    
    mpham 27/01/2021 - 24/02/2021
    """
    
    if clear_buffer:
      self.content = ''
    
    self.send_page_top(code)
    
    page = bytes(self.content + content, "UTF-8")
    self.wfile.write(page)
    
    self.send_page_bottom()


  def send_page_top(self, code=200, template=True, send_cookie=True):
    
    """
    envoie le haut d'une page
    
    mpham 24/02/2021
    """
    
    self.send_response(code)
    self.send_header('Content-type', 'text/html; charset=utf-8')
    if send_cookie and self.session_id is not None:
      self.send_header('Set-Cookie', 'fedclient_sessionid='+self.session_id+'; Max-Age=1200; HttpOnly; path=/;')
    self.end_headers()
    
    if (template):
      header = "<html><head><title>Aduneo - Identity Federation Test</title>"
      header += '<link rel="stylesheet" href="/css/aduneo.css">'
      header += '</head>'
      header += '<body><div style="color: #FFA500; font-family: Tahoma; font-size: 40px; background-color: #004c97; height: 74px;"><a href="https://www.aduneo.com"><img style="width: 294px; height: 64px; vertical-align: middle; margin-left: 8px; margin-top: 5px;" src="/images/aduneo.png"></a><span style="margin-left: 30px; vertical-align: middle;">Identity Federation Test</span>'
      header += '<a href="/"><img style="height: 36px; float: right; margin-top: 20px; margin-right: 20px" src="/images/home.png"></a></div>'
      header += '<div style="margin-top: 20px; margin-left: 50px; font-family: Verdana;">'
      page = bytes(header, "UTF-8")
      self.wfile.write(page)
    
    self.top_sent = True
    

  def send_page_bottom(self):
    
    """
    envoie le bas d'une page au navigateur
    
    mpham 24/02/2021
    """
    
    footer = '</div>'
    footer += "</body></html>"
    page = bytes(footer, "UTF-8")
    self.wfile.write(page)



  def send_redirection(self, url):
  
    """
    envoie une page au navigateur
    
    mpham 27/01/2021
    """
  
    self.send_response(302)
    self.send_header('location', url)
    if self.session_id is not None:
      self.send_header('Set-Cookie', 'fedclient_sessionid='+self.session_id+'; HttpOnly')
    self.end_headers()
    

  def send_json(self, dictionnary: dict):
    
    """
    Retourne un objet JSON
    
    mpham 13/04/2021
    """
    
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()

    content = bytes(json.dumps(dictionnary), "UTF-8")
    self.wfile.write(content)
      
      
  def send_image(self, path):
    
    """
    Les images sont nécessairement des PNG dans le dossier /static/images
    
    mpham 28/01/2021 - 12/02/2021 - 04/03/2021
    """

    self.send_static('images', path)


  def send_css(self, path):
    
    """
    Les styles sont nécessairement dans le dossier /static/css et se terminent par .css
    
    mpham 12/02/2021 - 04/03/2021
    """

    self.send_static('css', path)

  
  def send_javascript(self, path):
    
    """
    Les styles sont nécessairement dans le dossier /static/css et se terminent par .css
    
    mpham 12/02/2021 - 04/03/2021
    """

    self.send_static('javascript', path)

  
  def send_static(self, static_type: str, path: str):
    
    """
    Retourne un fichier static, placé dans le sous-dossier static_type du dossier static
    Vérifie que le fichier se trouve bien dans le dossier en question et que le chemin ne contient pas des ..
    
    mpham 12/02/2021 - 04/03/2021
    """
    
    content_type_map = {'images': 'image/png', 'css': 'text/css', 'javascript': 'text/javascript'}
    extension_map = {'images': '.png', 'css': '.css', 'javascript': '.js'}
    
    css_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', static_type)
    requested_path = os.path.join(css_dir, path)

    if not BaseServer.check_path_traversal(css_dir, requested_path):
      self.send_page('404 !', code=404, clear_buffer=True)
    elif not path.endswith(extension_map[static_type]):
      self.send_page('404 !', code=404, clear_buffer=True)
    else:
    
      self.send_response(200)
      self.send_header('Content-type', content_type_map[static_type])
      self.send_header('Cache-Control', 'public, max-age=3600')
      self.end_headers()
      
      in_file = open(requested_path, 'rb')
      while chunk := in_file.read(1024):
        self.wfile.write(chunk)
      in_file.close()


  def send_template(self, template_name:str, **parameters):
  
    """
    Mécanisme de template simplifié
    Fourniture du template par un nom de fichier dans le dossier templates
    
    mpham 16/08/2021
    """
  
    tpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    requested_path = os.path.join(tpl_dir, template_name)

    if not BaseServer.check_path_traversal(tpl_dir, requested_path):
      self.send_page('404 !', code=404, clear_buffer=True)
    else:
      with open(requested_path, mode='r', encoding="utf-8") as in_file:
        template_content = in_file.read()
        
      self.send_page(self.apply_template(template_content, **parameters))


  def apply_template(self, template:str, **parameters):
  
    """
    Mécanisme de template simplifié
    Fourniture du template directement en chaîne
    
    mpham 16/08/2021
    """
    
    from Template import Template
  
    return Template.apply_template(template, **parameters)

  
  def check_session(self, create_session=True):
  
    """
    Génère un identifiant de session s'il n'en existe pas déjà dans les cookies
    
    On appelle cette méthode en initialisation de GET et POST pour s'assurer qu'on envoie bien l'id de session
      dans les en-têtes
      
    On a eu en effet le cas où
    - on appelle send_page_top() avant d'avoir besoin de session
    - puis on ajoute une information dans la session qui n'existe pas
    - on génère donc un identifiant, mais comme les en-têtes ont déjà été envoyés, c'est trop tard
    
    mpham 01/03/2021
    """
    
    session_exists = False
    if self.headers.get('Cookie') is not None:
      cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
      if 'fedclient_sessionid' in cookies:
        self.session_id = cookies['fedclient_sessionid'].value
        session_exists = True
        
    if not session_exists and create_session:
      self.session_id = str(uuid.uuid4())

  
  def set_session_value(self, key, value):
    
    """
    met une variable en session
    
    mpham 27/01/2021
    """
    
    if self.sessions.get(self.session_id) is None:
      self.sessions[self.session_id] = {}
      
    self.sessions[self.session_id][key] = value
    
    
  def get_session_value(self, key):
    
    """
    récupère une variable de la session
    retourne None si elle n'existe pas
    
    mpham 27/01/2021
    """
    
    value = None
    
    if self.sessions.get(self.session_id) is not None:
      value = self.sessions[self.session_id].get(key)
      
    return value

    
  def del_session_value(self, key):
    
    """
    Supprime une variable de la session
    retourne None si elle n'existe pas
    
    mpham 01/03/2021
    """

    if self.session_id is not None:
      self.sessions[self.session_id].pop(key, None)
      

  def logon(self, idp_id, id_token = 'authenticated'):
    
    """
    Démarre une session authentifiée par un IdP
    
    mpham 01/03/2021
    """
    
    self.set_session_value('session_'+idp_id, id_token)
    
    
  def logoff(self, idp_id):
    
    """
    Met un terme à une session authentifiée par un IdP
    
    mpham 01/03/2021
    """
    
    self.del_session_value('session_'+idp_id)    
    
    
  def is_logged(self, idp_id):
    
    """
    Indique si une session est en cours avec une authentifiction par un IdP
    
    mpham 01/03/2021
    """
    
    return self.get_session_value('session_'+idp_id) is not None

    
  def check_path_traversal(base_dir, requested_path):

    """
    vérifie que le chemin demandé par le client ne fait pas de directory traversal
    retourne True si le chemin est conforme, False en cas d'attaque
    
    mpham 12/02/2021
    """
    
    return os.path.commonprefix((os.path.realpath(requested_path), base_dir)) == base_dir
    
    
  def log_info(self, message, level=0):
    for line in message.splitlines():
      print('INF '+('  ' * level)+line)
    return message

    
  def log_error(self, message, level=0):
    for line in message.splitlines():
      print('ERR '+('  ' * level)+line)
    return message


class BaseHandler:
  
  def __init__(self, hreq):
    
    """
    hreq est l'instance courante de HTTPRequestHandler
    
    mpham 01/03/2021
    """
    
    from server import Server  # pour éviter les imports circulaires
    self.conf = Server.conf
    self.post_form = hreq.post_form
    self.hreq = hreq
    self.server = hreq.server

    self.row_number = 0  # pour l'affichage des tableaux de résultat

  
  def get_query_string_param(self, key, default=None):
    
    """
    retourne la valeur d'un paramètre de la query string
      le paramètre ne soit se retrouver qu'une fois dans la query string
      
    retourne None si le paramètre n'est pas trouvé ou s'il a plusieurs valeurs
    
    mpham 01/03/2021
    """

    value = default
    
    url_params = self.parse_query_string()

    if key in url_params:
      values = url_params[key]
      if len(values) == 1:
        value = values[0]
    
    return value
    
  
  def parse_query_string(self):
  
    url_items = urllib.parse.urlparse(self.hreq.path)
    return urllib.parse.parse_qs(url_items.query)
  
    
  def add_content(self, content):
    self.hreq.add_content(content)
    
  
  def send_page(self, content = ''):
    self.hreq.send_page(content)


  def send_page_top(self, code = 200, template=True, send_cookie=True):
    self.hreq.send_page_top(code, template, send_cookie)


  def send_page_bottom(self):
    self.hreq.send_page_bottom()


  def send_template(self, template_name:str, **parameters):
    self.hreq.send_template(template_name, **parameters)
    
  
  def send_redirection(self, url):
    self.hreq.send_redirection(url)
    
    
  def send_json(self, url):
    self.hreq.send_json(url)
    
    
  def set_session_value(self, key, value):
    self.hreq.set_session_value(key, value)
    
    
  def get_session_value(self, key):
    return self.hreq.get_session_value(key)

    
  def del_session_value(self, key):
    self.hreq.del_session_value(key)


  def logon(self, idp_id, id_token = 'authenticated'):
    self.hreq.logon(idp_id, id_token)


  def logoff(self, idp_id):
    self.hreq.logoff(idp_id)


  def is_logged(self, idp_id):
    return self.hreq.is_logged(idp_id)


  def log_info(self, message, level=0):
    return self.hreq.log_info(message, level)

    
  def log_error(self, message, level=0):
    return self.hreq.log_error(message, level)


  def start_result_table(self):
    self.add_content('<table class="fixed">')
  

  def row_label(self, label : str, help_id : str) -> str:
    
    """ Formate le titre d'une ligne avec une icône d'aide à droite
    
    :param str name: libellé de la ligne
    :param str help_id: identifiant relatif de la rubrique d'aide (l'identifiant est préfixé par la fonction Javascript help() locale)
    :return: code HTML à insérer dans le <td>
    :rtype: str
    
    .. note::
      mpham 22/04/2021
    """
    
    return '<span class="celltxt">{label}</span><span class="cellimg"><img onclick="help(this, \'{help_id}\')" src="/images/help.png"></span>'.format(label=html.escape(label), help_id=help_id)
    

  def add_result_row(self, title : str, value : str, help_id : str = None) -> str:
    
    """
    Ajoute une ligne à un tableau de retour d'authentification
    Tronque la valeur si elle est trop longue (avec bouton d'affichage complet)
    Possibilité de copie de la valeur
    
    mpham 25/02/2021
    
    """

    self.row_number = self.row_number + 1
    col_id = 'col' + str(self.row_number)
    if help_id is None:
      row_label = html.escape(title)
    else:
      row_label = '<span class="celltxt">{label}</span><span class="cellimg"><img onclick="help(this, \'{help_id}\')" src="/images/help.png"></span>'.format(label=html.escape(title), help_id=help_id)
    self.add_content('<tr><td>'+row_label+'</td>')
    
    if len(value) <= 80:
      # la valeur tient sur une ligne
      html_value = html.escape(value).replace('\n', '<br>').replace(' ', '&nbsp;')
      self.add_content('<td><span id="'+col_id+'"><span id="'+col_id+'c">'+html_value+'</span>')
      self.add_content('<span> </span><img title="Copy value" class="smallButton" src="/images/copy.png" onClick="copyValue(\''+col_id+'\')"/></span></td></tr>')
    else:
      # la valeur doit être tronquée
      truncated_value = value[0:80]
      html_value = html.escape(value).replace('\n', '<br>').replace(' ', '&nbsp;')
      self.add_content('<td><span id="'+col_id+'s">'+html.escape(truncated_value)+'...')
      self.add_content('&nbsp;<img title="Expand" class="smallButton" src="/images/plus.png" onClick="showLong(\''+col_id+'\')"/>')
      self.add_content('<span> </span><img title="Copy value" class="smallButton" src="/images/copy.png" onClick="copyValue(\''+col_id+'\')"/></span>')
      self.add_content('<span id="'+col_id+'l" style="display: none;"><span id="'+col_id+'c">'+html_value+'</span>')
      self.add_content('&nbsp;<img title="Collapse" class="smallButton" src="/images/moins.png" onClick="showShort(\''+col_id+'\')"/>')
      self.add_content('<span> </span><img title="Copy value" class="smallButton" src="/images/copy.png" onClick="copyValue(\''+col_id+'\')"/></span></td></tr>')
    

  def end_result_table(self):
    self.add_content('</table>')

    
class AduneoError(Exception):
  pass
