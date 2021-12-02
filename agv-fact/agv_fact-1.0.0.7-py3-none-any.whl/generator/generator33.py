# -*- encoding: utf-8 -*-

from abc import abstractmethod, ABCMeta
from base64 import b64encode, b64decode
from urllib.request import urlopen
from xml.dom.minidom import parse
from xml.etree import ElementTree

import requests
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from lxml import etree
from lxml.etree import XSLTParseError
from Crypto.Hash import SHA256

from .contants import TRASLADO, EGRESO, INGRESO, PAGO, COMPLEMENTO_CARTA_PORTE, COMPLEMENTO_PAGO
from .utils import replace

import os
import logging


class DTDResolver(etree.Resolver):
    def resolve(self, url, id, context):
        url = 'https://www.sat.gob.mx/sitio_internet/cfd/3/cadenaoriginal_3_3/cadenaoriginal_3_3.xslt'
        print("Resolving URL '%s'" % url)
        return self.resolve_string(
            '<!ENTITY myentity "[resolved text: %s]">' % url, context)


class AbstractGeneratorXml(object):
    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.global_data = data
        self.data = data.get('data')
        self.dir_xml = os.path.dirname(os.path.abspath(__file__))
        self.dom = parse(self.dir_xml + '/comprobante.xml')
        self.algoritmoSha = None
        self.tipo_objeto = self.data.get('tipo') # I, E, P, T
        self.complemento = self.data.get('complemento', '') # Pago, CartaPorte
        self.tipo_transporte = self.data.get('tipo_transporte', '')
        self.version = ''
        self.cadena_original_value = ''

    @property
    def cadena_original(self) -> str:
        return self.cadena_original_value

    @abstractmethod
    def generate_xml(self):
        pass

    def create_xml(self, certificado_file_cer64, certificado_file_pem64):
        self.generate_xml()
        if self.global_data.get('provider') == 'solucion_factible':
            self.set_certificado(certificado_file_cer64)
            self.set_sello(certificado_file_pem64)

    def get_version(self):
        return self.data.get('version')

    def reset_dom(self):
        self.dom = parse(self.dir_xml + '/comprobante.xml')

    def get_xml(self):
        return self.dom.toxml(encoding='UTF-8')

    def get_xml_str(self):
        return self.dom.toxml(encoding='UTF-8').decode('utf8')

    def set_certificado(self, certificado64): #,certificado_file_cer):
        """
        Recibe el certificado abierto como archivo
        :param certificado_file:
        :return:
        """
        try:
            logging.info('OBTENIENDO EL CERTIFICADO DEL XML')
            #file = open(self.dir_xml + '//archivos//' + self.noCertificado + '.cer', 'rb')
            logging.info('CERTIFICADO DEL XML DEL INGRESO_ID')
            # certificado = certificado_file_cer.read()
            # certificado64 = b64encode(certificado)
            certificadoA = [certificado64[i:i + 76] for i in range(0, len(certificado64), 76)]
            certificadoF = ''
            for val in certificadoA:
                if certificadoF != '':
                    certificadoF += ' '
                certificadoF += val.decode("utf-8")
            self.dom.setAttribute('Certificado', certificadoF)
            logging.info('SETEO DEL CERTIFICADO EN EL XML')
        except Exception as e:
            logging.error('Error al generar el certificado. Error: ' + str(e))
            raise Exception(e)

    def set_sello(self, certificado_file_pem64): #, certificado_file_pem):
        try:
            logging.info('OBTENIENDO EL SELLO DEL XML')
            #file_pem = open(self.dir_xml + '/archivos/' + self.noCertificado + '.pem', 'rb')
            # key = RSA.importKey(certificado_file_pem.read())
            certificado_file_pem_bytes = b64decode(certificado_file_pem64)
            key = RSA.importKey(certificado_file_pem_bytes)
            logging.info('OBTENIENDO LA CADENA ORIGINAL DEL XML')
            self.cadena_original_value = self.get_cadena_original(self.get_xml())
            logging.info('LA CADENA ORIGINAL DEL XML')
            digest = self.algoritmoSha.new()
            digest.update(bytes(self.cadena_original_value))
            signer = PKCS1_v1_5.new(key)
            sign = signer.sign(digest)
            sello = b64encode(sign)
            self.dom.setAttribute('Sello', sello.decode("utf-8"))
        except Exception as e:
            logging.error('Error generar el sello. Error: ' + str(e))
            raise Exception(e)

    def get_cadena_original(self, xml):
        try:
            if type(xml) == str:
                xml = xml.encode('utf-8')
            xml = etree.fromstring(xml)
            logging.info('PARSE DE LA CADENA ORIGINAL DEL XML')
            logging.info(self.dir_xml)
            xslt = etree.parse(self.dir_xml + '/cadenaoriginal_3_3_local/cadenaoriginal_3_3.xslt')
            logging.info('XSLT CADENA ORIGINAL DEL XML')
            parser = etree.XSLT(xslt)
            logging.info('XSLT CADENA ORIGINAL DEL XML 2')
            cadena_original = parser(xml)
            logging.info('XSLT CADENA ORIGINAL DEL XML 3')
            return cadena_original
        except XSLTParseError as e:
            logging.error(u"Hubo un error al generar la cadena original, por favor intente mas tarde: " + str(e))
            raise Exception(u"Hubo un error al generar la cadena original, por favor intente mas tarde: " + str(e))
        except Exception as e:
            logging.error('Error al leer el archivo: cadenaoriginal_' + self.data.get('version') + '.xslt:' + str(e))
            raise Exception(e)

    @abstractmethod
    def get_datos(self, xml):
        pass

    def get_xml_info(self, xml):
        if type(xml) == str:
            xml = xml.encode('utf-8')
        root = ElementTree.fromstring(xml)
        xmlinfo = {}
        xmlinfo['xml'] = xml
        xmlinfo['documento'] = root
        indice = 0
        for doc in root:
            if doc.tag == '{http://www.sat.gob.mx/cfd/3}Complemento':
                break
            else:
                indice += 1
        for complemento_data in root[indice]:
            xmlinfo['complemento'] = complemento_data
        return xmlinfo


