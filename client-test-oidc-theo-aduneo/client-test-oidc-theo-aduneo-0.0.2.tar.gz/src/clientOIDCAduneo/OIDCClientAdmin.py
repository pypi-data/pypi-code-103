from .BaseServer import AduneoError
from .BaseServer import BaseHandler
from .Configuration import Configuration
from .Help import Help
import html

"""
  TODO : je crois qu'on ne peut pas donner la clé publique (drop down list qui ne fonctionne pas)
"""

class OIDCClientAdmin(BaseHandler):
  
  def display(self):
    
    """
    Ajout/modification d'un client OIDC
    
    mpham 12/02/2021 - 27/02/2021 - 28/12/2021 - 13/04/2021
    """
    
    rp = {}
    rp_id = self.get_query_string_param('id', '')
    if rp_id != '':
      rp = self.conf['oidc_clients'][rp_id]
    
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
    
    self.add_content('<form name="rp" action="/oidc/client/modifyclient" method="post">')
    self.add_content('<input name="rp_id" value="'+html.escape(rp_id)+'" type="hidden" />')
    self.add_content('<h1>Préférences</h1>')
    self.add_content('<table id="unTab" class="fixed">')
    self.add_content('<tr><td><span class="celltxt">Name</span><span class="cellimg"><img onclick="help(this, \'name\')" src="/images/help.png"></span></td><td><input name="name" value="'+html.escape(rp.get('name', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td><span class="celltxt">Redirect URI</span><span class="cellimg"><img onclick="help(this, \'redirect_uri\')" src="/images/help.png"></span></td><td><input name="redirect_uri" value="'+html.escape(redirect_uri)+'" class="intable" type="text"></td></tr>')
    
    # méthode de configuration des endpoint
    self.add_content('<tr><td>'+self.row_label('Endpoint configuration', 'endpoint_configuration')+'</td><td><select name="endpoint_configuration" class="intable" onchange="changeEndpointConfiguration()">')
    for value in ('Discovery URI', 'Local configuration'):
      selected = ''
      if value.casefold() == rp.get('endpoint_configuration', 'Discovery URI').casefold():
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</td></tr>')

    self.add_content('</table>')
    self.add_content('<p id="un" class="fixed etapes" hidden> Ces champs sont arbitraire, mettez le nom que vous souhaitez ainsi que la méthode qui vous semble la plus pratique pour récupérez les informations du fournisseur d\'identité. <button class="button" type="button" style="padding: 5px 10px !important;" onclick="showHelp(\'deux\');">Continuer</button></p>')
    self.add_content('<h1>Information de l\'IdP</h1>')
    self.add_content('<table id="deuxTab" class="fixed">')

    # configuration des endpoint par discovery uri
    visible = (rp.get('endpoint_configuration', 'Discovery URI').casefold() == 'discovery uri')
    visible_style = 'none'
    if visible:
      visible_style = 'table-row'
    self.add_content('<tr id="discovery_uri" style="display: '+visible_style+';"><td>'+self.row_label('Discovery URI', 'discovery_uri')+'</td><td><input name="discovery_uri" value="'+rp.get('discovery_uri', '')+'" class="intable" type="text"></td></tr>')
    
    # configuration des endpoint dans le fichier local
    visible = (rp.get('endpoint_configuration', 'Discovery URI').casefold() == 'local configuration')
    visible_style = 'none'
    if visible:
      visible_style = 'table-row'
    self.add_content('<tr id="issuer" style="display: '+visible_style+';"><td>'+self.row_label('Issuer', 'issuer')+'</td><td><input name="issuer" value="'+html.escape(rp.get('issuer', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr id="authorization_endpoint" style="display: '+visible_style+';"><td>'+self.row_label('Authorization endpoint', 'authorization_endpoint')+'</td><td><input name="authorization_endpoint" value="'+html.escape(rp.get('authorization_endpoint', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr id="token_endpoint" style="display: '+visible_style+';"><td>'+self.row_label('Token endpoint', 'token_endpoint')+'</td><td><input name="token_endpoint" value="'+html.escape(rp.get('token_endpoint', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr id="end_session_endpoint" style="display: '+visible_style+';"><td>'+self.row_label('Logout endpoint', 'end_session_endpoint')+'</td><td><input name="end_session_endpoint" value="'+html.escape(rp.get('end_session_endpoint', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr id="userinfo_endpoint" style="display: '+visible_style+';"><td>'+self.row_label('Userinfo endpoint', 'userinfo_endpoint')+'</td><td><input name="userinfo_endpoint" value="'+html.escape(rp.get('userinfo_endpoint', ''))+'" class="intable" type="text"></td></tr>')

    # configuration de la clé de vérification de signature
    self.add_content('<tr id="signature_key_configuration" style="display: '+visible_style+';"><td>'+self.row_label('Signature key configuration', 'signature_key_configuration')+'</td><td><select name="signature_key_configuration" class="intable" onchange="changeEndpointConfiguration()">')
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
    if not visible:
      key_visible_style = 'none'
    self.add_content('<tr id="jwks_uri" style="display: '+key_visible_style+';"><td>'+self.row_label('JWKS URI', 'jwks_uri')+'</td><td><input name="jwks_uri" value="'+html.escape(rp.get('jwks_uri', ''))+'" class="intable" type="text"></td></tr>')
    
    # clé de signature dans le fichier local
    key_visible = (rp.get('signature_key_configuration', 'JWKS URI').casefold() == 'local configuration')
    key_visible_style = 'none'
    if key_visible:
      key_visible_style = 'table-row'
    if not visible:
      key_visible_style = 'none'
    self.add_content('<tr id="signature_key" style="display: '+key_visible_style+';"><td>'+self.row_label('Signature Key', 'signature_key')+'</td><td><input name="signature_key" value="'+html.escape(rp.get('signature_key', ''))+'" class="intable" type="text"></td></tr>')
    
    # configuration de la cinématique
    self.add_content('<tr><td>'+self.row_label('Client ID', 'client_id')+'</td><td><input name="client_id" value="'+html.escape(rp.get('client_id', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Client secret', 'client_secret')+'</td><td><input name="client_secret!" value="'+html.escape(rp.get('client_secret!', ''))+'" class="intable" type="password"></td></tr>')

    self.add_content('</table>')
    self.add_content('<p id="deux" class="fixed etapes"  hidden> Il s\'agit ici des champs spécifique à votre IdP. <br>- choisissez en premier l\'url qui va permettre au client de récupérer les metadonnée de votre IdP souvent cette url est celui définit dans la RFC 5785 qui est sous la forme /.well-known/oauth-authorization-server <br>- Vous trouverez les deux dernier champs dans la page de configuration de votre application sur votre IdP. <button class="button" type="button" style="padding: 5px 10px !important;" onclick="showHelp(\'trois\');">Continuer</button></p></p>')
    self.add_content('<h1>Paramètres par défaut de la requêtes</h1>')
    self.add_content('<table id="troisTab" class="fixed">')

    self.add_content('<tr><td>'+self.row_label('Scope', 'scope')+'</td><td><input name="scope" value="'+html.escape(rp.get('scope', 'openid profile'))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>'+self.row_label('Response type', 'response_type')+'</td><td><select name="response_type" class="intable">')
    for value in ['code']:
      selected = ''
      if value == rp.get('response_type', ''):
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select></td></tr>')
    
    
    checked = ''
    if Configuration.is_on(rp.get('fetch_userinfo', 'off')):
      checked = ' checked'
    self.add_content('<tr><td>'+self.row_label('Fetch userinfo', 'fetch_userinfo')+'</td><td><input name="fetch_userinfo" type="checkbox"'+checked+'></td></tr>')
    self.add_content('</table>')
    self.add_content('<p id="trois" class="etapes fixed"  hidden> Ces champs sont les paramètres par défaut pour les champs obligatoire que vous voulez appliquer à vos requêtes. <button class="button" type="button" style="padding: 5px 10px !important;" onclick="showHelp(\'zero\');">Continuer</button></p></p>')
    self.add_content('<button type="submit" class="button">Save</button>')
    self.add_content('<button type="button" class="button" onclick="showHelp(\'un\');">Help</button>')
    self.add_content('<a href="/oidc/client/modifyclient/guide?id="'+rp_id+'"><button type="button" class="button">Guide</button></a>')

    self.add_content('</form>')

    self.add_content("""
      <script>
      function changeEndpointConfiguration() {
        if (document.rp.endpoint_configuration.value == 'Discovery URI') {
          document.getElementById('discovery_uri').style.display = 'table-row';
          ['issuer', 'authorization_endpoint', 'end_session_endpoint', 'token_endpoint', 'userinfo_endpoint', 'signature_key_configuration', 'jwks_uri', 'signature_key'].forEach(function(item, index) {
            document.getElementById(item).style.display = 'none';
          });
        } else {
          document.getElementById('discovery_uri').style.display = 'none';
          ['issuer', 'authorization_endpoint', 'token_endpoint', 'end_session_endpoint', 'userinfo_endpoint', 'signature_key_configuration'].forEach(function(item, index) {
            document.getElementById(item).style.display = 'table-row';
          });
          if (document.rp.signature_key_configuration.value == 'JWKS URI') {
            document.getElementById('jwks_uri').style.display = 'table-row';
            document.getElementById('signature_key').style.display = 'none';
          } else {
            document.getElementById('jwks_uri').style.display = 'none';
            document.getElementById('signature_key').style.display = 'table-row';
          }
        }
      }
      </script>
    """)

    self.add_content(Help.help_window_definition())
    
    self.send_page()


  def modify(self):
  
    """
    Crée ou modifie un IdP dans la configuration
    
    S'il existe, ajoute un suffixe numérique
    
    mpham 28/02/2021
    """
    
    rp_id = self.post_form['rp_id']
    if rp_id == '':
      rp_id = self.generate_rpid(self.post_form['name'], self.conf['oidc_clients'].keys())
      self.conf['oidc_clients'][rp_id] = {}
    
    rp = self.conf['oidc_clients'][rp_id]
    
    for item in ['name', 'endpoint_configuration', 'discovery_uri', 'issuer', 'authorization_endpoint', 'token_endpoint', 
    'end_session_endpoint', 'userinfo_endpoint', 'signature_key_configuration', 'jwks_uri', 'signature_key', 
    'client_id', 'client_secret!', 'scope', 'response_type']:
      if self.post_form[item] == '':
        rp.pop(item, None)
      else:
        rp[item] = self.post_form[item]
      
    if 'fetch_userinfo' in self.post_form:
      rp['fetch_userinfo'] = 'on'
    else:
      rp['fetch_userinfo'] = 'off'

    Configuration.write_configuration(self.conf)
    
    self.send_redirection('/')


  def remove(self):
  
    """
    Supprime un client OpenID Connect
    
    mpham 28/12/2021
    """

    rp_id = self.get_query_string_param('id')
    if rp_id is not None:
      self.conf['oidc_clients'].pop(rp_id, None)
      Configuration.write_configuration(self.conf)
      
    self.send_redirection('/')


  def generate_rpid(self, name, existing_names):
    
    """
    Génère un identifiant à partir d'un nom
    en ne retenant que les lettres et les chiffres
    et en vérifiant que l'identifiant n'existe pas déjà
    
    S'il existe, ajoute un suffixe numérique
    
    mpham 28/02/2021
    """
    
    base = name
    ok = False
    rank = 0
    
    while not ok:
      id = ''.join(c for c in base.casefold() if c.isalnum())
      if id == '':
        id = 'oidc_rp'
      if rank > 0:
        id = id+str(rank)
      
      if id in existing_names:
        rank = rank+1
      else:
        ok = True
        
    return id
