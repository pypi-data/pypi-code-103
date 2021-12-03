from .BaseServer import AduneoError
from .BaseServer import BaseHandler
from .Configuration import Configuration
from .Help import Help
import base64
import datetime
import html
import json
import jwcrypto.jwt
import requests
import traceback
import uuid

"""
  TODO : si signature HMAC (HS256 dans l'alg de l'en-tête de l'ID Token), il faut utiliser le secret (encodé en UTF-8 puis en base 64) comme clé
         voir le code France Connect
"""


class OIDCClientLogin(BaseHandler):
 
  def prepare_request(self):

    """
      Prépare la requête d'authentification OIDC
      
      mpham 26/02/2021 - 05/03/2021
    """

    rp_id = self.get_query_string_param('id')
    state = self.get_query_string_param('state')
    
    if rp_id is not None:

      if rp_id not in self.conf['oidc_clients']:
        self.send_redirection('/')

      rp = self.conf['oidc_clients'][rp_id]

      if rp.get('endpoint_configuration', 'Local configuration').casefold() == 'discovery uri':
        self.add_content('<span id="meta_data_ph">Retrieving metadata from<br>'+rp['discovery_uri']+'<br>...</span>')
        try:
          self.log_info('Starting metadata retrieval')
          self.log_info('discovery_uri: '+rp['discovery_uri'], 1)
          r = requests.get(rp['discovery_uri'], verify=False)
          self.log_info(r.text, 1)
          meta_data = r.json()
          self.add_content('<script>document.getElementById("meta_data_ph").style.display = "none"</script>')
          meta_data['signature_key'] = rp.get('signature_key', '')
        except Exception as error:
          self.log_error(traceback.format_exc(), 1)
          self.add_content('failed<br>'+str(error))
          self.send_page()
          return
        if r.status_code != 200:
          self.log_error('Server responded with code '+str(r.status_code), 1)
          self.add_content('failed<br>Server responded with code '+str(r.status_code))
          self.send_page()
          return
      else:
        meta_data = {}
        meta_data = dict((k, rp[k]) for k in ['issuer', 'authorization_endpoint', 'token_endpoint', 'jwks_uri', 'userinfo_endpoint', 'signature_key'] if k in rp)
      
    elif state is not None:
        
      rp = self.get_session_value(state)
      if (rp is None):
        self.send_redirection('/')
      rp_id = rp['rp_id']
      #self.del_session_value(state)   TODO
      
      conf_rp = self.conf['oidc_clients'][rp_id]
      rp['name'] = conf_rp['name']
      meta_data = rp['meta_data']
        
    else:
      self.send_redirection('/')
    
    self.add_content("<h1>OIDC Client: "+rp["name"]+"</h1>")
    
    if 'redirect_uri' in rp:
      redirect_uri = rp['redirect_uri']
    else:
      redirect_uri = 'http'
      if Configuration.is_on(self.conf['server']['ssl']):
        redirect_uri = redirect_uri + 's'
      redirect_uri = redirect_uri + '://' + self.conf['server']['host']
      if (Configuration.is_on(self.conf['server']['ssl']) and self.conf['server']['port'] != '443') or (Configuration.is_off(self.conf['server']['ssl']) and self.conf['server']['port'] != '80'):
        redirect_uri = redirect_uri + ':' + self.conf['server']['port']
      redirect_uri = redirect_uri + '/oidc/client/callback'

    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    
    self.add_content('<form name="request" action="/oidc/client/sendrequest" method="post">')
    self.add_content('<input name="rp_id" value="'+html.escape(rp_id)+'" type="hidden" />')
    self.add_content('<table class="fixed">')
    self.add_content('<tr><td>'+self.row_label('Authorization Endpoint', 'authorization_endpoint')+'</td><td><input name="authorization_endpoint" value="'+html.escape(meta_data['authorization_endpoint'])+'"class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Token endpoint', 'token_endpoint')+'</td><td><input name="token_endpoint" value="'+html.escape(meta_data['token_endpoint'])+'"class="intable" type="text"></td></tr>')

    # configuration de la clé de vérification de signature
    self.add_content('<tr id="signature_key_configuration"><td>'+self.row_label('Signature key configuration', 'signature_key_configuration')+'</td><td><select name="signature_key_configuration" class="intable" onchange="changeSignatureKeyConfiguration()">')
    for value in ('JWKS URI', 'Local configuration'):
      selected = ''
      if value.casefold() == rp.get('signature_key_configuration', 'JWKS URI').casefold():
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</td></tr>')
    
    # clé de signature récupérée par JWKS
    key_visible = (rp.get('signature_key_configuration', 'JWKS URI').casefold() == 'jwks uri')
    key_visible_style = 'none'
    if key_visible:
      key_visible_style = 'table-row'
    self.add_content('<tr id="jwks_uri" style="display: '+key_visible_style+';"><td>'+self.row_label('JWKS URI', 'jwks_uri')+'</td><td><input name="jwks_uri" value="'+html.escape(meta_data.get('jwks_uri', ''))+'" class="intable" type="text"></td></tr>')
    
    # clé de signature dans le fichier local
    key_visible = (rp.get('signature_key_configuration', 'JWKS URI').casefold() == 'local configuration')
    key_visible_style = 'none'
    if key_visible:
      key_visible_style = 'table-row'
    self.add_content('<tr id="signature_key" style="display: '+key_visible_style+';"><td>'+self.row_label('Signature key', 'signature_key')+'</td><td><input name="signature_key" value="'+html.escape(meta_data.get('signature_key', ''))+'" class="intable" type="text"></td></tr>')
    
    self.add_content('<tr><td>'+self.row_label('UserInfo endpoint', 'userinfo_endpoint')+'</td><td><input name="userinfo_endpoint" value="'+html.escape(meta_data.get('userinfo_endpoint', ''))+'"class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Issuer', 'issuer')+'</td><td><input name="issuer" value="'+html.escape(meta_data['issuer'])+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Scope', 'scope')+'</td><td><input name="scope" value="'+html.escape(rp['scope'])+'" class="intable" type="text"></td></tr>')
    
    self.add_content('<tr><td>'+self.row_label('Reponse type', 'response_type')+'</td><td><select name="response_type" class="intable">')
    for value in ['code']:
      selected = ''
      if value == rp.get('response_type', ''):
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select></td></tr>')
    
    self.add_content('<tr><td>'+self.row_label('Client ID', 'client_id')+'</td><td><input name="client_id" value="'+html.escape(rp['client_id'])+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Client secret', 'client_secret')+'</td><td><input name="client_secret!" class="intable" type="password"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Redirect URI', 'redirect_uri')+'</td><td><input name="redirect_uri" value="'+html.escape(redirect_uri)+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('State', 'state')+'</td><td>'+html.escape(state)+'</td></tr>')
    self.add_content('<tr><td>'+self.row_label('Nonce', 'nonce')+'</td><td><input name="nonce" value="'+html.escape(nonce)+'" class="intable" type="text"></td></tr>')

    self.add_content('<tr><td>'+self.row_label('Display', 'display')+'</td><td><select name="display" class="intable">')
    for value in ('', 'page', 'popup', 'touch', 'wap'):
      selected = ''
      if value == rp.get('display', ''):
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select></td></tr>')

    self.add_content('<tr><td>'+self.row_label('Prompt', 'prompt')+'</td><td><select name="prompt" class="intable">')
    for value in ('', 'none', 'login', 'consent', 'select_account'):
      selected = ''
      if value == rp.get('prompt', ''):
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select></td></tr>')

    self.add_content('<tr><td>'+self.row_label('Max age', 'max_age')+'</td><td><input name="max_age" value="'+html.escape(rp.get('max_age', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('UI locales', 'ui_locales')+'</td><td><input name="ui_locales" value="'+html.escape(rp.get('ui_locales', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('ID token hint', 'id_token_hint')+'</td><td><input name="id_token_hint" value="'+html.escape(rp.get('id_token_hint', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Login hint', 'login_hint')+'</td><td><input name="login_hint" value="'+html.escape(rp.get('login_hint', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('ACR values', 'acr_values')+'</td><td><input name="acr_values" value="'+html.escape(rp.get('acr_values', ''))+'" class="intable" type="text"></td></tr>')
    
    checked = ''
    if Configuration.is_on(rp.get('fetch_userinfo', 'off')):
      checked = ' checked'
    self.add_content('<tr><td>'+self.row_label('Fetch UserInfo', 'fetch_userinfo')+'</td><td><input name="fetch_userinfo" type="checkbox"'+checked+'></td></tr>')
    
    self.add_content('</table>')
    
    self.add_content('<div style="padding-top: 20px; padding-bottom: 12px;"><div style="padding-bottom: 6px;"><strong>Authentication request</strong> <img title="Copy request" class="smallButton" src="/images/copy.png" onClick="copyRequest()"/></div>')
    self.add_content('<span id="auth_request" style="font-size: 14px;"></span></div>')
    self.add_content('<input name="authentication_request" type="hidden">')
    self.add_content('<input name="state" value="'+html.escape(state)+'" type="hidden">')
    
    self.add_content('<button type="submit" class="button">Send to IdP</button>')
    self.add_content('</form>')

    self.add_content("""
    <script>
    function updateAuthRequest() {
      var request = document.request.authorization_endpoint.value
        + '?scope='+encodeURIComponent(document.request.scope.value);
      ['response_type', 'client_id', 'redirect_uri', 'state'].forEach(function(item, index) {
        request += '&'+item+'='+encodeURIComponent(document.request[item].value)
      });
      ['nonce', 'display', 'prompt', 'max_age', 'ui_locales', 'id_token_hint', 'login_hint', 'acr_values'].forEach(function(item, index) {
        if (document.request[item].value != '') { request += '&'+item+'='+encodeURIComponent(document.request[item].value); }
      });
      
      document.getElementById('auth_request').innerHTML = request;
      document.request.authentication_request.value = request;
    }
    var input = document.request.getElementsByTagName('input');
    Array.prototype.slice.call(input).forEach(function(item, index) {
      if (item.type == 'text') { item.addEventListener("input", updateAuthRequest); }
    });
    var select = document.request.getElementsByTagName('select');
    Array.prototype.slice.call(select).forEach(function(item, index) {
      if (item.name != 'signature_key_configuration') {
        item.addEventListener("change", updateAuthRequest);
      }
    });
    updateAuthRequest();

    function copyRequest() {
      copyTextToClipboard(document.request.authentication_request.value);
    }
    function copyTextToClipboard(text) {
      var tempArea = document.createElement('textarea')
      tempArea.value = text
      document.body.appendChild(tempArea)
      tempArea.select()
      tempArea.setSelectionRange(0, 99999)
      document.execCommand("copy")
      document.body.removeChild(tempArea)
    }
    
    function changeSignatureKeyConfiguration() {
      if (document.request.signature_key_configuration.value == 'JWKS URI') {
        document.getElementById('jwks_uri').style.display = 'table-row';
        document.getElementById('signature_key').style.display = 'none';
      } else {
        document.getElementById('jwks_uri').style.display = 'none';
        document.getElementById('signature_key').style.display = 'table-row';
      }
    }
    </script>
    """)
  
    self.add_content(Help.help_window_definition())
    
    self.send_page()


  def send_request(self):
    
    """
    Récupère les informations saisies dans /oidc/client/preparerequest pour les mettre dans la session
      (avec le state comme clé)
    Redirige vers l'IdP grâce à la requête générée dans /oidc/client/preparerequest et placée dans le paramètre authentication_request
    
    mpham 26/02/2021 - 28/02/2021
    """
    
    self.log_info('Redirection to IdP requested')
    state = self.post_form['state']
    
    meta_data = {}
    for item in ['authorization_endpoint', 'token_endpoint', 'userinfo_endpoint', 'jwks_uri', 'issuer', 'signature_key']:
      if self.post_form[item] != '':
        meta_data[item] = self.post_form[item]
    
    request = {}
    request['meta_data'] = meta_data
    
    for item in ['rp_id', 'state', 'scope', 'response_type', 'client_id', 'client_secret!', 'redirect_uri', 'state', 'nonce', 'display', 'prompt', 'max_age', 'ui_locales', 'id_token_hint', 'login_hint', 'acr_values', 'signature_key_configuration', ]:
      if self.post_form[item] != '':
        request[item] = self.post_form[item]
    
    if 'fetch_userinfo' in self.post_form:
      request['fetch_userinfo'] = 'on'
    else:
      request['fetch_userinfo'] = 'off'
    
    self.set_session_value(state, request)
    
    authentication_request = self.post_form['authentication_request']
    self.log_info('Redirecting to:', 1)
    self.log_info(authentication_request, 1)
    self.send_redirection(authentication_request)


  def callback(self):

    """
    Retour d'authentification :
    - récupère les jeton auprès de l'IdP
    - valide les jetons
    - récupère (si demandé) les informations auprès de userinfo
    
    mpham 26/02/2021 - 28/02/2021
    """
    
    self.send_page_top(200)
    self.add_content("""<script src="/javascript/resultTable.js"></script>""")

    self.log_info('Authentication callback')
    self.add_content('<h2>Authentication callback</h2>')
    
    auth_result = False
    try:
      self.check_authentication()
      self.add_content('<h3>Authentication succcessful</h3>')
      auth_result = True
    except AduneoError as error:
      self.add_content('<h3>Authentication failed : '+html.escape(str(error))+'</h3>')
    except Exception as error:
      self.log_error(traceback.format_exc(), 1)
      self.add_content('<h3>Authentication failed : '+html.escape(str(error))+'</h3>')
    
    state = self.get_query_string_param('state')
    request = self.get_session_value(state)
    fetch_userinfo = request.get('fetch_userinfo', 'off')
    
    if auth_result and Configuration.is_on(fetch_userinfo):
      try:
        self.get_userinfo()
        self.add_content('<h3>Userinfo succcessful</h3>')
      except AduneoError as error:
        self.add_content('<h3>Userinfo failed : '+html.escape(str(error))+'</h3>')
      except Exception as error:
        self.log_error(traceback.format_exc(), 1)
        self.add_content('<h3>Userinfo failed : '+html.escape(str(error))+'</h3>')

    self.add_content('<form action="/oidc/client/preparerequest" method="get">')
    self.add_content("""<input type="hidden" name="state" value="""+'"'+html.escape(state)+'" />')
    self.add_content("""<button type="submit" class="button">Retry</button>""")
    self.add_content("""</form>""")
    
    self.send_page_bottom()


  def check_authentication(self):
    
    """
    Vérifie la bonne authentification :
    - récupère les jeton auprès de l'IdP
    - valide les jetons
    
    mpham 26/02/2021 - 28/02/2021
    """
    
    self.add_content(Help.help_window_definition())
    self.start_result_table()
    
    try:
    
      self.log_info('Checking authentication')
      
      error = self.get_query_string_param('error')
      if error is not None:
        description = ''
        error_description = self.get_query_string_param('error_description')
        if error_description is not None:
          description = ', '+error_description
        raise AduneoError(self.log_error('IdP returned an error: '+error+description))

      # récupération de state pour obtention des paramètres dans la session
      idp_state = self.get_query_string_param('state')
      self.log_info('for state: '+idp_state, 1)
      self.add_result_row('State returned by IdP', idp_state, 'idp_state')
      request = self.get_session_value(idp_state)
      if (request is None):
        raise AduneoError(self.log_error('state not found in session'))

      # extraction des informations utiles de la session
      rp_id = request['rp_id']
      meta_data = request['meta_data']
      token_endpoint = meta_data['token_endpoint']
      client_id = request['client_id']
      redirect_uri = request['redirect_uri']
      
      if 'client_secret!' in request:
        client_secret = request['client_secret!']
      else:
        # il faut aller chercher le mot de passe dans la configuration
        rp = self.conf['oidc_clients'][rp_id]
        client_secret = rp['client_secret!']

      # Vérification de state (plus besoin puisqu'on utilise le state pour récupérer les informations dans la session)
      #session_state = request['state']
      #idp_state = url_params['state'][0]
      #if session_state != idp_state:
      #   print('ERROR')
      
      grant_type = "authorization_code";
      code = self.get_query_string_param('code')
      self.add_result_row('Code returned by IdP', code, 'idp_code')
      self.add_result_row('Token endpoint', token_endpoint, 'token_endpoint')
      self.add_content('<tr><td>Retrieving tokens...</td>')
      self.log_info("Starting token retrieval", 1)
      try:
        self.log_info("Connecting to "+token_endpoint, 1)
        # Remarque : ici on est en authentification client_secret_post alors que la méthode par défaut, c'est client_secret_basic (https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication)
        r = requests.post(token_endpoint, data = {'grant_type':grant_type,
            'code':code, 'redirect_uri':redirect_uri, 'client_id':client_id, 'client_secret':client_secret}, verify=False)
      except Exception as error:
        self.add_content('<td>Error : '+str(error)+'</td></tr>')
        raise AduneoError(self.log_error('token retrieval error: '+str(error), 1))
      if r.status_code == 200:
        self.add_content('<td>OK</td></tr>')
      else:
        self.add_content('<td>Error, status code '+str(r.status_code)+'</td></tr>')
        raise AduneoError(self.log_error('token retrieval error: status code '+str(r.status_code)))

      response = r.json()
      self.log_info("IdP response:", 1)
      self.log_info(json.dumps(response, indent=2), 2)
      id_token = response['id_token']
      self.add_result_row('JWT ID Token', id_token, 'jwt_id_token')
      
      self.log_info("Decoding ID token", 1)
      token_items = id_token.split('.')
      encoded_token_header = token_items[0]
      token_header_string = base64.urlsafe_b64decode(encoded_token_header + '=' * (4 - len(encoded_token_header) % 4))
      encoded_token_payload = token_items[1]
      token_payload = base64.urlsafe_b64decode(encoded_token_payload + '=' * (4 - len(encoded_token_payload) % 4))

      token_header = json.loads(token_header_string)
      self.add_result_row('ID Token header', json.dumps(token_header, indent=2), 'id_token_header')
      self.log_info("ID token header:", 1)
      self.log_info(json.dumps(token_header, indent=2), 1)

      json_token = json.loads(token_payload)
      self.add_result_row('ID Token claims set', json.dumps(json_token, indent=2), 'id_token_claims_set')
      self.add_result_row('ID Token sub', json_token['sub'], 'id_token_sub')
      self.log_info("ID token payload:", 1)
      self.log_info(json.dumps(json_token, indent=2), 1)

      # Vérification de nonce
      session_nonce = request['nonce']
      idp_nonce = json_token['nonce']
      if session_nonce == idp_nonce:
        self.log_info("Nonce verification OK: "+session_nonce, 1)
        self.add_result_row('Nonce verification', 'OK: '+session_nonce, 'nonce_verification')
      else:
        self.log_error("Nonce verification failed", 1)
        self.log_error("client nonce: "+session_nonce, 2)
        self.log_error("IdP nonce   :"+idp_nonce, 2)
        self.add_result_row('Nonce verification', "Failed\n  client nonce: "+session_nonce+"\n  IdP nonce: "+idp_nonce, 'nonce_verification')
        raise AduneoError('nonce verification failed')

      # Vérification de validité du jeton
      self.log_info("Starting token validation", 1)
      
      # On vérifie que le jeton est toujours valide (la date est au format Unix)
      tokenExpiryTimestamp = json_token['exp']
      tokenExpiryTime = datetime.datetime.utcfromtimestamp(tokenExpiryTimestamp)
      if tokenExpiryTime >= datetime.datetime.utcnow():
        self.log_info("Token expiration verification OK:", 1)
        self.log_info("Token expiration: "+str(tokenExpiryTime)+' UTC', 2)
        self.log_info("Now             : "+str(datetime.datetime.utcnow())+' UTC', 2)
        self.add_result_row('Expiration verification', 'OK:'+str(tokenExpiryTime)+' UTC (now is '+str(datetime.datetime.utcnow())+' UTC)', 'expiration_verification')
      else:
        self.log_error("Token expiration verification failed:", 1)
        self.log_error("Token expiration: "+str(tokenExpiryTime)+' UTC', 2)
        self.log_error("Now             : "+str(datetime.datetime.utcnow())+' UTC', 2)
        self.add_result_row('Expiration verification', 'Failed:'+str(tokenExpiryTime)+' UTC (now is '+str(datetime.datetime.utcnow())+' UTC)', 'expiration_verification')
        raise AduneoError('token expiration verification failed')
      
      # On vérifie l'origine du jeton 
      token_issuer = json_token['iss']
      if token_issuer == meta_data['issuer']:
        self.log_info("Token issuer verification OK: "+token_issuer, 1)
        self.add_result_row('Issuer verification', 'OK: '+token_issuer, 'issuer_verification')
      else:
        self.log_error("Expiration verification failed:", 1)
        self.log_error("Token issuer   : "+token_issuer, 2)
        self.log_error("Metadata issuer: "+meta_data['issuer'], 2)
        self.add_result_row('Issuer verification', "Failed\n  token issuer: "+token_issuer+"\n  metadata issuer:"+meta_data['issuer'], 'issuer_verification')
        raise AduneoError('token issuer verification failed')
      
      # On vérifie l'audience du jeton, qui doit être le client ID
      token_audience = json_token['aud']
      if token_audience == client_id:
        self.log_info("Token audience verification OK: "+token_audience, 1)
        self.add_result_row('Audience verification', 'OK: '+token_audience, 'audience_verification')
      else:
        self.log_error("Audience verification failed:", 1)
        self.log_error("Token audience: "+token_audience, 2)
        self.log_error("ClientID      : "+client_id, 2)
        self.add_result_row('Audience verification', 'Failed ('+client_id+' != '+token_audience, 'audience_verification')
        raise AduneoError('token audience verification failed')
      
      # Vérification de signature, on commence par regarde l'algorithme
      token_key = None
      alg = token_header.get('alg')
      self.log_info('Signature verification', 1)
      self.log_info('Signature algorithm in token header : '+alg, 2)
      if alg == 'HS256':
        # Signature symétrique HMAC 256
        self.log_info('HS256 signature, the secret is client_secret', 2)
        print(client_secret)
        encoded_secret = base64.urlsafe_b64encode(str.encode(client_secret)).decode()
        key = {"alg":"HS265","kty":"oct","use":"sig","kid":"1","k":encoded_secret}
        print(key)
        token_key = jwcrypto.jwk.JWK(**key)

      elif alg == 'RS256':
        # Signature asymétrique RSA 256
        self.log_info('RS256 signature, fetching public key', 2)
      
        # On regarde si on doit aller chercher les clés avec l'endpoint JWKS ou si la clé a été donnée localement
        if request['signature_key_configuration'] == 'Local configuration':
          self.log_info('Signature JWK:', 2)
          self.log_info(meta_data['signature_key'], 3)
          token_jwk = json.loads(meta_data['signature_key'])
        else:
        
          # On extrait l'identifiant de la clé depuis l'id token
          idp_kid = token_header['kid']
          self.log_info('Signature key kid: '+idp_kid)
          self.add_result_row('Signature key kid', idp_kid, 'signature_key_kid')
          
          # on va chercher la liste des clés
          self.log_info("Starting IdP keys retrieval", 2)
          self.add_result_row('JWKS endpoint', meta_data['jwks_uri'], 'jwks_endpoint')
          self.add_content('<tr><td>Retrieving keys...</td>')
          try:
            r = requests.get(meta_data['jwks_uri'], verify=False)
          except Exception as error:
            self.add_content('<td>Error : '+str(error)+'</td></tr>')
            raise AduneoError(self.log_error('IdP keys retrieval error: '+str(error), 2))
          if r.status_code == 200:
            self.add_content('<td>OK</td></tr>')
          else:
            self.add_content('<td>Error, status code '+str(r.status_code)+'</td></tr>')
            raise AduneoError(self.log_error('IdP keys retrieval error: status code '+str(r.status_code)))

          keyset = r.json()
          self.log_info("IdP response:", 1)
          self.log_info(json.dumps(keyset, indent=2), 3)
          self.add_result_row('Keyset', json.dumps(keyset, indent=2), 'keyset')
          
          # On en extrait la JWK qui correspond au token
          self.add_result_row('Retrieved keys', '', 'retrieved_keys')
          token_jwk = None
          for jwk in keyset['keys']:
              self.add_result_row(jwk['kid'], json.dumps(jwk, indent=2))
              if jwk['kid'] == idp_kid:
                token_jwk = jwk
                
          self.log_info('Signature JWK:', 1)
          self.log_info(json.dumps(token_jwk, indent=2), 3)
          
        self.add_result_row('Signature JWK', json.dumps(token_jwk, indent=2), 'signature_jwk')
        token_key = jwcrypto.jwk.JWK(**token_jwk)

      elif alg is None:
        raise AduneoError('Signature algorithm not found in header '+json.dumps(token_header))
      else:
        raise AduneoError('Signature algorithm '+alg+' not supported')

      # On vérifie la signature
      try:
        jwcrypto.jwt.JWT(key=token_key, jwt=id_token)
        self.log_info('Signature verification OK', 1)
        self.add_content('<tr><td>Signature verification</td><td>OK</td></tr>')
      except Exception as error:

        default_case = True
        # Si on est en HS256, peut-être que le serveur a utilisé une clé autre que celle du client_secret (cas Keycloak)
        if alg == 'HS256':
          if request['signature_key_configuration'] != 'Local configuration':
            self.log_info('HS256 signature, client_secret not working. The server might have used another key. Put this key in configuration', 2)
          else:
            default_case = False
            self.log_info('HS256 signature, client_secret not working, trying key from configuration', 2)
            
            configuration_key = meta_data['signature_key']
            self.log_info('Configuration key:', 2)
            self.log_info(configuration_key, 3)
            json_key = json.loads(configuration_key)
          
            token_key = jwcrypto.jwk.JWK(**json_key)
          
            try:
              jwcrypto.jwt.JWT(key=token_key, jwt=id_token)
              self.log_info('Signature verification OK', 1)
              self.add_content('<tr><td>Signature verification</td><td>OK</td></tr>')
            except Exception as error:
              default_case = True
          
        if default_case:
          # Cas normal de la signature non vérifiée
          self.add_content('<tr><td>Signature verification</td><td>Failed</td></tr>')
          raise AduneoError(self.log_error('Signature verification failed'))
      
      # On conserve l'access token pour userinfo
      self.log_info('Access token:', 1)
      self.log_info(response['access_token'], 2)
      self.access_token = response['access_token']

      # on considère qu'on est bien loggé
      self.logon('oidc_client_'+rp_id, id_token)

      
    finally:
      self.end_result_table()


  def get_userinfo(self):

    self.log_info('Getting userinfo')
    self.start_result_table()

    try:

      # récupération de state pour obtention des paramètres dans la session
      idp_state = self.get_query_string_param('state')
      self.log_info('for state: '+idp_state, 1)
      self.add_result_row('State returned by IdP', idp_state, 'idp_state')
      request = self.get_session_value(idp_state)
      if (request is None):
        raise AduneoError(self.log_error('state not found in session'))

      # extraction des informations utiles de la session
      meta_data = request['meta_data']
      token_endpoint = meta_data['token_endpoint']
      client_id = request['client_id']
      redirect_uri = request['redirect_uri']

      # récupération UserInfo
      userinfo_endpoint = meta_data['userinfo_endpoint']
      self.log_info('Userinfo endpoint: '+userinfo_endpoint, 1)
      self.add_result_row('Userinfo endpoint', userinfo_endpoint, 'userinfo_endpoint')
      self.add_result_row('Access token', self.access_token, 'access_token')
      
      # Décodage de l'AT si c'est un JWT (pour l'instant la vérification que c'est un JWT est sommaire et devra être affinée
      if self.access_token.startswith('eyJh'):
        self.log_info("Access token is a JWT", 1)
        at_items = self.access_token.split('.')
        encoded_at_header = at_items[0]
        at_header_string = base64.urlsafe_b64decode(encoded_at_header + '=' * (4 - len(encoded_at_header) % 4))
        encoded_at_payload = at_items[1]
        at_payload = base64.urlsafe_b64decode(encoded_at_payload + '=' * (4 - len(encoded_at_payload) % 4))

        at_header = json.loads(at_header_string)
        self.add_result_row('Access token header', json.dumps(at_header, indent=2), 'at_header')
        self.log_info("Access token header:", 1)
        self.log_info(json.dumps(at_header, indent=2), 1)

        at_claims = json.loads(at_payload)
        self.add_result_row('Access token claims set', json.dumps(at_claims, indent=2), 'at_claims_set')
        self.log_info("Access token payload:", 1)
        self.log_info(json.dumps(at_claims, indent=2), 1)
      
      self.log_info('Starting userinfo retrieval', 1)
      self.add_content('<tr><td>Retrieving user info...</td>')
      try:
        r = requests.get(userinfo_endpoint, headers = {'Authorization':"Bearer "+self.access_token}, verify=False)
      except Exception as error:
        self.add_content('<td>Error : '+str(error)+'</td></tr>')
        raise AduneoError(self.log_error('userinfo retrieval error: '+str(error), 1))
      if r.status_code == 200:
        self.add_content('<td>OK</td></tr>')
      else:
        self.add_content('<td>Error, status code '+str(r.status_code)+'</td></tr>')
        raise AduneoError(self.log_error('userinfo retrieval error: status code '+str(r.status_code)))
      
      response = r.json()
      self.log_info('User info:', 1)
      self.log_info(json.dumps(response, indent=2), 2)
      self.add_result_row('User info', json.dumps(response, indent=2), 'user_info')
      
    finally: 
      self.end_result_table()


