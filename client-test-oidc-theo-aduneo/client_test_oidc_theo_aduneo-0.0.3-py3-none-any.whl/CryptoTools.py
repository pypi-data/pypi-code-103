from OpenSSL import crypto, SSL
import os
import tempfile


class CryptoTools:
  
  def generate_key_self_signed():
    
    """Génère un biclé RSA et retourne la clé et un certificat auto-signé en PEM
    
    :return: (clé privée en PEM, certificat autosigné en PEM)
    :rtype: (str, str)
    
    .. notes::
      mpham 21/05/2021
    """

    key_pair = crypto.PKey()
    key_pair.generate_key(crypto.TYPE_RSA, 4096)

    cert = crypto.X509()
    cert.get_subject().C = 'FR'
    cert.get_subject().L = 'Paris'
    cert.get_subject().O = 'Aduneo'
    cert.get_subject().CN = 'Federation Test'
    cert.get_subject().emailAddress = 'contact@aduneo.com'
    cert.set_serial_number(0)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key_pair)
    cert.sign(key_pair, 'sha512')

    private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair).decode("utf-8")
    certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8")
    
    return (private_key, certificate)
    
    
  def generate_temp_certificate(conf : dict):
    
    """Génère une biclé RSA et la stocke dans des fichiers temporaires du dossier conf
    Met le nom des fichiers dans les champs server/ssl_key_file et server/ssl_cert_file de l'objet de configuration
    
    :param conf: object JSON de configuration
    :type conf: dict
    
    .. notes::
      mpham 21/05/2021
    """
    
    key_pair = crypto.PKey()
    key_pair.generate_key(crypto.TYPE_RSA, 4096)
    
    cert = crypto.X509()
    cert.get_subject().C = 'FR'
    cert.get_subject().L = 'Paris'
    cert.get_subject().O = 'Aduneo'
    cert.get_subject().CN = conf['server']['host']
    cert.get_subject().emailAddress = 'contact@aduneo.com'
    cert.set_serial_number(0)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key_pair)
    cert.sign(key_pair, 'sha512')

    conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
    
    fd, path = tempfile.mkstemp(prefix="temp_", dir=conf_path, text=True)
    with open(fd, 'w') as out_file:
      out_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair).decode("utf-8"))
    conf['server']['ssl_key_file'] = os.path.basename(path)
      
    fd, path = tempfile.mkstemp(prefix="temp_", dir=conf_path, text=True)
    with open(fd, 'w') as out_file:
      out_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    conf['server']['ssl_cert_file'] = os.path.basename(path)
    
