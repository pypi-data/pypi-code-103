from .BaseServer import AduneoError
from .BaseServer import BaseHandler
from .Configuration import Configuration
import html

class SAMLClientAdmin(BaseHandler):
  
  def display(self):
    
    """
    Ajout/modification d'un client SAML
    
    mpham 06/03/20241
    """
    
    sp = {}
    sp_id = self.get_query_string_param('id', '')
    if sp_id == '':
      sp['sp_entity_id'] = 'https://aduneo.com/FedTest/SAML'
      secure = ''
      if Configuration.is_on(self.conf['server']['ssl']):
        secure = 's'
      sp['sp_acs_url'] = 'http'+secure+'://'+self.conf['server']['host']+'/saml/client/acs'
    else:
      sp = self.conf['saml_clients'][sp_id]

    self.add_content('<script src="/javascript/SAMLClientAdmin.js"></script>')
    self.add_content('<h2>SAML SP Configuration</h3>')
    
    self.add_content('<form name="sp" action="/saml/client/modifyclient" method="post">')
    self.add_content('<input name="sp_id" value="'+html.escape(sp_id)+'" type="hidden" />')
    self.add_content('<table class="fixed">')
    self.add_content('<tr><td>Name</td><td><input name="name" value="'+html.escape(sp.get('name', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('</table>')
    
    self.add_content('<h3>Parameters coming from the idP</h3>')
    self.add_content('<table class="fixed">')
    self.add_content('<tr><td>&nbsp;</td><td><label for="upload_idp_metadata_input" class="middlebutton">Upload IdP Metadata</label><input id="upload_idp_metadata_input" type="file" style="display: none" onchange="uploadIdPMetadata(event)"></td></tr>')
    self.add_content('<tr><td>IdP Entity ID</td><td><input name="idp_entity_id" value="'+html.escape(sp.get('idp_entity_id', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>IdP SSO URL</td><td><input name="idp_sso_url" value="'+html.escape(sp.get('idp_sso_url', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>IdP SLO URL</td><td><input name="idp_slo_url" value="'+html.escape(sp.get('idp_slo_url', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>IdP Certificate</td><td><textarea name="idp_certificate" id="idp_certificate_input" rows="10" class="intable">'+html.escape(sp.get('idp_certificate', ''))+'</textarea>')
    self.add_content('  <label for="upload_idp_certificate_input" class="middlebutton">Upload certificate</label><input id="upload_idp_certificate_input" type="file" style="display: none" onchange="uploadPem(event)"/></td></tr>')
    self.add_content('</table>')
    
    self.add_content('<h3>Parameters to send to the idP</h3>')
    self.add_content('<table class="fixed">')
    self.add_content('<tr><td>SP Entity ID</td><td><input name="sp_entity_id" value="'+html.escape(sp.get('sp_entity_id', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>SP Assertion Consumer Service URL</td><td><input name="sp_acs_url" value="'+html.escape(sp.get('sp_acs_url', ''))+'" class="intable" type="text"></td></tr>')
    
    # configuration de la clé de vérification de signature
    self.add_content('<tr id="sp_key_configuration"><td>SP key configuration</td><td><select name="sp_key_configuration" class="intable" onchange="changeSPKeyConfiguration()">')
    for value in ('Server keys', 'Specific keys'):
      selected = ''
      if value.casefold() == sp.get('sp_key_configuration', 'Server keys').casefold():
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select>')
    
    display_style = 'none'
    if sp.get('sp_key_configuration', 'Server keys').casefold() == 'specific keys':
      display_style = 'block'
    self.add_content('&nbsp;&nbsp;<button id="generate_keys" type="button" class="middlebutton" onclick="generateKeys()" style="display: '+display_style+'">Generate keys</button>')
    self.add_content('</td></tr>')

    display_style = 'none'
    if sp.get('sp_key_configuration', 'Server keys').casefold() == 'server keys':
      display_style = 'table-row'
    self.add_content('<tr id="sp_download_server_certificate" style="display: '+display_style+'"><td>Server certificate</td><td><a href="/downloadservercertificate"><button type="button" class="middlebutton">Download certificate</button></a></td></tr>')

    display_style = 'none'
    if sp.get('sp_key_configuration', 'Server keys').casefold() == 'specific keys':
      display_style = 'table-row'
    self.add_content('<tr id="sp_private_key" style="display: '+display_style+'"><td>SP private key</td><td><textarea name="sp_private_key" id="sp_private_key_input" rows="10" class="intable">'+html.escape(sp.get('sp_private_key', ''))+'</textarea>')
    self.add_content('  <label for="upload_sp_private_key_input" class="middlebutton">Upload private key</label><input id="upload_sp_private_key_input" type="file" style="display: none" onchange="uploadPem(event)"/></td></tr>')
    self.add_content('<tr id="sp_certificate" style="display: '+display_style+'"><td>SP Certificate</td><td><textarea name="sp_certificate" id="sp_certificate_input" rows="10" class="intable">'+html.escape(sp.get('sp_certificate', ''))+'</textarea>')
    self.add_content('  <label for="upload_sp_certificate_input" class="middlebutton">Upload certificate</label><input id="upload_sp_certificate_input" type="file" style="display: none" onchange="uploadPem(event)"/></td></tr>')
    self.add_content('<tr id="sp_download_local_certificate" style="display: '+display_style+'"><td>Local certificate</td><td><button type="button" class="middlebutton" onclick="downloadLocalCertificate()">Download certificate</button></td></tr>')
    
    self.add_content('</table>')

    self.add_content('<h3>General parameters</h3>')
    self.add_content('<table class="fixed">')
    self.add_content('<tr><td>NameID Policy</td><td><input name="nameid_policy" value="'+html.escape(sp.get('nameid_policy', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>Authentication binding</td><td><select name="authentication_binding" class="intable">')
    for value in ('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect', 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'):
      selected = ''
      if value == sp.get('authentication_binding', 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'):
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select></td></tr>')

    checked = ''
    if Configuration.is_on(sp.get('sign_auth_request', 'off')):
      checked = ' checked'
    self.add_content('<tr><td>Sign authentication request</td><td><input name="sign_auth_request" type="checkbox"'+checked+'></td></tr>')

    self.add_content('<tr><td>Logout binding</td><td><select name="logout_binding" class="intable">')
    for value in ('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect', 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'):
      selected = ''
      if value == sp.get('logout_binding', 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'):
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select></td></tr>')

    checked = ''
    if Configuration.is_on(sp.get('sign_logout_request', 'off')):
      checked = ' checked'
    self.add_content('<tr><td>Sign logout request</td><td><input name="sign_logout_request" type="checkbox"'+checked+'></td></tr>')
    
    self.add_content('</table>')
    self.add_content('<button type="submit" class="button">Save</button>')
    self.add_content('</form>')

    self.add_content("""
    <script>
    function changeSPKeyConfiguration() {
      var server_display_style = 'none'
      var local_display_style = 'table-row'
      if (document.sp.sp_key_configuration.value == 'Server keys') {
        server_display_style = 'table-row'
        local_display_style = 'none'
      }
      document.getElementById('sp_download_server_certificate').style.display = server_display_style;
      ['sp_private_key', 'sp_certificate', 'sp_download_local_certificate'].forEach(function(item, index) {
        document.getElementById(item).style.display = local_display_style;
      });
      document.getElementById('generate_keys').style.display = (local_display_style == 'none' ? 'none' : 'inline');
    }
    
    function downloadLocalCertificate() {
    
      certificate = document.sp.sp_certificate.value
      if (!certificate.startsWith('-----BEGIN CERTIFICATE-----')) {
        segments = certificate.match(/.{1,64}/g)
        certificate = '-----BEGIN CERTIFICATE-----\\n'+segments.join('\\n')+'\\n-----END CERTIFICATE-----'
      }
      
      var element = document.createElement('a');
      element.setAttribute('href', 'data:application/x-pem-file;charset=utf-8,' + encodeURIComponent(certificate));
      element.setAttribute('download', 'aduneo.crt');

      element.style.display = 'none';
      document.body.appendChild(element);

      element.click();

      document.body.removeChild(element);
    }
    
    
    function generateKeys() {

      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          jsonResponse = JSON.parse(xhttp.responseText);
          document.getElementById("sp_private_key_input").innerHTML = stripPEM(jsonResponse.private_key);
          document.getElementById("sp_certificate_input").innerHTML = stripPEM(jsonResponse.certificate);
        }
      };
      xhttp.open("GET", "/generatecertificate", true);
      xhttp.send();
    }
    
    
    function stripPEM(pem) {
      items = pem.split('\\n');
      items.shift();
      items.pop();
      items.pop();
      return items.join();
    }
    
    </script>""")
    
    self.send_page()


  def modify(self):
  
    """
    Crée ou modifie un client SAML dans la configuration
    
    S'il existe, ajoute un suffixe numérique
    
    mpham 06/03/2021
    """
    
    sp_id = self.post_form['sp_id']
    if sp_id == '':
      sp_id = self.generate_spid(self.post_form['name'], self.conf['saml_clients'].keys())
      self.conf['saml_clients'][sp_id] = {}
    
    sp = self.conf['saml_clients'][sp_id]
    
    for item in ['name', 'idp_entity_id', 'idp_sso_url', 'idp_slo_url', 'idp_certificate', 'sp_entity_id', 'sp_acs_url', 
    'sp_key_configuration', 'sp_private_key', 'sp_certificate', 'nameid_policy', 'authentication_binding', 'logout_binding']:
      if self.post_form[item] == '':
        sp.pop(item, None)
      else:
        sp[item] = self.post_form[item]

    for item in ['sign_auth_request', 'sign_logout_request']:
      if item in self.post_form:
        sp[item] = 'on'
      else:
        sp[item] = 'off'

    Configuration.write_configuration(self.conf)
    
    self.send_redirection('/')


  def remove(self):
  
    """
    Supprime un client SAML
    
    mpham 06/03/2021
    """

    sp_id = self.get_query_string_param('id')
    if sp_id is not None:
      self.conf['saml_clients'].pop(sp_id, None)
      Configuration.write_configuration(self.conf)
      
    self.send_redirection('/')


  def generate_spid(self, name, existing_names):
    
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
        id = 'saml_sp'
      if rank > 0:
        id = id+str(rank)
      
      if id in existing_names:
        rank = rank+1
      else:
        ok = True
        
    return id
