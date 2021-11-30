class DropOffType:
    REGULAR_PICKUP = 'REGULAR_PICKUP'
    REQUEST_COURIER = 'REQUEST_COURIER'

class PaymentInfo:
    PAYMENT_CFR = 'CFR'
    PAYMENT_CIF = 'CIF'
    PAYMENT_CIP = 'CIP'
    PAYMENT_CPT = 'CPT'
    PAYMENT_DAF = 'DAF'
    PAYMENT_DDP = 'DPP'
    PAYMENT_DDU = 'DDU'
    PAYMENT_DAP = 'DAP'
    PAYMENT_DEQ = 'DEQ'
    PAYMENT_DES = 'DES'
    PAYMENT_EXW = 'EXW'
    PAYMENT_FAS = 'FAS'
    PAYMENT_FCA = 'FCA'
    PAYMENT_FOB = 'FOB'

class ContentType:
    DOCUMENTS = 'DOCUMENTS'
    NON_DOCUMENTS = 'NON_DOCUMENTS'

class Measurement:
    MEASUREMENT_METRIC = 'SI'
    MEASUREMENT_US = 'SU'

class OnDemandDelivery:
    SERVICE_POINT = 'TV'
    LEAVE_AT_NEIGHBOUR = 'SW'
    SIGNATURE_NEEDED = 'SX'

class RegistrationNumberType:
    VAT = 'VAT'
    EIN = 'EIN'
    GST = 'GST'
    SSN = 'SSN'
    EOR = 'EOR'
    DUN = 'DUN'
    FED = 'FED'
    STA = 'STA'
    CNP = 'CNP'
    IE = 'IE'
    INN = 'INN'
    KPP = 'KPP'
    OGR = 'OGR'
    OKP = 'OKP'
    MRN = 'MRN'
    OSR = 'OSR'

class NotificationMethods:
    EMAIL = 'EMAIL'


EU_COUNTRIES = {
    'BE' : 'Belgium',
    'BG' : 'Bulgaria',
    'CZ' : 'Czechia',
    'DK' : 'Denmark',
    'DE' : 'Germany',
    'EE' : 'Estonia',
    'IE' : 'Ireland',
    'EL' : 'Greece',
    'ES' : 'Spain',
    'FR' : 'France',
    'HR' : 'Croatia',
    'IT' : 'Italy',
    'CY' : 'Cyprus',
    'LV' : 'Latvia',
    'LT' : 'Lithuania',
    'LU' : 'Luxembourg',
    'HU' :' Hungary',
    'MT' : 'Malta',
    'NL' : 'Netherlands',
    'AT' : 'Austria',
    'PL' : 'Poland',
    'PT' : 'Portugal',
    'RO' : 'Romania',
    'SI' : 'Slovenia',
    'FI' : 'Finland',
    'SE': 'Sweden'
}


PRODUCTS_GLOBAL = {
    'K' : 'Express 9:00 - Documents',
    'E' : 'Express 9:00 - NonDocuments (outside EU)',

    'L' : 'Express 10:30 - Documents (USA)',
    'M' : 'Express 10:30 - NonDocuments (USA)',

    'T' : 'Express 12:00 - Documents',
    'Y' : 'Express 12:00 - NonDocuments (outside EU)',

    'U' : 'Express Worldwide (EU)',
    'D' : 'Express Worldwide - Documents (outside EU)',
    'P' : 'Express Worldwide - NonDocuments (outside EU)',

    'I' : 'Express 9:00  (Domestic)',
    '1' : 'Express 12:00 (Domestic)',
    'N' : 'Express 18:00 (Domestic)',

    'W' : 'Economy Select - Documents (EU)',
    'H' : 'Economy Select - NonDocuments (outside EU)',

    'X' : 'Express Enveloppe - Documents under 0.3kg',
}