LIBRETRANS_HEADER = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Magic Google Chrome UA
GOOGLE_USER_AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}

# Google Translate servers
# Copied from https://github.com/ssut/py-googletrans/pull/255/files
GOOGLE_TRANSLATE_ENDPOINTS = ['translate.google.ac', 'translate.google.ad', 'translate.google.ae',
                        'translate.google.al', 'translate.google.am', 'translate.google.as',
                        'translate.google.at', 'translate.google.az', 'translate.google.ba',
                        'translate.google.com.ai', 'translate.google.com.ar', 'translate.google.com.au',
                        'translate.google.com.bd', 'translate.google.com.bh', 'translate.google.com.bn',
                        'translate.google.com.bo', 'translate.google.com.br', 'translate.google.com.bz',
                        'translate.google.com.co', 'translate.google.com.cu', 'translate.google.com.cy',
                        'translate.google.com.do', 'translate.google.com.ec', 'translate.google.com.eg',
                        'translate.google.com.et', 'translate.google.com.fj', 'translate.google.com.gh',
                        'translate.google.com.gi', 'translate.google.com.gt', 'translate.google.com.hk',
                        'translate.google.com.jm', 'translate.google.com.kh', 'translate.google.com.kw',
                        'translate.google.com.lb', 'translate.google.com.ly', 'translate.google.com.mm',
                        'translate.google.com.mt', 'translate.google.com.mx', 'translate.google.com.my',
                        'translate.google.com.na', 'translate.google.com.ng', 'translate.google.com.ni',
                        'translate.google.com.np', 'translate.google.com.om', 'translate.google.com.pa',
                        'translate.google.com.pe', 'translate.google.com.pg', 'translate.google.com.ph',
                        'translate.google.com.pk', 'translate.google.com.pr', 'translate.google.com.py',
                        'translate.google.com.qa', 'translate.google.com.sa', 'translate.google.com.sb',
                        'translate.google.com.sg', 'translate.google.com.sl', 'translate.google.com.sv',
                        'translate.google.com.tj', 'translate.google.com.tr', 'translate.google.com.tw',
                        'translate.google.com.ua', 'translate.google.com.uy', 'translate.google.com.vc',
                        'translate.google.com.vn', 'translate.google.com', 'translate.google.cv',
                        'translate.google.cz', 'translate.google.de', 'translate.google.dj',
                        'translate.google.dk', 'translate.google.dm', 'translate.google.dz',
                        'translate.google.st', 'translate.google.td', 'translate.google.tg',
                        'translate.google.tk', 'translate.google.tl', 'translate.google.tm',
                        'translate.google.tn', 'translate.google.to', 'translate.google.tt',
                        'translate.google.us', 'translate.google.vg', 'translate.google.vu',
                        'translate.google.ws']