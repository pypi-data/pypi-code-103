from .StatusMessage import StatusMessage


class StandardMessages:

    """
    This class provides easy access to the standard set of ELG status messages that are provided by default by
    the platform and should be fully translated in the ELG user interface. If you use codes other than these
    standard ones in your services then you should also try to contribute translations of your messages into as
    many languages as possible for the benefit of other ELG users.

    Implementation note: This class is auto-generated from elg-messages.properties - to add new message codes you
    should edit the property files, then run /utils/generate_standard_messages.py. Do not edit this class directly.
    """

    @classmethod
    def generate_elg_request_invalid(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.invalid"""
        code = "elg.request.invalid"
        text = {"en": "Invalid request message", "es": "Mensaje de petici\u00f3n inv\u00e1lido"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_missing(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.missing"""
        code = "elg.request.missing"
        text = {"en": "No request provided in message", "es": "Ninguna petici\u00f3n provista en el mensaje"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_type_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.type.unsupported"""
        code = "elg.request.type.unsupported"
        text = {
            "en": "Request type {0} not supported by this service",
            "es": "Tipo de petici\u00f3n {0} no soportada por este servicio",
        }
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_property_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.property.unsupported"""
        code = "elg.request.property.unsupported"
        text = {"en": "Unsupported property {0} in request", "es": "Propiedad no soportada {0} en la petici\u00f3n"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_too_large(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.too.large"""
        code = "elg.request.too.large"
        text = {"en": "Request size too large", "es": "Tama\u00f1o de petici\u00f3n demasiado grande"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_text_mimetype_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.text.mimeType.unsupported"""
        code = "elg.request.text.mimeType.unsupported"
        text = {
            "en": "MIME type {0} not supported by this service",
            "es": "Tipo MIME {0} no soportado por este servicio",
        }
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_audio_format_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.audio.format.unsupported"""
        code = "elg.request.audio.format.unsupported"
        text = {
            "en": "Audio format {0} not supported by this service",
            "es": "Formato de audio {0} no soportado por este servicio",
        }
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_audio_samplerate_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.audio.sampleRate.unsupported"""
        code = "elg.request.audio.sampleRate.unsupported"
        text = {
            "en": "Audio sample rate {0} not supported by this service",
            "es": "Tasa de sampleo de audio {0} no soportado por este servicio",
        }
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_request_structuredtext_property_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.request.structuredText.property.unsupported"""
        code = "elg.request.structuredText.property.unsupported"
        text = {
            "en": 'Unsupported property {0} in "texts" of structuredText request',
            "es": 'Propiedad no soportada {0} en "texts" de la petici\u00f3n structuredText',
        }
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_response_property_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.response.property.unsupported"""
        code = "elg.response.property.unsupported"
        text = {"en": "Unsupported property {0} in response", "es": "Propiedad no soportada {0} en la respuesta"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_response_texts_property_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.response.texts.property.unsupported"""
        code = "elg.response.texts.property.unsupported"
        text = {
            "en": 'Unsupported property {0} in "texts" of texts response',
            "es": 'Propiedad no soportada {0} en "texts" de la respuesta de textos',
        }
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_response_classification_property_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.response.classification.property.unsupported"""
        code = "elg.response.classification.property.unsupported"
        text = {
            "en": 'Unsupported property {0} in "classes" of classification response',
            "es": 'Propiedad no soportada {0} en "classes" de la respuesta de clasificaci\u00f3n',
        }
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_response_invalid(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.response.invalid"""
        code = "elg.response.invalid"
        text = {"en": "Invalid response message", "es": "Mensaje de respuesta inv\u00e1lido"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_response_type_unsupported(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.response.type.unsupported"""
        code = "elg.response.type.unsupported"
        text = {"en": "Response type {0} not supported", "es": "Tipo de respuesta {0} no soportada"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_service_not_found(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.service.not.found"""
        code = "elg.service.not.found"
        text = {"en": "Service {0} not found", "es": "Servicio {0} no se encontr\u00f3"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)

    @classmethod
    def generate_elg_service_internalerror(cls, params=[], detail={}, lang="en"):
        """Generate StatusMessage for code: elg.service.internalError"""
        code = "elg.service.internalError"
        text = {"en": "Internal error during processing: {0}", "es": "Error interno durante el procesamiento: {0}"}
        return StatusMessage(code=code, text=text[lang], params=params, detail=detail)
