from .BaseServer import AduneoError
from .BaseServer import BaseHandler
from .BaseServer import BaseServer
from .Configuration import Configuration
from datetime import datetime
from lxml import etree
import base64
import html
import os
import requests
import traceback
import urllib.parse
import uuid
import xmlsec
import zlib


class SAMLClientLogin(BaseHandler):
 
  def prepare_request(self):

    client_id = self.get_query_string_param('id')
    relay_state = self.get_query_string_param('relay_state')
    if client_id is None:
      if relay_state is None:
        self.send_redirection('/')
      else:
        # Rejeu de requête (conservée dans la session)
        client = self.get_session_value(relay_state)
        if (client is None):
          self.send_redirection('/')
        client_id = client['client_id']
        #self.del_session_value(relay_state)   TODO
        
        conf_client = self.conf['saml_clients'][client_id]
        client['name'] = conf_client['name']
        
    else:
      # Nouvelle requête
      if client_id not in self.conf['saml_clients']:
        self.send_redirection('/')
      client = self.conf['saml_clients'][client_id]

      # récupération des clés
      if client.get('sp_key_configuration').casefold() == 'server keys':
        self.log_info('Fetching local web server keys as SP keys')
        conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
        
        key_filename = self.conf['server'].get('ssl_key_file')
        if key_filename is None:
          self.log_info('  Local web server private key file name not present in configuration file')
          client['sp_private_key'] = ''
        else:
          key_path = os.path.join(conf_dir, key_filename)
          with open(key_path) as key_file:
            client['sp_private_key'] = ''.join(key_file.readlines()[1:-1]).replace('\n', '')
            
        cert_filename = self.conf['server'].get('ssl_cert_file')
        if cert_filename is None:
          self.log_info('  Local web server certificate file name not present in configuration file')
          client['sp_certificate'] = ''
        else:
          cert_path = os.path.join(conf_dir, cert_filename)
          with open(cert_path) as cert_file:
            client['sp_certificate'] = ''.join(cert_file.readlines()[1:-1]).replace('\n', '')
  


    relay_state = str(uuid.uuid4())
                                          
    self.add_content("<h1>SAML SP: "+client["name"]+"</h1>")
    self.add_content('<form name="request" action="/saml/client/sendrequest" method="post">')
    self.add_content('<input name="client_id" value="'+html.escape(client_id)+'" type="hidden" />')
    self.add_content('<table class="fixed">')
     
    self.add_content('<tr><td>IdP Entity ID</td><td><input name="idp_entity_id" value="'+html.escape(client.get('idp_entity_id', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>IdP Certificate</td><td><textarea name="idp_certificate" rows="10" class="intable">'+html.escape(client.get('idp_certificate', ''))+'</textarea></td></tr>')
    self.add_content('<tr><td>IdP Single Sign-On URL</td><td><input name="idp_sso_url" value="'+html.escape(client.get('idp_sso_url', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>SP Entity ID</td><td><input name="sp_entity_id" value="'+html.escape(client.get('sp_entity_id', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>SP Assertion Consumer Service URL</td><td><input name="sp_acs_url" value="'+html.escape(client.get('sp_acs_url', ''))+'" class="intable" type="text"></td></tr>')
    self.add_content('<tr><td>NameID Policy</td><td><input name="nameid_policy" value="'+html.escape(client.get('nameid_policy', ''))+'" class="intable" type="text"></td></tr>')
    
    self.add_content('<tr><td>Authentication binding</td><td><select name="authentication_binding" class="intable" onchange="reset_keys_fields()">')
    for value in ('urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect', 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'):
      selected = ''
      if value == client.get('authentication_binding', 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'):
        selected = ' selected'
      self.add_content('<option value="'+value+'"'+selected+'>'+html.escape(value)+'</value>')
    self.add_content('</select></td></tr>')

    checked = ''
    if Configuration.is_on(client.get('sign_auth_request', 'off')):
      checked = ' checked'
    self.add_content('<tr><td>Sign authentication request</td><td><input name="sign_auth_request" type="checkbox"'+checked+' onchange="reset_keys_fields()"></td></tr>')

    display_sp_private_key = 'none'
    display_sp_certificate = 'none'
    if Configuration.is_on(client.get('sign_auth_request', 'off')):
      display_sp_private_key = 'table-row'
      if client.get('authentication_binding') == 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post':
        display_sp_certificate = 'table-row'

    self.add_content('<tr id="sp_private_key_row" style="display: '+display_sp_private_key+'"><td>SP Private Key</td><td><textarea name="sp_private_key" rows="10" class="intable">'+html.escape(client['sp_private_key'])+'</textarea></td></tr>')
    self.add_content('<tr id="sp_certificate_row" style="display: '+display_sp_certificate+'"><td>SP Certificate</td><td><textarea name="sp_certificate" rows="10" class="intable">'+html.escape(client['sp_certificate'])+'</textarea></td></tr>')
      
    self.add_content('</table>')
    
    self.add_content('<div style="padding-top: 20px; padding-bottom: 12px;"><div style="padding-bottom: 6px;"><strong>Authentication request</strong> <img title="Copy request" class="smallButton" src="/images/copy.png" onClick="copyRequest()"/></div>')
    self.add_content('<span id="auth_request" style="font-size: 14px;"></span></div>')
    self.add_content('<input name="authentication_request" type="hidden">')
    self.add_content('<input name="relay_state" value="'+html.escape(relay_state)+'" type="hidden">')
    
    self.add_content('<button type="submit" class="button">Send to IdP</button>')
    self.add_content('</form>')

    self.add_content("""
      <script>
      function reset_keys_fields() {
        if (document.request.sign_auth_request.checked) {
          document.getElementById('sp_private_key_row').style.display = 'table-row';
          if (document.request.authentication_binding.value == 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST') {
            document.getElementById('sp_certificate_row').style.display = 'table-row';
          } else {
            document.getElementById('sp_certificate_row').style.display = 'none';
          }
        } else {
          document.getElementById('sp_private_key_row').style.display = 'none';
          document.getElementById('sp_certificate_row').style.display = 'none';
        }
      }
      </script>
    """)
      
    self.send_page()
      

  def send_request(self):
  
    self.log_info('Redirection to SAML IdP requested')
    relay_state = self.post_form.get('relay_state')

    client_id = self.post_form['client_id']
    conf_client = self.conf['saml_clients'][client_id]

    request = {}
    for item in ['client_id', 'relay_state', 'idp_entity_id', 'idp_certificate', 'idp_sso_url', 'sp_entity_id', 
      'sp_acs_url', 'authentication_binding', 'sp_private_key', 'sp_certificate', 'sign_auth_request']:
      if self.post_form.get(item, '') != '':
        request[item] = self.post_form[item]
    request['nameid_policy'] = self.post_form.get('nameid_policy', 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified')

    self.set_session_value(relay_state, request)
        
    authentication_binding = request.get('authentication_binding', '')
    if authentication_binding == '':
      error_message = 'Authentication binding not found'
      self.log_error(error_message)
      self.send_page(error_message)
    if authentication_binding == 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect':
      self.send_request_redirect(request, conf_client)
    elif authentication_binding == 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST':
      self.send_request_post(request, conf_client)
    else:
      error_message = 'Authentication binding '+authentication_binding+' not supported'
      self.log_error(error_message)
      self.send_page(error_message)

  
  def send_request_redirect(self, request, conf_client):
    
    relay_state = request['relay_state']
    
    req_template = """
    <samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="{id}" Version="2.0" ProviderName="{provider_name}" IssueInstant="{timestamp}" Destination="{destination}" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" AssertionConsumerServiceURL="{acs_url}">
      <saml:Issuer>{sp_id}</saml:Issuer>
      <samlp:NameIDPolicy Format="{nameid_policy}" AllowCreate="true"/>
    </samlp:AuthnRequest>
    """
    
    req_id = 'id'+str(uuid.uuid4())
    request['request_id'] = req_id   # pour validation du subject de l'assertion
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')     # 2014-07-16T23:52:45Z
    
    xml_req = req_template.format(
      id = req_id, 
      provider_name = conf_client['name'], 
      timestamp = timestamp, 
      destination = request['idp_sso_url'], 
      acs_url = request['sp_acs_url'], 
      sp_id = request['sp_entity_id'],
      nameid_policy = request['nameid_policy']
      )
    
    self.log_info("Authentication request:", 1)
    self.log_info(xml_req, 1)
    
    # on deflate la requête
    compress = zlib.compressobj(
            zlib.Z_DEFAULT_COMPRESSION, # level: 0-9
            zlib.DEFLATED,        # method: must be DEFLATED
            -zlib.MAX_WBITS,      # window size in bits:
                                  #   -15..-8: negate, suppress header
                                  #   8..15: normal
                                  #   16..30: subtract 16, gzip header
            zlib.DEF_MEM_LEVEL,   # mem level: 1..8/9
            0                     # strategy:
                                  #   0 = Z_DEFAULT_STRATEGY
                                  #   1 = Z_FILTERED
                                  #   2 = Z_HUFFMAN_ONLY
                                  #   3 = Z_RLE
                                  #   4 = Z_FIXED
    )
    deflated_req = compress.compress(xml_req.encode('iso-8859-1'))
    deflated_req += compress.flush()    

    base64_req = base64.b64encode(deflated_req)
    self.log_info("Base64 encoded deflated authentication request:", 1)
    self.log_info(base64_req.decode(), 1)
    
    urlencoded_req = urllib.parse.quote_plus(base64_req)

    sign_auth_request = request.get('sign_auth_request', 'off')
    if Configuration.is_on(sign_auth_request):
    
      # Signature de la requête
      #   on construit le message SAMLRequest=value&RelayState=value&SigAlg=value
      #   (les valeurs doivent être URL-encoded)
      #   que l'on signe
      
      urlencoded_relay_state = urllib.parse.quote_plus(relay_state)
      urlencoded_sig_alg = urllib.parse.quote_plus('http://www.w3.org/2000/09/xmldsig#rsa-sha1')
      
      message = 'SAMLRequest='+urlencoded_req+'&RelayState='+urlencoded_relay_state+'&SigAlg='+urlencoded_sig_alg
      self.log_info('Signature message: '+message, 1)

      xmlsec.enable_debug_trace(True)

      if request.get('sp_private_key', '') == '':
        raise AduneoError("Missing private key, can't sign request")
      sp_private_key = '-----BEGIN PRIVATE KEY-----\n' + request['sp_private_key'] + '\n-----END PRIVATE KEY-----'

      ctx = xmlsec.SignatureContext()
      ctx.key = xmlsec.Key.from_memory(sp_private_key, xmlsec.KeyFormat.PEM, None)
      signature = ctx.sign_binary(message.encode(), xmlsec.constants.TransformRsaSha1)
      base64_signature = base64.b64encode(signature).decode()
      self.log_info('Signature: '+base64_signature, 1)

      url = self.post_form['idp_sso_url'] + '?' + message + '&signature=' + urllib.parse.quote_plus(base64_signature)
      self.log_info('URL: '+url, 1)
      
      self.log_info('Sending redirection', 1)
      self.send_redirection(url)
      
    else:
      # requête non signée
    
      url = request['idp_sso_url'] + '?SAMLRequest=' + urlencoded_req + '&RelayState=' + urllib.parse.quote_plus(relay_state)
      print(url)
      
      self.send_redirection(url)


  def send_request_post(self, request, conf_client):

    relay_state = request['relay_state']

    req_id = 'id'+str(uuid.uuid4())
    request['request_id'] = req_id   # pour validation du subject de l'assertion
    self.log_info('Constructing authentication request '+req_id, 1)
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')     # 2014-07-16T23:52:45Z

    req_template = """
    <samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="{id}" Version="2.0" ProviderName="{provider_name}" IssueInstant="{timestamp}" Destination="{destination}" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" AssertionConsumerServiceURL="{acs_url}">
      <saml:Issuer>{sp_id}</saml:Issuer>
      <samlp:NameIDPolicy Format="{nameid_policy}" AllowCreate="true"/>
    </samlp:AuthnRequest>
    """

    xml_req = req_template.format(
      id = req_id, 
      provider_name = conf_client['name'], 
      timestamp = timestamp, 
      destination = request['idp_sso_url'], 
      acs_url = request['sp_acs_url'], 
      sp_id = request['sp_entity_id'],
      nameid_policy = request['nameid_policy']
      )
    
    self.log_info("Authentication request:", 1)
    self.log_info(xml_req, 1)
    
    byte_xml_req = xml_req.encode()

    sign_auth_request = self.post_form.get('sign_auth_request', 'off')
    if Configuration.is_on(sign_auth_request):
    
      # Signature de la requête
      template = etree.fromstring(xml_req)
      xmlsec.tree.add_ids(template, ["ID"]) 

      # on crée le noeud pour la signature
      signature_node = xmlsec.template.create(
        template,
        c14n_method=xmlsec.Transform.EXCL_C14N,
        sign_method=xmlsec.Transform.RSA_SHA1,
        ns='ds')

      # Pour que le XML soit valide, il faut ajouter la signature après l'issuer
      issuer_el = template.find('{urn:oasis:names:tc:SAML:2.0:assertion}Issuer')
      issuer_el.addnext(signature_node)
#      template.append(signature_node)
      ref = xmlsec.template.add_reference(signature_node, xmlsec.Transform.SHA1, uri='#'+req_id)
      xmlsec.template.add_transform(ref, xmlsec.Transform.ENVELOPED)
      xmlsec.template.add_transform(ref, xmlsec.constants.TransformExclC14N)
      key_info = xmlsec.template.ensure_key_info(signature_node)
      xmlsec.template.add_x509_data(key_info)  

      # on signe le XML

      if request.get('sp_private_key', '') == '':
        raise AduneoError("Missing private key, can't sign request")
      sp_private_key = '-----BEGIN PRIVATE KEY-----\n' + request['sp_private_key'] + '\n-----END PRIVATE KEY-----'
      if request.get('sp_certificate', '') == '':
        raise AduneoError("Missing certificate, can't sign request")
      sp_certificate = '-----BEGIN CERTIFICATE-----\n' + request['sp_certificate'] + '\n-----END CERTIFICATE-----'

      ctx = xmlsec.SignatureContext()
      ctx.key = xmlsec.Key.from_memory(sp_private_key, xmlsec.KeyFormat.PEM, None)
      ctx.key.load_cert_from_memory(sp_certificate, xmlsec.KeyFormat.CERT_PEM)
      ctx.sign(signature_node)
      self.log_info('Signed request:', 1)
      self.log_info(etree.tostring(template, pretty_print=True).decode(), 1)
      
      byte_xml_req = etree.tostring(template)
      
    base64_req = base64.b64encode(byte_xml_req).decode()
    self.log_info("Base64 encoded authrntication request:", 1)
    self.log_info(base64_req, 1)

    self.send_page_top(200, template=False)
    
    self.add_content('<html><body onload="document.saml.submit()">')
    self.add_content('<html><body>')
    self.add_content('<form name="saml" action="'+self.post_form['idp_sso_url']+'" method="post">')
    self.add_content('<input type="hidden" name="SAMLRequest" value="'+html.escape(base64_req)+'" />')
    self.add_content('<input type="hidden" name="RelayState" value="'+html.escape(relay_state)+'" />')
    #self.add_content('<input type="submit"/>')
    self.add_content('</form></body></html>')
    
    
  def authcallback(self):
    
    """
    Retour d'authentification (endpoint ACS)
    
    Problème Chrome et "SameSite by default"
    
    Chrome bloque parfois le cookie de session en retour SAML parce qu'il considère le cookie en Lax par défaut.
    De ce fait, lorsque l'IdP poste sa réponse, elle arrive d'un autre site que celui du client (souvent localhost)
    et Chrome n'envoie pas le cookie de session.
    
    Parfois, ça fonctionne quand même, je n'ai pas encore compris pourquoi.
    
    Une description par Okta : https://support.okta.com/help/s/article/FAQ-How-Chrome-80-Update-for-SameSite-by-default-Potentially-Impacts-Your-Okta-Environment?language=en_US
    Une discussion StackOverflow : https://stackoverflow.com/questions/60068271/samesite-attribute-break-saml-flow
    
    Il faudrait donc passer en SameSite=None pour autoriser que le cookie de session soit envoyé depuis l'IdP
    Mais ça requiert HTTPS (ne fonctionne donc pas en HTTP)
    
    On résout le problème en renvoyant un formulaire au navigateur avec un autosubmit :
      les informations proviennent du client et tout rentre dans l'ordre
      (il faut cependant faire attention à ne pas créer une nouvelle session, voir Server.do_POST)
    
    mpham 03/03/2021-05/03/2021
    """
    
    # Problème cookie SameSite=Lax
    if self.hreq.headers.get('Cookie') is None:
      self.log_error('Session cookie not sent by brower (SameSite problem), form is sent to brower and autosubmitted')
      self.send_page_top(200, template=False, send_cookie=False)
      
      self.add_content('<html><body onload="document.saml.submit()">')
      self.add_content('<form name="saml" method="post">')
      for item in self.post_form:
        self.add_content('<input type="hidden" name="'+html.escape(item)+'" value="'+html.escape(self.post_form[item])+'" />')
      #self.add_content('<input type="submit" />')
      self.add_content('</form></body></html>')
      return
      

    self.send_page_top(200)
    self.add_content("""<script src="/javascript/resultTable.js"></script>""")

    self.log_info('Authentication callback')
    

    try:

      self.log_info('raw response:', 1)
      self.log_info(str(self.post_form), 1)
    
      self.log_info('Checking authentication')
      
      # récupération de relay_state pour obtention des paramètres dans la session
      idp_relay_state = self.post_form.get('RelayState', None)
      if idp_relay_state is None:
        raise AduneoError('Relay state not found in POST data')
      self.log_info('for relay state: '+idp_relay_state, 1)
      auth_req = self.get_session_value(idp_relay_state)
      if (auth_req is None):
        print(str(self.hreq.sessions))
        raise AduneoError(self.log_error('relay state not found in session'))
        
      client_id = auth_req['client_id']
      conf_client = self.conf['saml_clients'][client_id]
      self.log_info('SP Name: '+conf_client['name'], 1)
        
      self.add_content('<h2>Authentication callback for '+html.escape(conf_client['name'])+'</h2>')
      self.start_result_table()
        
      self.add_result_row('Relay state returned by IdP', idp_relay_state)
      self.add_result_row('Raw response', str(self.post_form))

      # analyse du XML de réponse
      base64_resp = self.post_form.get('SAMLResponse', None)
      if base64_resp is None:
        raise AduneoError('SAMLResponse not found in POST data')
      xml_resp = base64.b64decode(base64_resp).decode()

      self.log_info(xml_resp, 1)

      root_el = etree.fromstring(xml_resp.encode())
      self.add_result_row('XML response', etree.tostring(root_el, pretty_print=True).decode())
      
      # Vérification du statut
      try:
        status_el = root_el.find('{urn:oasis:names:tc:SAML:2.0:protocol}Status')
        if status_el is None:
          raise AduneoError('Status element not found')
        status_code_el = status_el.find('{urn:oasis:names:tc:SAML:2.0:protocol}StatusCode')
        if status_code_el is None:
          raise AduneoError('StatusCode element not found')
        status_code = status_code_el.attrib['Value']
        self.log_info('Status code: '+status_code, 2)
        
        if status_code == 'urn:oasis:names:tc:SAML:2.0:status:Success':
          self.add_result_row('Status authenticated', status_code)
        else:
          self.add_result_row('Status failed', status_code)
          raise AduneoError('wrong status: '+status_code)
        
      except Exception as error:
        self.log_error("Status verification failed: "+str(error), 1)
        raise AduneoError('status verification failed: '+str(error))
        
      # Vérification d'issuer
      self.log_info('Issuer verification', 1)
      try:
        issuer_el = root_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}Issuer')
        if issuer_el is None:
          raise AduneoError('Issuer element not found')
        issuer = issuer_el.text
        self.log_info('issuer       : '+issuer, 2)
        self.log_info('IdP entity id: '+auth_req['idp_entity_id'], 2)
        
        if issuer == auth_req['idp_entity_id']:
          self.add_result_row('Issuer verification passed', issuer)
        else:
          title = 'Issuer verification failed'
          value = issuer+' (response) != '+auth_req['idp_entity_id']+' (conf)'
          self.add_result_row(title, value)
          raise AduneoError(title)
        
      except Exception as error:
        self.log_error("Issuer verification failed: "+str(error), 1)
        raise AduneoError('issuer verification failed: '+str(error))

      # Vérification de signature de la réponse
      self.log_info('Response signature verification', 1)
      try:
        self.log_info('IdP Certificate', 2)
        self.log_info(auth_req['idp_certificate'], 2)
      
        cert = '-----BEGIN CERTIFICATE-----\n' + auth_req['idp_certificate'] + '\n-----END CERTIFICATE-----'
      
        xmlsec.enable_debug_trace(True)
        xmlsec.tree.add_ids(root_el, ["ID"]) # -> correspond à l'attribut ID dans le tag response, c'est demandé par XML Signature
        # Référence : https://www.aleksey.com/xmlsec/faq.html (section 3.2) : LibXML2 and XMLSec libraries do support ID attributes. However, you have to tell LibXML2/XMLSec what is the name of your ID attribute. XML specification does not require ID attribute to have name "Id" or "id". It can be anything you want!
        # Ca permet à XMLSec de faire le lien entre la signature et le contenu. Dans la signature, il y a une référence par URI="# à la reponse au travers d'un identifiant unique. Il faut indiquer que la recherche du contenu se fait apr le tag ID
        signature_node = xmlsec.tree.find_node(root_el, xmlsec.constants.NodeSignature)
        
        manager = xmlsec.KeysManager()
        manager.load_cert_from_memory(cert, xmlsec.constants.KeyDataFormatPem, xmlsec.KeyDataType.TRUSTED)
        ctx = xmlsec.SignatureContext(manager)
        ctx.verify(signature_node)
        self.log_info('Response signature verification: OK', 2)
        self.add_result_row('Response signature verification', 'Passed')
      
      except Exception as error:
        self.log_error("Response signature verification failed: "+str(error), 1)
        self.add_result_row('Response signature failed', str(error))
        raise AduneoError('Response signature verification failed: '+str(error))

      # Extraction de l'assertion
      self.log_info('Extracting assertion', 1)
      assertion_el = root_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
      if assertion_el is None:
        # on ne trouve pas l'assertion directement, elle est peut-être chiffrée
        self.log_info('Element Assertion not found, looking for EncryptedAssertion', 2)
        
        encrypted_assertion_el = root_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAssertion')
        if encrypted_assertion_el is None:
          raise AduneoError('Neither Assertion nor EncryptedAssertion elements found')

        self.log_info('EncryptedAssertion', 2)
        self.log_info(etree.tostring(encrypted_assertion_el).decode(), 2)
        
        xmlsec.tree.add_ids(encrypted_assertion_el, ["Id"]) # attention, on est case sensitive !
        
        sp_private_key = '-----BEGIN PRIVATE KEY-----\n' + auth_req['sp_private_key'] + '\n-----END PRIVATE KEY-----'
        
        manager = xmlsec.KeysManager()
#        manager.add_key(xmlsec.Key.from_file('conf/localhost.key', xmlsec.KeyFormat.PEM, None))
        manager.add_key(xmlsec.Key.from_memory(sp_private_key, xmlsec.KeyFormat.PEM, None))
        enc_ctx = xmlsec.EncryptionContext(manager)
        enc_data = xmlsec.tree.find_child(encrypted_assertion_el, "EncryptedData", xmlsec.constants.EncNs)
        assertion_el = enc_ctx.decrypt(enc_data)
        self.log_info('Assertion decrypted', 2)
        self.add_result_row('Assertion decryption', 'OK')
      
      self.log_info('XML assertion', 2)
      self.log_info(etree.tostring(assertion_el).decode(), 2)
      self.add_result_row('XML assertion', etree.tostring(assertion_el, pretty_print=True).decode())

      # Extraction des conditions de validité de l'assertion
      conditions_el = assertion_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}Conditions')
      if conditions_el is None:
        raise AduneoError('Conditions element not found')
      
      # Vérification de timestamp
      now = datetime.utcnow()
      
      self.log_info("NotBefore condition verification:", 1)
      not_before_str = conditions_el.attrib.get('NotBefore')
      if not_before_str is None:
        raise AduneoError('NotBefore attribute not found')
      self.log_info('NotBefore attribute: '+not_before_str,2)
      
      not_before_date = datetime.strptime(not_before_str, '%Y-%m-%dT%H:%M:%S.%fZ')
      self.log_info("Assertion NotBefore: "+str(not_before_date)+' UTC', 2)
      self.log_info("Now                : "+str(now)+' UTC', 2)
      if now > not_before_date:
        self.log_info("NotBefore condition verification OK", 2)
        self.add_result_row('NotBefore condition passed', str(not_before_date)+' UTC (now is '+str(now)+' UTC)')
      else:
        self.log_info("NotBefore condition verification failed", 2)
        self.add_result_row('NotBefore condition failed', str(not_before_date)+' UTC (now is '+str(now)+' UTC)')
        raise AduneoError('NotBefore condition failed')
        
      self.log_info("NotOnOrAfter condition verification:", 1)
      not_on_or_after_str = conditions_el.attrib.get('NotOnOrAfter')
      if not_on_or_after_str is None:
        raise AduneoError('NotOnOrAfter attribute not found')
      self.log_info('NotOnOrAfter attribute: '+not_on_or_after_str,2)
      
      not_on_or_after_date = datetime.strptime(not_on_or_after_str, '%Y-%m-%dT%H:%M:%S.%fZ')
      self.log_info("Assertion NotOnOrAfter: "+str(not_on_or_after_date)+' UTC', 2)
      self.log_info("Now                : "+str(now)+' UTC', 2)
      if now < not_on_or_after_date:
        self.log_info("NotOnOrAfter condition verification OK", 2)
        self.add_result_row('NotOnOrAfter condition passed', str(not_on_or_after_date)+' UTC (now is '+str(now)+' UTC)')
      else:
        self.log_info("NotOnOrAfter condition verification failed", 2)
        self.add_result_row('NotOnOrAfter condition failed', str(not_on_or_after_date)+' UTC (now is '+str(now)+' UTC)')
        raise AduneoError('NotOnOrAfter condition failed')
      
      # Vérification d'audience
      self.log_info("Audience condition verification:", 1)
      
      audience_restriction_el = conditions_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction')
      if audience_restriction_el is None:
        raise AduneoError('AudienceRestriction element not found')
      audience_el = audience_restriction_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}Audience')
      if audience_el is None:
        raise AduneoError('Audience element not found')
      audience = audience_el.text
      self.log_info("Audience    : "+audience, 2)
      self.log_info("SP Entity ID: "+auth_req['sp_entity_id'], 2)
      if audience == auth_req['sp_entity_id']:
        self.log_info("Audience condition OK", 2)
        self.add_result_row('Audience condition passed', audience)
      else:
        self.log_info("Audience condition failed", 2)
        title = 'Audience condition failed'
        value = audience+' (response) != '+auth_req['sp_entity_id']+' (conf)'
        self.add_result_row(title, value)
        raise AduneoError(title)
      
      # Vérification de signature de l'assertion
      self.log_info('Assertion signature verification', 1)
      try:
        self.log_info('IdP Certificate', 2)
        self.log_info(auth_req['idp_certificate'], 2)
      
        cert = '-----BEGIN CERTIFICATE-----\n' + auth_req['idp_certificate'] + '\n-----END CERTIFICATE-----'
      
        xmlsec.enable_debug_trace(True)
        xmlsec.tree.add_ids(assertion_el, ["ID"]) # -> correspond à l'attribut ID dans le tag response, c'est demandé par XML Signature
        # Référence : https://www.aleksey.com/xmlsec/faq.html (section 3.2) : LibXML2 and XMLSec libraries do support ID attributes. However, you have to tell LibXML2/XMLSec what is the name of your ID attribute. XML specification does not require ID attribute to have name "Id" or "id". It can be anything you want!
        # Ca permet à XMLSec de faire le lien entre la signature et le contenu. Dans la signature, il y a une référence par URI="# à la reponse au travers d'un identifiant unique. Il faut indiquer que la recherche du contenu se fait apr le tag ID
        signature_node = xmlsec.tree.find_node(assertion_el, xmlsec.constants.NodeSignature)
        
        manager = xmlsec.KeysManager()
        manager.load_cert_from_memory(cert, xmlsec.constants.KeyDataFormatPem, xmlsec.KeyDataType.TRUSTED)
        ctx = xmlsec.SignatureContext(manager)
        ctx.verify(signature_node)
        self.log_info('Assertion signature verification: OK', 2)
        self.add_result_row('Assertion signature verification', 'Passed')
      
      except Exception as error:
        self.log_error("Assertion signature verification failed: "+str(error), 1)
        self.add_result_row('Assertion signature failed', str(error))
        raise AduneoError('Assertion signature verification failed: '+str(error))

      
      # Extraction du subject
      self.log_info('Subject parsing', 1)
      subject_el = assertion_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}Subject')
      if subject_el is None:
        self.log_info('Subject element not found in assertion', 2)
        self.add_result_row('Subject', 'Not found in assertion')
        raise AduneoError('Subject element not found in assertion')
        
      # Récupération du NameID
      nameid_el = subject_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}NameID')
      if nameid_el is None:
        self.log_info('NameID element not found in subject', 2)
        self.add_result_row('NameID', 'Not found in subject')
        raise AduneoError('NameID element not found in subject')
        
      nameid = nameid_el.text
      self.log_info('NameID: '+nameid, 2)
      self.add_result_row('NameID', nameid)
          
      # Validation du subject
      subjectconfirmation_el = subject_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmation')
      if subjectconfirmation_el is None:
        self.log_info('SubjectConfirmation element not found in subject', 2)
        self.add_result_row('SubjectConfirmation', 'Not found in subject')
        raise AduneoError('SubjectConfirmation element not found in subject')
      
      subjectconfirmationdata_el = subjectconfirmation_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationData')
      if subjectconfirmationdata_el is None:
        self.log_info('SubjectConfirmationData element not found in SubjectConfirmation', 2)
        self.add_result_row('SubjectConfirmation', 'Not found in SubjectConfirmation')
        raise AduneoError('SubjectConfirmation element not found in SubjectConfirmation')
      
      # Vérification de l'identifiant de la requête
      in_response_to = subjectconfirmationdata_el.attrib.get('InResponseTo')
      if in_response_to is not None:
        self.log_info('Subject InResponseTo verification', 1)
        self.log_info("InResponseTo: "+in_response_to, 2)
        self.log_info("Request ID  : "+auth_req['request_id'], 2)
        if in_response_to == auth_req['request_id']:
          self.log_info("Subject InResponseTo verification passed", 2)
          self.add_result_row('Subject InResponseTo verification passed', in_response_to)
        else:
          self.log_info("Subject InResponseTo verification failed", 2)
          title = 'Subject InResponseTo verification failed'
          value = in_response_to+' (response) != '+auth_req['request_id']+' (authn request)'
          self.add_result_row(title, value)
          raise AduneoError(title)
      
      # Vérification du destinataire
      recipient = subjectconfirmationdata_el.attrib.get('Recipient')
      if recipient is not None:
        self.log_info('Subject Recipient verification', 1)
        self.log_info("Recipient : "+recipient, 2)
        self.log_info("SP ACS URL: "+auth_req['sp_acs_url'], 2)
        if recipient == auth_req['sp_acs_url']:
          self.log_info("Subject Recipient verification passed", 2)
          self.add_result_row('Subject Recipient verification passed', recipient)
        else:
          self.log_info("Subject Recipient verification failed", 2)
          title = 'Subject Recipient verification failed'
          value = recipient+' (response) != '+auth_req['sp_acs_url']+' (SP ACS URL)'
          self.add_result_row(title, value)
          raise AduneoError(title)

      # Vérification d'expiration (NotOnOrAfter)
      not_on_or_after_str = subjectconfirmationdata_el.attrib.get('NotOnOrAfter')
      if not_before_str is not None:
        self.log_info('Subject NotOnOrAfter verification', 1)
        not_on_or_after_date = datetime.strptime(not_on_or_after_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        if now < not_on_or_after_date:
          self.log_info("Subject NotOnOrAfter verification passed", 2)
          self.add_result_row('NotOnOrAfter verification passed', str(not_on_or_after_date)+' UTC (now is '+str(now)+' UTC)')
        else:
          self.log_info("Subject NotOnOrAfter verification failed", 2)
          title = 'Subject NotOnOrAfter verification failed'
          value = str(not_on_or_after_date)+' UTC (now is '+str(now)+' UTC)'
          self.add_result_row(title, value)
          raise AduneoError(title)
      
      # Extraction de SessionIndex
      self.log_info('Extracting AuthnStatement for SessionIndex', 1)
      authn_statement_el = assertion_el.find('{urn:oasis:names:tc:SAML:2.0:assertion}AuthnStatement')
      if authn_statement_el is None:
        self.log_info('AuthnStatement element not found in assertion', 2)
        self.add_result_row('AuthnStatement', 'Not found in assertion')
        raise AduneoError('AuthnStatement element not found in assertion')
      session_index = authn_statement_el.attrib.get('SessionIndex', '')
      self.log_info("SessionIndex: "+session_index, 2)
      self.add_result_row('SessionIndex', session_index)
      
      self.end_result_table()
      self.add_content('<h3>Authentication succcessful</h3>')

      self.add_content('<form action="/saml/client/preparerequest" method="get">')
      self.add_content("""<input type="hidden" name="relay_state" value="""+'"'+html.escape(idp_relay_state)+'" />')
      self.add_content("""<button type="submit" class="button">Retry</button>""")
      self.add_content("""</form>""")
      
      self.send_page_bottom()

      # on considère qu'on est bien loggé
      #   on place dans la session le NameID, son format et le SessionIndex, utilisés ensuite pour le logout
      self.logon('saml_client_'+client_id, 
        {'NameID': nameid, 'Format': nameid_el.attrib.get('Format'), 'SessionIndex': session_index})

    except AduneoError as error:
      self.end_result_table()
      self.add_content('<h3>Authentication failed : '+html.escape(str(error))+'</h3>')
    except Exception as error:
      self.log_error(traceback.format_exc(), 1)
      self.end_result_table()
      self.add_content('<h3>Authentication failed : '+html.escape(str(error))+'</h3>')

    self.send_page_bottom()

    