class GeneratorXmlThreeDotThree(AbstractGeneratorXml):

    def __init__(self, data):
        super(self.__class__, self).__init__(data)
        self.version = '3.3'
        self.algoritmoSha = SHA256
        self.__cadena_original = ''

    def get_datos(self,xml):
        self.__cadena_original = self.get_cadena_original(xml)
        xml_info = self.get_xml_info(xml)
        return {
            'cadena_original':str(self.__cadena_original),
            'serie': xml_info['documento'].attrib['Serie'],
            'fecha_emision': xml_info['documento'].attrib['Fecha'],
            'no_certificado': xml_info['documento'].attrib['NoCertificado'],
            'folio': xml_info['documento'].attrib['Folio'],
            'uuid': xml_info['complemento'].attrib['UUID'],
            'fecha_timbrado': xml_info['complemento'].attrib['FechaTimbrado'],
            'sello_emisor': xml_info['complemento'].attrib['SelloCFD'],
            'sello_sat': xml_info['complemento'].attrib['SelloSAT'],
            'no_certificado_sat': xml_info['complemento'].attrib['NoCertificadoSAT'],
        }

    def get_datos_test(self,xml):
        cadena_original = self.get_cadena_original(xml)
        xml_info = self.get_xml_info(xml)
        return {
            'cadena_original': str(cadena_original),
            'serie': xml_info['documento'].attrib['Serie'],
            'fecha_emision': xml_info['documento'].attrib['Fecha'],
            'no_certificado': xml_info['documento'].attrib['NoCertificado'],
            'folio': xml_info['documento'].attrib['Folio'],
            'uuid': '',
            'fecha_timbrado': '',
            'sello_emisor': '',
            'sello_sat': '',
            'no_certificado_sat': '',
        }

    def generate_xml(self):
        self.reset_dom()
        dom = self.dom.childNodes[ 0 ]
        # xmlns: cfdi = "http://www.sat.gob.mx/cfd/3"
        # xmlns: xsi = "http://www.w3.org/2001/XMLSchema-instance"
        # xmlns: cartaporte = "http://www.sat.gob.mx/CartaPorte"
        # xsi: schemaLocation = "http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd http://www.sat.gob.mx/CartaPorte http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte.xsd"
        if self.data.get('tipo_comprobante') == 4: #recibo donativo
            dom.setAttribute('xsi:schemaLocation',
                             'http://www.sat.gob.mx/cfd/3 ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd ' +
                             'http://www.sat.gob.mx/donat ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xsd')
            dom.setAttribute('xmlns:donat', 'http://www.sat.gob.mx/donat')
        elif self.tipo_objeto == TRASLADO:
            dom.setAttribute('xmlns:cfdi', 'http://www.sat.gob.mx/cfd/3')
            dom.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            dom.setAttribute('xmlns:cartaporte', 'http://www.sat.gob.mx/CartaPorte')
            dom.setAttribute('xsi:schemaLocation',
                             'http://www.sat.gob.mx/cfd/3 ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd ' +
                             'http://www.sat.gob.mx/CartaPorte ' +
                             'http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte.xsd')
        else:
            dom.setAttribute('xsi:schemaLocation',
                             'http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd http://www.sat.gob.mx/TimbreFiscalDigital http://www.sat.gob.mx/sitio_internet/cfd/timbrefiscaldigital/TimbreFiscalDigitalv11.xsd')
        dom.setAttribute('xmlns:tfd',"http://www.sat.gob.mx/TimbreFiscalDigital")
        dom.setAttribute('xmlns:implocal',"http://www.sat.gob.mx/implocal")
        dom.setAttribute('xmlns:notariospublicos',"http://www.sat.gob.mx/notariospublicos")
        dom.setAttribute('Version', self.global_data.get('version', ''))
        dom.setAttribute('Serie', self.data.get('serie', ''))
        dom.setAttribute('Folio', self.data.get('folio', ''))
        dom.setAttribute('Fecha', self.data.get('fecha'))
        dom.setAttribute('Sello', '')
        dom.setAttribute('NoCertificado', self.global_data.get('no_certificado'))
        dom.setAttribute('Certificado','')
        dom.setAttribute('TipoDeComprobante', self.tipo_objeto)
        dom.setAttribute('LugarExpedicion', self.data.get('codigo_postal', ''))
        if self.data.get('confirmacion'):
            if len(self.data.get('confirmacion', [])) == 5:
                dom.setAttribute('Confirmacion', self.data.get('confirmacion'))  # opcional
        dom.appendChild(self.get_emisor())
        dom.appendChild(self.get_receptor())

        if self.tipo_objeto == EGRESO:
            dom.appendChild(self.get_cfdi_relacionados())
        if self.tipo_objeto == INGRESO and self.complemento == COMPLEMENTO_CARTA_PORTE and self.data.get('tipo_relacion') == '05':
            # Agregar lo siguiente
            # 1.- Información en el campo TipoEstación de la sección Ubicación con el valor “02” (Intermedia), contenida en el catálogo del complemento Carta Porte, c_TipoEstacion, publicado en el portal del SAT.
            # 2.- Información en la sección TransporteFerroviario de la sección Mercancias.
            dom.appendChild(self.get_cfdi_relacionados())
        elif len(self.data.get('cfdi_relacionados', [])) > 0:
            dom.appendChild(self.get_cfdi_relacionados())

        if (self.tipo_objeto == INGRESO) or (self.tipo_objeto == EGRESO and not self.global_data.get('concepto_fijo')):
            dom.setAttribute('FormaPago', self.data.get('forma_pago'))
            dom.setAttribute('CondicionesDePago', self.data.get('condicion_pago'))
            # dom.setAttribute('Descuento', '0.00') # 'Opcional'
            dom.setAttribute('MetodoPago', self.data.get('metodo_pago'))
            # Campos que solo en ingreso no son fijos
            dom.setAttribute('Moneda', self.data.get('moneda'))  # 'Peso Mexicano'
            # 'Opcional solo cuando moneda es distinta de MXN'
            dom.setAttribute('TipoCambio', '1' if self.data.get('moneda') == 'MXN' else self.data.get('tipo_cambio'))
            dom.setAttribute('SubTotal', self.data.get('importe', ''))
            dom.setAttribute('Total', self.data.get('importe_total', ''))
            conceptos_list = self.data.get('conceptos', [])
            if len(conceptos_list) > 0:
                conceptos = self.dom.createElement('cfdi:Conceptos')
                for concepto in conceptos_list:
                    conceptos.appendChild(self.get_conceptos(concepto))
                dom.appendChild(conceptos)
            if self.data.get('iva') != '0' and self.data.get('iva') != 0 and self.data.get('tipo_comprobante') != 3:
                dom.appendChild(self.get_impuestos())
        elif self.tipo_objeto == PAGO:
            dom.setAttribute('SubTotal','0')
            dom.setAttribute('Moneda','XXX')
            dom.setAttribute('Total','0')
            dom.appendChild(self.get_concepto_fijo())
        elif self.tipo_objeto == TRASLADO:
            dom.setAttribute('SubTotal','0')
            dom.setAttribute('Moneda','XXX')
            dom.setAttribute('Total','0')
            conceptos_list = self.data.get('conceptos', [])
            if len(conceptos_list) > 0:
                conceptos = self.dom.createElement('cfdi:Conceptos')
                for concepto in conceptos_list:
                    conceptos.appendChild(self.get_conceptos(concepto))
                dom.appendChild(conceptos)
        elif self.tipo_objeto == EGRESO and self.global_data.get('concepto_fijo'):
            dom.setAttribute('FormaPago',self.data.get('forma_pago'))
            dom.setAttribute('CondicionesDePago', self.data.get('condicion_pago'))
            dom.setAttribute('MetodoPago', self.data.get('metodo_pago'))
            dom.setAttribute('Moneda', self.data.get('moneda'))  # 'Peso Mexicano'
            # 'Opcional solo cuando moneda es distinta de MXN'
            dom.setAttribute('TipoCambio', '1' if self.data.get('moneda') == 'MXN' else self.data.get('tipo_cambio'))
            dom.setAttribute('SubTotal',str(self.data.get('total')))
            dom.setAttribute('Total',str(self.data.get('total')))
            dom.appendChild(self.get_concepto_fijo())
            dom.appendChild(self.get_impuestos())
        if self.data.get('tipo_comprobante') in [4, 5] or self.complemento in [COMPLEMENTO_PAGO, COMPLEMENTO_CARTA_PORTE]:
            dom.appendChild(self.get_complementos())
        self.dom = dom
        return self.dom

    def get_cfdi_relacionados(self):
        try:
            relacionados = self.dom.createElement('cfdi:CfdiRelacionados')
            if self.tipo_objeto == INGRESO:
                relacionados.setAttribute('TipoRelacion', self.data.get('tipo_relacion'))
            elif self.tipo_objeto == PAGO:
                relacionados.setAttribute('TipoRelacion','04')  # Sustitución de CFDI previos
            elif self.tipo_objeto == EGRESO:
                relacionados.setAttribute('TipoRelacion', self.data.get('tipo_relacion'))
            cfdirelacionados = self.data.get('cfdi_relacionados')
            for uuid_cfdi in cfdirelacionados:
                relacionado = self.dom.createElement('cfdi:CfdiRelacionado')
                relacionado.setAttribute('UUID', uuid_cfdi)
                relacionados.appendChild(relacionado)
            return relacionados
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_emisor(self):
        try:
            emisor = self.dom.createElement('cfdi:Emisor')
            emisor.setAttribute('Rfc', self.data.get('emisor_rfc'))
            emisor.setAttribute('Nombre', replace(self.data.get('emisor_nombre', '')).strip())
            emisor.setAttribute('RegimenFiscal', self.data.get('regimen_fiscal'))
            return emisor
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_receptor(self):
        try:
            receptor = self.dom.createElement('cfdi:Receptor')
            receptor.setAttribute('Rfc', self.data.get('receptor_rfc'))
            receptor.setAttribute('Nombre',replace(self.data.get('receptor_nombre', '')).strip())
            if self.data.get('receptor_residencia_fiscal') != 'MEX':
                receptor.setAttribute('ResidenciaFiscal',self.data.get('receptor_residencia_fiscal'))
                receptor.setAttribute('NumRegIdTrib',self.data.get('receptor_num_reg_id_trib'))
            if self.tipo_objeto == TRASLADO and self.data.get('uso_cfdi') != 'P01':
                raise Exception('El campo Uso CFDI debe contener el valor P01 - Por Definir')
            receptor.setAttribute('UsoCFDI', self.data.get('uso_cfdi'))
            return receptor
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_concepto_fijo(self):
        try:
            conceptos = self.dom.createElement('cfdi:Conceptos')
            concepto = self.dom.createElement('cfdi:Concepto')
            concepto.setAttribute('ClaveProdServ','84111506')
            concepto.setAttribute('Cantidad','1')
            concepto.setAttribute('ClaveUnidad','ACT')
            if self.tipo_objeto == PAGO:
                concepto.setAttribute('Descripcion','Pago')
                concepto.setAttribute('ValorUnitario','0')
                concepto.setAttribute('Importe','0')
            elif self.tipo_objeto == EGRESO:
                if self.data.get('descripcion', '') != '':
                    concepto.setAttribute('Descripcion',replace(self.data.get('descripcion', '').strip()))
                else:
                    raise Exception('Se debe especificar una descripción para poder timbrar')
                concepto.setAttribute('ValorUnitario',str(self.data.get('total')))
                concepto.setAttribute('Importe',str(self.data.get('total')))
            conceptos.appendChild(concepto)
            return conceptos
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_impuestos(self):
        try:
            impuestos = self.dom.createElement('cfdi:Impuestos')
            if self.data.get('tipo_comprobante') not in [ 5,6 ]:
                if self.data.get('iva') != '0' and self.data.get('iva') != 0:
                    impuestos.setAttribute('TotalImpuestosTrasladados',str(self.data.get('iva')))
                    impuestos.appendChild(self.get_traslados())
                else:
                    impuestos.setAttribute('TotalImpuestosTrasladados','0')
                    impuestos.appendChild(self.get_traslados())
            return impuestos
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_traslados(self):
        traslados = self.dom.createElement('cfdi:Traslados')
        traslado = self.dom.createElement('cfdi:Traslado')
        traslado.setAttribute('Impuesto','002')
        if self.data.get('iva') != '0' and self.data.get('iva') != 0:
            traslado.setAttribute('TipoFactor','Tasa')
            traslado.setAttribute('TasaOCuota',str(self.data.get('porcentaje')))
            traslado.setAttribute('Importe',str(self.data.get('iva')))
        else:
            traslado.setAttribute('TipoFactor','Exento')
        traslados.appendChild(traslado)
        return traslados

    def get_retenciones(self):
        retenciones = self.dom.createElement('cfdi:Retenciones')
        retencion = self.dom.createElement('cfdi:Retencion')
        retencion.setAttribute('Impuesto','002')
        if self.data.get('iva') != '0' and self.data.get('iva') != 0:
            retencion.setAttribute('Importe',str(self.data.get('iva')))
        else:
            retencion.setAttribute('Importe','0')
        retenciones.appendChild(retencion)
        return retenciones

    def get_complementos(self):
        try:
            complemento = self.dom.createElement('cfdi:Complemento')
            if self.data.get('tipo_comprobante') == 4:
                complemento.appendChild(self.get_donatarias())
            elif self.data.get('tipo_comprobante') == 5:
                complemento.appendChild(self.get_pagos())
            elif self.complemento == COMPLEMENTO_CARTA_PORTE:
                complemento.appendChild(self.get_complemento_cartaporte())
            return complemento
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_donatarias(self):
        try:
            donataria = self.dom.createElement('donat:Donatarias')
            donataria.setAttribute('xmlns:donat','http://www.sat.gob.mx/donat')
            donataria.setAttribute('xsi:schemaLocation',
                                   'http://www.sat.gob.mx/cfd/3 ' +
                                   'http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd ' +
                                   'http://www.sat.gob.mx/donat ' +
                                   'http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xsd')
            donataria.setAttribute('version','1.1')
            donataria.setAttribute('noAutorizacion', self.data.get('donataria_no_autorizacion'))
            donataria.setAttribute('fechaAutorizacion', self.data.get('donataria_fecha_autorizacion'))
            donataria.setAttribute('leyenda', self.data.get('donataria_leyenda'))
            return donataria
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_pagos(self):
        try:
            pagos = self.dom.createElement('pago10:Pagos')
            pagos.setAttribute('Version','1.0')
            pagos.setAttribute('xmlns:catCFDI','http://www.sat.gob.mx/sitio_internet/cfd/catalogos')
            pagos.setAttribute('xmlns:catPagos','http://www.sat.gob.mx/sitio_internet/cfd/catalogos/Pagos')
            pagos.setAttribute('xmlns:pago10','http://www.sat.gob.mx/Pagos')
            pagos.setAttribute('xmlns:tdCFDI','http://www.sat.gob.mx/sitio_internet/cfd/tipoDatos/tdCFDI')
            pagos.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
            pagos.setAttribute('xsi:schemaLocation',
                               'http://www.sat.gob.mx/Pagos http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos10.xsd http://www.sat.gob.mx/sitio_internet/cfd/catalogos/catCFDI.xsd http://www.sat.gob.mx/sitio_internet/cfd/tipoDatos/tdCFDI http://www.sat.gob.mx/sitio_internet/cfd/catalogos/tdCFDI.xsd http://www.sat.gob.mx/sitio_internet/cfd/catalogos/Pagos http://www.sat.gob.mx/sitio_internet/cfd/catalogos/Pagos/catPagos.xsd')
            pago = self.dom.createElement('pago10:Pago')
            pago.setAttribute('FechaPago', self.data.get('fecha_pago') + 'T00:00:00')
            if self.data.get('forma_pago') == '99':
                raise Exception('La forma de pago no puede ser "Por Definir".')
            pago.setAttribute('FormaDePagoP', self.data.get('forma_pago'))
            pago.setAttribute('MonedaP', self.data.get('moneda_pago'))
            if self.data.get('moneda_pago') != 'MXN':
                pago.setAttribute('TipoCambioP', '1' if self.data.get('moneda_pago') == 'MXN' else self.data.get('tipo_cambio_pago'))
            pago.setAttribute('Monto', str(self.data.get('monto')))
            if self.data.get('numero_operacion') != '':
                pago.setAttribute('NumOperacion',self.data.get('numero_operacion'))
            if self.data.get('bancarizado'):
                if self.data.get('patron_cuenta_ordenante') and self.data.get('patron_cuenta_ordenante') != '':
                    if self.data.get('banco_ordenante'):
                        pago.setAttribute('RfcEmisorCtaOrd',self.data.get('emisor_cuenta_ordenante_rfc'))
                        if self.data.get('emisor_cuenta_ordenante_rfc') == 'XEXX010101000':
                            pago.setAttribute('NomBancoOrdExt',self.data.get('emisor_cuenta_ordenante_nombre'))
                    pago.setAttribute('CtaOrdenante',self.data.get('emisor_cuenta_ordenante'))
                if self.data.get('forma_pago') != '06':
                    if self.data.get('emisor_cuenta_beneficiaria_rfc'):
                        pago.setAttribute('RfcEmisorCtaBen',self.data.get('emisor_cuenta_beneficiaria_rfc'))
                    pago.setAttribute('CtaBeneficiario',self.data.get('emisor_cuenta_beneficiaria'))

            doctos = self.data.get('documentos_relacionados')
            for cfdi in doctos:
                docto = self.dom.createElement('pago10:DoctoRelacionado')
                docto.setAttribute('IdDocumento', cfdi.get('uuid'))
                docto.setAttribute('Serie', cfdi.get('serie'))
                docto.setAttribute('Folio', cfdi.get('folio'))
                docto.setAttribute('MonedaDR', cfdi.get('moneda'))
                docto.setAttribute('MetodoDePagoDR', 'PPD')
                docto.setAttribute('NumParcialidad', str(cfdi.get('num_parcialidad')))
                docto.setAttribute('ImpSaldoAnt', str(cfdi.get('imp_saldo_ant')))
                docto.setAttribute('ImpPagado', str(cfdi.get('imp_pagado')))
                docto.setAttribute('ImpSaldoInsoluto', str(cfdi.get('imp_saldo_insoluto')))
                pago.appendChild(docto)
            pagos.appendChild(pago)
            return pagos
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_addenda(self):
        try:
            addenda = self.dom.createElement('cfdi:Addenda')
            return addenda
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_conceptos(self, concepto):
        try:
            cfdi_concepto = self.dom.createElement('cfdi:Concepto')
            cfdi_concepto.setAttribute('ClaveProdServ', concepto.get('clave_prod_serv'))
            if concepto.get('no_identificacion'):
                cfdi_concepto.setAttribute('NoIdentificacion',concepto.get('no_identificacion'))
            cfdi_concepto.setAttribute('Cantidad', str(concepto.get('cantidad')))
            cfdi_concepto.setAttribute('ClaveUnidad', concepto.get('clave_unidad'))
            if concepto.get('unidad'):
                cfdi_concepto.setAttribute('Unidad',concepto.get('unidad'))
            if concepto.get('descripcion', '') != '':
                cfdi_concepto.setAttribute('Descripcion',replace(concepto.get('descripcion', '').strip()))
            else:
                raise Exception('Se debe especificar una descripción para poder timbrar y posteriormente crear una poliza.')
            cfdi_concepto.setAttribute('ValorUnitario', str(concepto.get('valor_unitario')))
            cfdi_concepto.setAttribute('Importe', str(concepto.get('importe')))
            if self.tipo_objeto != TRASLADO and self.complemento != COMPLEMENTO_CARTA_PORTE:
                cfdi_concepto.appendChild(self.get_impuestos_concepto(concepto))
            if concepto.get('informacion_aduanera'):
                cfdi_concepto.appendChild(self.get_informacion_aduanera(concepto.get('informacion_aduanera')))
            if concepto.get('cuenta_predial'):
                cfdi_concepto.appendChild(self.get_cuenta_predial(concepto.get('cuenta_predial')))
            return cfdi_concepto
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_impuestos_concepto(self,concepto):
        impuestos = self.dom.createElement('cfdi:Impuestos')
        impuestos.appendChild(self.get_traslados_retencion_concepto(concepto))
        return impuestos

    def get_traslados_retencion_concepto(self, concepto, retenciones = False):
        trasretcons = self.dom.createElement('cfdi:Traslados')
        trasretcon = self.dom.createElement('cfdi:Traslado')
        if retenciones:
            trasretcons = self.dom.createElement('cfdi:Retenciones')
            trasretcon = self.dom.createElement('cfdi:Retencion')
        trasretcon.setAttribute('Impuesto','002')  # 'IVA'
        if concepto.get('iva') != '0' and concepto.get('iva') != 0:
            trasretcon.setAttribute('TipoFactor','Tasa')
            trasretcon.setAttribute('Base', str(concepto.get('base')))
            trasretcon.setAttribute('TasaOCuota', str(concepto.get('porcentaje')))
            trasretcon.setAttribute('Importe', str(concepto.get('iva')))
        else:
            trasretcon.setAttribute('TipoFactor','Exento')
            trasretcon.setAttribute('Base', str(concepto.get('importe')))
        trasretcons.appendChild(trasretcon)
        return trasretcons

    def get_informacion_aduanera(self, informacion_aduanera):
        try:
            informacionaduanera = self.dom.createElement('cfdi:InformacionAduanera ')
            informacionaduanera.setAttribute('NumeroPedimento', informacion_aduanera.numeroPedimento)
            return informacionaduanera
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_cuenta_predial(self, cuenta_predial):
        try:
            cuentapredial = self.dom.createElement('cfdi:CuentaPredial ')
            cuentapredial.setAttribute('Numero', cuenta_predial)
            return cuentapredial
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_parte(self, ingreso_parte):
        try:
            parte = self.dom.createElement('cfdi:CfdiParte')
            parte.setAttribute('ClaveProdServ',ingreso_parte.claveProdServ)
            if ingreso_parte.noIdentificacion:
                parte.setAttribute('NoIdentificacion',ingreso_parte.noIdentificacion)
            parte.setAttribute('Cantidad',str(ingreso_parte.cantidad))
            if len(ingreso_parte.descripcion) > 0:
                parte.setAttribute('Descripcion',replace(ingreso_parte.descripcion.strip()))
            else:
                parte.setAttribute('Descripcion','N/A')
            parte.setAttribute('ValorUnitario',str(ingreso_parte.importe))
            parte.setAttribute('Importe',str(ingreso_parte.importe))
            if ingreso_parte.informacionAduanera:
                parte.appendChild(self.get_informacion_aduanera(ingreso_parte.informacionAduanera))  # No se usara
            return parte
        except Exception as e:
            raise Exception("Ocurrio un error. Error::: " + str(e))

    def get_complemento_cartaporte(self):
        try:
            cartaporte = self.dom.createElement('cartaporte:CartaPorte')
            cartaporte.setAttribute('Version', '1.0')
            cartaporte.setAttribute('TranspInternac', self.data.get('TranspInternac'))
            if self.data.get('TranspInternac') == 'Si':
                if self.data.get('EntradaSalidaMerc', '') not in ['Entrada', 'Salida']:
                    raise Exception('El valor del campo EntradaSalidaMerc debe ser: Entrada ó Salida')
                cartaporte.setAttribute('EntradaSalidaMerc', self.data.get('EntradaSalidaMerc'))
                cartaporte.setAttribute('ViaEntradaSalida', self.data.get('ViaEntradaSalida'))

            cartaporte_ubicaciones = self.dom.createElement('cartaporte:Ubicaciones')
            ubicaciones = self.data.get('ubicaciones', [])
            total_distancia_recorrida = 0
            for ubicacion_data in ubicaciones:
                cartaporte_ubicacion = self.dom.createElement('cartaporte:Ubicacion')
                if ubicacion_data.get('type') == 'origen':
                    cartaporte_ubicacion_origen = self.dom.createElement('cartaporte:Origen')
                    cartaporte_ubicacion_origen.setAttribute('RFCRemitente', ubicacion_data.get('RFCRemitente'))
                    cartaporte_ubicacion_origen.setAttribute('NombreRemitente', ubicacion_data.get('NombreRemitente'))
                    cartaporte_ubicacion_origen.setAttribute('FechaHoraSalida', ubicacion_data.get('FechaHoraSalida'))
                    cartaporte_ubicacion.appendChild(cartaporte_ubicacion_origen)
                elif ubicacion_data.get('type') == 'destino':
                    cartaporte_ubicacion.setAttribute('DistanciaRecorrida', str(ubicacion_data.get('DistanciaRecorrida')))
                    cartaporte_ubicacion_destino = self.dom.createElement('cartaporte:Destino')
                    cartaporte_ubicacion_destino.setAttribute('RFCDestinatario', ubicacion_data.get('RFCDestinatario'))
                    cartaporte_ubicacion_destino.setAttribute('NombreDestinatario', ubicacion_data.get('NombreDestinatario'))
                    cartaporte_ubicacion_destino.setAttribute('FechaHoraProgLlegada', ubicacion_data.get('FechaHoraProgLlegada'))
                    cartaporte_ubicacion.appendChild(cartaporte_ubicacion_destino)
                    total_distancia_recorrida += float(ubicacion_data.get('DistanciaRecorrida'))

                cartaporte_ubicacion_domicilio = self.dom.createElement('cartaporte:Domicilio')
                cartaporte_ubicacion_domicilio.setAttribute('Calle', ubicacion_data.get('Calle'))
                if ubicacion_data.get('NumeroExterior') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('NumeroExterior', ubicacion_data.get('NumeroExterior'))
                if ubicacion_data.get('Colonia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Colonia', ubicacion_data.get('Colonia'))
                if ubicacion_data.get('Localidad') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Localidad', ubicacion_data.get('Localidad'))
                if ubicacion_data.get('Referencia') != '':
                    cartaporte_ubicacion_domicilio.setAttribute('Referencia', ubicacion_data.get('Referencia'))
                cartaporte_ubicacion_domicilio.setAttribute('Municipio', ubicacion_data.get('Municipio'))
                cartaporte_ubicacion_domicilio.setAttribute('Estado', ubicacion_data.get('Estado'))
                cartaporte_ubicacion_domicilio.setAttribute('Pais', ubicacion_data.get('Pais'))
                cartaporte_ubicacion_domicilio.setAttribute('CodigoPostal', ubicacion_data.get('CodigoPostal'))
                cartaporte_ubicacion.appendChild(cartaporte_ubicacion_domicilio)
                cartaporte_ubicaciones.appendChild(cartaporte_ubicacion)
            cartaporte.appendChild(cartaporte_ubicaciones)
            if self.tipo_transporte in ['AutotransporteFederal', 'TransporteFerroviario']:
                cartaporte.setAttribute('TotalDistRec', str(total_distancia_recorrida))

            cartaporte_mercancias = self.dom.createElement('cartaporte:Mercancias')
            mercancias = self.data.get('mercancias', [])
            num_total_mercancias = 0
            for mercancia_data in mercancias:
                cartaporte_mercancia = self.dom.createElement('cartaporte:Mercancia')
                cartaporte_mercancia.setAttribute('PesoEnKg', mercancia_data.get('PesoEnKg'))
                cartaporte_mercancia.setAttribute('ValorMercancia', mercancia_data.get('ValorMercancia'))
                cartaporte_mercancia.setAttribute('Moneda', mercancia_data.get('Moneda'))
                cartaporte_mercancias.appendChild(cartaporte_mercancia)
                num_total_mercancias += 1

            cartaporte_mercancias.setAttribute('NumTotalMercancias', str(num_total_mercancias))
            cartaporte.appendChild(cartaporte_mercancias)

            if self.tipo_transporte not in ['AutotransporteFederal', 'TransporteMaritimo', 'TransporteAereo', 'TransporteFerroviario']:
                raise Exception('Se debe registrar un tipo de transporte')
            transporte_data = self.data.get('transporte')
            if self.tipo_transporte == 'AutotransporteFederal':
                cartaporte_tipo_transporte = self.dom.createElement('cartaporte:AutotransporteFederal')
                cartaporte_tipo_transporte.setAttribute('PermSCT', transporte_data.get('PermSCT'))
                cartaporte_tipo_transporte.setAttribute('NumPermisoSCT', transporte_data.get('NumPermisoSCT'))
                cartaporte_tipo_transporte.setAttribute('NombreAseg', transporte_data.get('NombreAseg'))
                cartaporte_tipo_transporte.setAttribute('NumPolizaSeguro', transporte_data.get('NumPolizaSeguro'))

                cartaporte_identificacion_vehicular = self.dom.createElement('cartaporte:IdentificacionVehicular')
                cartaporte_identificacion_vehicular.setAttribute('ConfigVehicular', transporte_data.get('ConfigVehicular'))
                cartaporte_identificacion_vehicular.setAttribute('PlacaVM', transporte_data.get('PlacaVM'))
                cartaporte_identificacion_vehicular.setAttribute('AnioModeloVM', transporte_data.get('AnioModeloVM'))
                cartaporte_tipo_transporte.appendChild(cartaporte_identificacion_vehicular)

                remolques = transporte_data.get('remolques', [])
                if len(remolques) > 0:
                    cartaporte_remolques = self.dom.createElement('cartaporte:Remolques')
                    for remolque_data in remolques:
                        cartaporte_remolque = self.dom.createElement('cartaporte:Remolque')
                        cartaporte_remolque.setAttribute('SubTipoRem', remolque_data.get('SubTipoRem'))
                        cartaporte_remolque.setAttribute('Placa', remolque_data.get('Placa'))
                        cartaporte_remolques.appendChild(cartaporte_remolque)
                    cartaporte_tipo_transporte.appendChild(cartaporte_remolques)

                cartaporte_mercancias.appendChild(cartaporte_tipo_transporte)

            cartaporte_figura_transporte = self.dom.createElement('cartaporte:FiguraTransporte')
            cartaporte_figura_transporte.setAttribute('CveTransporte', transporte_data.get('CveTransporte'))

            operadores = transporte_data.get('operadores', [])
            cartaporte_operadores = self.dom.createElement('cartaporte:Operadores')
            for operador_data in operadores:
                cartaporte_operador = self.dom.createElement('cartaporte:Operador')
                cartaporte_operador.setAttribute('RFCOperador', operador_data.get('RFCOperador'))
                cartaporte_operador.setAttribute('NumLicencia', operador_data.get('NumLicencia'))
                cartaporte_operador.setAttribute('NombreOperador', operador_data.get('NombreOperador'))

                if operador_data.get('Calle', '') != '':
                    cartaporte_operador_domicilio = self.dom.createElement('cartaporte:Domicilio')
                    cartaporte_operador_domicilio.setAttribute('Calle', operador_data.get('Calle'))
                    if operador_data.get('NumeroExterior', '') != '':
                        cartaporte_operador_domicilio.setAttribute('NumeroExterior', operador_data.get('NumeroExterior'))
                    if operador_data.get('Colonia', '') != '':
                        cartaporte_operador_domicilio.setAttribute('Colonia', operador_data.get('Colonia'))
                    cartaporte_operador_domicilio.setAttribute('Localidad', operador_data.get('Localidad'))
                    if operador_data.get('Referencia', '') != '':
                        cartaporte_operador_domicilio.setAttribute('Referencia', operador_data.get('Referencia'))
                    cartaporte_operador_domicilio.setAttribute('Municipio', operador_data.get('Municipio'))
                    cartaporte_operador_domicilio.setAttribute('Estado', operador_data.get('Estado'))
                    cartaporte_operador_domicilio.setAttribute('Pais', operador_data.get('Pais'))
                    cartaporte_operador_domicilio.setAttribute('CodigoPostal', operador_data.get('CodigoPostal'))
                    cartaporte_operador.appendChild(cartaporte_operador_domicilio)

                cartaporte_operadores.appendChild(cartaporte_operador)
            cartaporte_figura_transporte.appendChild(cartaporte_operadores)
            cartaporte.appendChild(cartaporte_figura_transporte)

            return cartaporte
        except Exception as e:
            raise Exception("Ocurrio un error al generar el complemento cartaporte. Error::: " + str(e))
