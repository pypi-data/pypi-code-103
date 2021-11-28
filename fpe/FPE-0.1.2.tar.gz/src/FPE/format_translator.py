from FPE import Format
from numpy import arange

RADIX_DEFAULT = 10

dates = [
    '0101', '0201', '0301', '0401', '0501', '0601', '0701',
    '0801', '0901', '1001', '1101', '1201', '1301', '1401',
    '1501', '1601', '1701', '1801', '1901', '2001', '2101',
    '2201', '2301', '2401', '2501', '2601', '2701', '2801', 
    '2901', '3001', '3101', '0102', '0202', '0302', '0402', 
    '0502', '0602', '0702', '0802', '0902', '1002', '1102', 
    '1202', '1302', '1402', '1502', '1602', '1702', '1802', 
    '1902', '2002', '2102', '2202', '2302', '2402', '2502', 
    '2602', '2702', '2802', '0103', '0203', '0303', '0403', 
    '0503', '0603', '0703', '0803', '0903', '1003', '1103', 
    '1203', '1303', '1403', '1503', '1603', '1703', '1803', 
    '1903', '2003', '2103', '2203', '2303', '2403', '2503', 
    '2603', '2703', '2803', '2903', '3003', '3103', '0104', 
    '0204', '0304', '0404', '0504', '0604', '0704', '0804', 
    '0904', '1004', '1104', '1204', '1304', '1404', '1504', 
    '1604', '1704', '1804', '1904', '2004', '2104', '2204', 
    '2304', '2404', '2504', '2604', '2704', '2804', '2904', 
    '3004', '0105', '0205', '0305', '0405', '0505', '0605', 
    '0705', '0805', '0905', '1005', '1105', '1205', '1305', 
    '1405', '1505', '1605', '1705', '1805', '1905', '2005', 
    '2105', '2205', '2305', '2405', '2505', '2605', '2705', 
    '2805', '2905', '3005', '3105', '0106', '0206', '0306', 
    '0406', '0506', '0606', '0706', '0806', '0906', '1006', 
    '1106', '1206', '1306', '1406', '1506', '1606', '1706', 
    '1806', '1906', '2006', '2106', '2206', '2306', '2406', 
    '2506', '2606', '2706', '2806', '2906', '3006', '0107', 
    '0207', '0307', '0407', '0507', '0607', '0707', '0807', 
    '0907', '1007', '1107', '1207', '1307', '1407', '1507', 
    '1607', '1707', '1807', '1907', '2007', '2107', '2207', 
    '2307', '2407', '2507', '2607', '2707', '2807', '2907', 
    '3007', '3107', '0108', '0208', '0308', '0408', '0508', 
    '0608', '0708', '0808', '0908', '1008', '1108', '1208', 
    '1308', '1408', '1508', '1608', '1708', '1808', '1908', 
    '2008', '2108', '2208', '2308', '2408', '2508', '2608', 
    '2708', '2808', '2908', '3008', '3108', '0109', '0209', 
    '0309', '0409', '0509', '0609', '0709', '0809', '0909', 
    '1009', '1109', '1209', '1309', '1409', '1509', '1609', 
    '1709', '1809', '1909', '2009', '2109', '2209', '2309', 
    '2409', '2509', '2609', '2709', '2809', '2909', '3009', 
    '0110', '0210', '0310', '0410', '0510', '0610', '0710', 
    '0810', '0910', '1010', '1110', '1210', '1310', '1410', 
    '1510', '1610', '1710', '1810', '1910', '2010', '2110', 
    '2210', '2310', '2410', '2510', '2610', '2710', '2810', 
    '2910', '3010', '3110', '0111', '0211', '0311', '0411', 
    '0511', '0611', '0711', '0811', '0911', '1011', '1111', 
    '1211', '1311', '1411', '1511', '1611', '1711', '1811', 
    '1911', '2011', '2111', '2211', '2311', '2411', '2511', 
    '2611', '2711', '2811', '2911', '3011', '0112', '0212', 
    '0312', '0412', '0512', '0612', '0712', '0812', '0912', 
    '1012', '1112', '1212', '1312', '1412', '1512', '1612', 
    '1712', '1812', '1912', '2012', '2112', '2212', '2312', 
    '2412', '2512', '2612', '2712', '2812', '2912', '3012', 
    '3112'
]

top_lvl_domains = [
    'aaa', 'aarp', 'abarth', 'abb', 'abbott', 'abbvie', 'abc',
    'able', 'abogado', 'abudhabi', 'ac', 'academy', 'accenture',
    'accountant', 'accountants', 'aco', 'actor', 'ad', 'adac', 
    'ads', 'adult', 'ae', 'aeg', 'aero', 'aetna', 'af', 'afamilycompany', 
    'afl', 'africa', 'ag', 'agakhan', 'agency', 'ai', 'aig', 'airbus', 
    'airforce', 'airtel', 'akdn', 'al', 'alfaromeo', 'alibaba', 'alipay', 
    'allfinanz', 'allstate', 'ally', 'alsace', 'alstom', 'am', 'amazon', 
    'americanexpress', 'americanfamily', 'amex', 'amfam', 'amica', 
    'amsterdam', 'analytics', 'android', 'anquan', 'anz', 'ao', 'aol', 
    'apartments', 'app', 'apple', 'aq', 'aquarelle', 'ar', 'arab', 
    'aramco', 'archi', 'army', 'arpa', 'art', 'arte', 'as', 'asda', 
    'asia', 'associates', 'at', 'athleta', 'attorney', 'au', 'auction', 
    'audi', 'audible', 'audio', 'auspost', 'author', 'auto', 'autos', 
    'avianca', 'aw', 'aws', 'ax', 'axa', 'az', 'azure', 'ba', 'baby', 
    'baidu', 'banamex', 'bananarepublic', 'band', 'bank', 'bar', 'barcelona', 
    'barclaycard', 'barclays', 'barefoot', 'bargains', 'baseball', 'basketball', 
    'bauhaus', 'bayern', 'bb', 'bbc', 'bbt', 'bbva', 'bcg', 'bcn', 'bd', 
    'be', 'beats', 'beauty', 'beer', 'bentley', 'berlin', 'best', 
    'bestbuy', 'bet', 'bf', 'bg', 'bh', 'bharti', 'bi', 'bible', 
    'bid', 'bike', 'bing', 'bingo', 'bio', 'biz', 'bj', 'black', 
    'blackfriday', 'blockbuster', 'blog', 'bloomberg', 'blue', 'bm', 
    'bms', 'bmw', 'bn', 'bnpparibas', 'bo', 'boats', 'boehringer', 
    'bofa', 'bom', 'bond', 'boo', 'book', 'booking', 'bosch', 'bostik', 
    'boston', 'bot', 'boutique', 'box', 'br', 'bradesco', 'bridgestone', 
    'broadway', 'broker', 'brother', 'brussels', 'bs', 'bt', 'budapest', 
    'bugatti', 'build', 'builders', 'business', 'buy', 'buzz', 'bv', 'bw', 
    'by', 'bz', 'bzh', 'ca', 'cab', 'cafe', 'cal', 'call', 'calvinklein', 
    'cam', 'camera', 'camp', 'cancerresearch', 'canon', 'capetown', 'capital', 
    'capitalone', 'car', 'caravan', 'cards', 'care', 'career', 'careers', 
    'cars', 'casa', 'case', 'cash', 'casino', 'cat', 'catering', 'catholic', 
    'cba', 'cbn', 'cbre', 'cbs', 'cc', 'cd', 'center', 'ceo', 'cern', 
    'cf', 'cfa', 'cfd', 'cg', 'ch', 'chanel', 'channel', 'charity', 
    'chase', 'chat', 'cheap', 'chintai', 'christmas', 'chrome', 'church',
    'ci', 'cipriani', 'circle', 'cisco', 'citadel', 'citi', 'citic', 
    'city', 'cityeats', 'ck', 'cl', 'claims', 'cleaning', 'click', 
    'clinic', 'clinique', 'clothing', 'cloud', 'club', 'clubmed', 
    'cm', 'cn', 'co', 'coach', 'codes', 'coffee', 'college', 'cologne', 
    'com', 'comcast', 'commbank', 'community', 'company', 'compare', 
    'computer', 'comsec', 'condos', 'construction', 'consulting', 
    'contact', 'contractors', 'cooking', 'cookingchannel', 'cool',
    'coop', 'corsica', 'country', 'coupon', 'coupons', 'courses', 
    'cpa', 'cr', 'credit', 'creditcard', 'creditunion', 'cricket',
    'crown', 'crs', 'cruise', 'cruises', 'csc', 'cu', 'cuisinella',
    'cv', 'cw', 'cx', 'cy', 'cymru', 'cyou', 'cz', 'dabur', 'dad', 
    'dance', 'data', 'date', 'dating', 'datsun', 'day', 'dclk',
    'dds', 'de', 'deal', 'dealer', 'deals', 'degree', 'delivery', 
    'dell', 'deloitte', 'delta', 'democrat', 'dental', 'dentist', 
    'desi', 'design', 'dev', 'dhl', 'diamonds', 'diet', 'digital', 
    'direct', 'directory', 'discount', 'discover', 'dish', 'diy', 
    'dj', 'dk', 'dm', 'dnp', 'do', 'docs', 'doctor', 'dog', 'domains', 
    'dot', 'download', 'drive', 'dtv', 'dubai', 'duck', 'dunlop', 
    'dupont', 'durban', 'dvag', 'dvr', 'dz', 'earth', 'eat', 'ec', 
    'eco', 'edeka', 'edu', 'education', 'ee', 'eg', 'email', 'emerck', 
    'energy', 'engineer', 'engineering', 'enterprises', 'epson', 
    'equipment', 'er', 'ericsson', 'erni', 'es', 'esq', 'estate', 
    'et', 'etisalat', 'eu', 'eurovision', 'eus', 'events', 'exchange', 
    'expert', 'exposed', 'express', 'extraspace', 'fage', 'fail', 
    'fairwinds', 'faith', 'family', 'fan', 'fans', 'farm', 'farmers', 
    'fashion', 'fast', 'fedex', 'feedback', 'ferrari', 'ferrero', 'fi', 
    'fiat', 'fidelity', 'fido', 'film', 'final', 'finance', 'financial', 
    'fire', 'firestone', 'firmdale', 'fish', 'fishing', 'fit', 'fitness', 
    'fj', 'fk', 'flickr', 'flights', 'flir', 'florist', 'flowers', 'fly', 
    'fm', 'fo', 'foo', 'food', 'foodnetwork', 'football', 'ford', 
    'forex', 'forsale', 'forum', 'foundation', 'fox', 'fr', 'free', 
    'fresenius', 'frl', 'frogans', 'frontdoor', 'frontier', 'ftr', 
    'fujitsu', 'fun', 'fund', 'furniture', 'futbol', 'fyi', 'ga', 'gal', 
    'gallery', 'gallo', 'gallup', 'game', 'games', 'gap', 'garden', 'gay', 
    'gb', 'gbiz', 'gd', 'gdn', 'ge', 'gea', 'gent', 'genting', 'george', 
    'gf', 'gg', 'ggee', 'gh', 'gi', 'gift', 'gifts', 'gives', 'giving', 
    'gl', 'glade', 'glass', 'gle', 'global', 'globo', 'gm', 'gmail', 
    'gmbh', 'gmo', 'gmx', 'gn', 'godaddy', 'gold', 'goldpoint', 'golf', 
    'goo', 'goodyear', 'goog', 'google', 'gop', 'got', 'gov', 'gp', 'gq', 
    'gr', 'grainger', 'graphics', 'gratis', 'green', 'gripe', 'grocery', 
    'group', 'gs', 'gt', 'gu', 'guardian', 'gucci', 'guge', 'guide', 
    'guitars', 'guru', 'gw', 'gy', 'hair', 'hamburg', 'hangout', 'haus', 
    'hbo', 'hdfc', 'hdfcbank', 'health', 'healthcare', 'help', 'helsinki', 
    'here', 'hermes', 'hgtv', 'hiphop', 'hisamitsu', 'hitachi', 'hiv', 
    'hk', 'hkt', 'hm', 'hn', 'hockey', 'holdings', 'holiday', 'homedepot', 
    'homegoods', 'homes', 'homesense', 'honda', 'horse', 'hospital', 
    'host', 'hosting', 'hot', 'hoteles', 'hotels', 'hotmail', 'house', 
    'how', 'hr', 'hsbc', 'ht', 'hu', 'hughes', 'hyatt', 'hyundai', 'ibm', 
    'icbc', 'ice', 'icu', 'id', 'ie', 'ieee', 'ifm', 'ikano', 'il', 'im', 
    'imamat', 'imdb', 'immo', 'immobilien', 'in', 'inc', 'industries', 
    'infiniti', 'info', 'ing', 'ink', 'institute', 'insurance', 'insure', 
    'int', 'international', 'intuit', 'investments', 'io', 'ipiranga', 
    'iq', 'ir', 'irish', 'is', 'ismaili', 'ist', 'istanbul', 'it', 'itau', 
    'itv', 'jaguar', 'java', 'jcb', 'je', 'jeep', 'jetzt', 'jewelry', 
    'jio', 'jll', 'jm', 'jmp', 'jnj', 'jo', 'jobs', 'joburg', 'jot', 
    'joy', 'jp', 'jpmorgan', 'jprs', 'juegos', 'juniper', 'kaufen', 
    'kddi', 'ke', 'kerryhotels', 'kerrylogistics', 'kerryproperties', 
    'kfh', 'kg', 'kh', 'ki', 'kia', 'kim', 'kinder', 'kindle', 'kitchen', 
    'kiwi', 'km', 'kn', 'koeln', 'komatsu', 'kosher', 'kp', 'kpmg', 
    'kpn', 'kr', 'krd', 'kred', 'kuokgroup', 'kw', 'ky', 'kyoto', 'kz', 
    'la', 'lacaixa', 'lamborghini', 'lamer', 'lancaster', 'lancia', 
    'land', 'landrover', 'lanxess', 'lasalle', 'lat', 'latino', 'latrobe', 
    'law', 'lawyer', 'lb', 'lc', 'lds', 'lease', 'leclerc', 'lefrak', 
    'legal', 'lego', 'lexus', 'lgbt', 'li', 'lidl', 'life', 'lifeinsurance', 
    'lifestyle', 'lighting', 'like', 'lilly', 'limited', 'limo', 'lincoln', 
    'linde', 'link', 'lipsy', 'live', 'living', 'lixil', 'lk', 'llc', 'llp', 
    'loan', 'loans', 'locker', 'locus', 'loft', 'lol', 'london', 'lotte', 
    'lotto', 'love', 'lpl', 'lplfinancial', 'lr', 'ls', 'lt', 'ltd', 'ltda', 
    'lu', 'lundbeck', 'luxe', 'luxury', 'lv', 'ly', 'ma', 'macys', 'madrid', 
    'maif', 'maison', 'makeup', 'man', 'management', 'mango', 'map', 
    'market', 'marketing', 'markets', 'marriott', 'marshalls', 'maserati', 
    'mattel', 'mba', 'mc', 'mckinsey', 'md', 'me', 'med', 'media', 
    'meet', 'melbourne', 'meme', 'memorial', 'men', 'menu', 'merckmsd', 
    'mg', 'mh', 'miami', 'microsoft', 'mil', 'mini', 'mint', 'mit', 
    'mitsubishi', 'mk', 'ml', 'mlb', 'mls', 'mm', 'mma', 'mn', 'mo', 
    'mobi', 'mobile', 'moda', 'moe', 'moi', 'mom', 'monash', 'money', 
    'monster', 'mormon', 'mortgage', 'moscow', 'moto', 'motorcycles', 
    'mov', 'movie', 'mp', 'mq', 'mr', 'ms', 'msd', 'mt', 'mtn', 'mtr', 
    'mu', 'museum', 'mutual', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'nab', 
    'nagoya', 'name', 'natura', 'navy', 'nba', 'nc', 'ne', 'nec', 'net', 
    'netbank', 'netflix', 'network', 'neustar', 'new', 'news', 'next', 
    'nextdirect', 'nexus', 'nf', 'nfl', 'ng', 'ngo', 'nhk', 'ni', 'nico', 
    'nike', 'nikon', 'ninja', 'nissan', 'nissay', 'nl', 'no', 'nokia', 
    'northwesternmutual', 'norton', 'now', 'nowruz', 'nowtv', 'np', 
    'nr', 'nra', 'nrw', 'ntt', 'nu', 'nyc', 'nz', 'obi', 'observer', 
    'off', 'office', 'okinawa', 'olayan', 'olayangroup', 'oldnavy', 
    'ollo', 'om', 'omega', 'one', 'ong', 'onl', 'online', 'ooo', 'open', 
    'oracle', 'orange', 'org', 'organic', 'origins', 'osaka', 'otsuka', 
    'ott', 'ovh', 'pa', 'page', 'panasonic', 'paris', 'pars', 'partners', 
    'parts', 'party', 'passagens', 'pay', 'pccw', 'pe', 'pet', 'pf', 
    'pfizer', 'pg', 'ph', 'pharmacy', 'phd', 'philips', 'phone', 'photo', 
    'photography', 'photos', 'physio', 'pics', 'pictet', 'pictures', 
    'pid', 'pin', 'ping', 'pink', 'pioneer', 'pizza', 'pk', 'pl', 'place', 
    'play', 'playstation', 'plumbing', 'plus', 'pm', 'pn', 'pnc', 'pohl', 
    'poker', 'politie', 'porn', 'post', 'pr', 'pramerica', 'praxi', 
    'press', 'prime', 'pro', 'prod', 'productions', 'prof', 'progressive', 
    'promo', 'properties', 'property', 'protection', 'pru', 'prudential', 
    'ps', 'pt', 'pub', 'pw', 'pwc', 'py', 'qa', 'qpon', 'quebec', 'quest', 
    'racing', 'radio', 'raid', 're', 'read', 'realestate', 'realtor',
    'realty', 'recipes', 'red', 'redstone', 'redumbrella', 'rehab', 'reise', 
    'reisen', 'reit', 'reliance', 'ren', 'rent', 'rentals', 'repair', 
    'report', 'republican', 'rest', 'restaurant', 'review', 'reviews', 
    'rexroth', 'rich', 'richardli', 'ricoh', 'ril', 'rio', 'rip', 'ro', 
    'rocher', 'rocks', 'rodeo', 'rogers', 'room', 'rs', 'rsvp', 'ru', 
    'rugby', 'ruhr', 'run', 'rw', 'rwe', 'ryukyu', 'sa', 'saarland', 'safe', 
    'safety', 'sakura', 'sale', 'salon', 'samsclub', 'samsung', 'sandvik', 
    'sandvikcoromant', 'sanofi', 'sap', 'sarl', 'sas', 'save', 'saxo', 'sb', 
    'sbi', 'sbs', 'sc', 'sca', 'scb', 'schaeffler', 'schmidt', 'scholarships', 
    'school', 'schule', 'schwarz', 'science', 'scjohnson', 'scot', 'sd', 
    'se', 'search', 'seat', 'secure', 'security', 'seek', 'select', 'sener', 
    'services', 'ses', 'seven', 'sew', 'sex', 'sexy', 'sfr', 'sg', 'sh', 
    'shangrila', 'sharp', 'shaw', 'shell', 'shia', 'shiksha', 'shoes', 'shop', 
    'shopping', 'shouji', 'show', 'showtime', 'si', 'silk', 'sina', 'singles', 
    'site', 'sj', 'sk', 'ski', 'skin', 'sky', 'skype', 'sl', 'sling', 'sm', 
    'smart', 'smile', 'sn', 'sncf', 'so', 'soccer', 'social', 'softbank', 
    'software', 'sohu', 'solar', 'solutions', 'song', 'sony', 'soy', 'spa', 
    'space', 'sport', 'spot', 'sr', 'srl', 'ss', 'st', 'stada', 'staples', 
    'star', 'statebank', 'statefarm', 'stc', 'stcgroup', 'stockholm', 'storage', 
    'store', 'stream', 'studio', 'study', 'style', 'su', 'sucks', 'supplies', 
    'supply', 'support', 'surf', 'surgery', 'suzuki', 'sv', 'swatch', 'swiss', 
    'sx', 'sy', 'sydney', 'systems', 'sz', 'tab', 'taipei', 'talk', 'taobao', 
    'target', 'tatamotors', 'tatar', 'tattoo', 'tax', 'taxi', 'tc', 'tci', 'td', 
    'tdk', 'team', 'tech', 'technology', 'tel', 'temasek', 'tennis', 'teva', 
    'tf', 'tg', 'th', 'thd', 'theater', 'theatre', 'tiaa', 'tickets', 'tienda', 
    'tiffany', 'tips', 'tires', 'tirol', 'tj', 'tjmaxx', 'tjx', 'tk', 'tkmaxx', 
    'tl', 'tm', 'tmall', 'tn', 'to', 'today', 'tokyo', 'tools', 'top', 'toray', 
    'toshiba', 'total', 'tours', 'town', 'toyota', 'toys', 'tr', 'trade', 
    'trading', 'training', 'travel', 'travelchannel', 'travelers', 
    'travelersinsurance', 'trust', 'trv', 'tt', 'tube', 'tui', 'tunes', 'tushu', 
    'tv', 'tvs', 'tw', 'tz', 'ua', 'ubank', 'ubs', 'ug', 'uk', 'unicom', 
    'university', 'uno', 'uol', 'ups', 'us', 'uy', 'uz', 'va', 'vacations', 
    'vana', 'vanguard', 'vc', 've', 'vegas', 'ventures', 'verisign', 
    'versicherung', 'vet', 'vg', 'vi', 'viajes', 'video', 'vig', 'viking', 
    'villas', 'vin', 'vip', 'virgin', 'visa', 'vision', 'viva', 'vivo', 
    'vlaanderen', 'vn', 'vodka', 'volkswagen', 'volvo', 'vote', 'voting', 
    'voto', 'voyage', 'vu', 'vuelos', 'wales', 'walmart', 'walter', 'wang', 
    'wanggou', 'watch', 'watches', 'weather', 'weatherchannel', 'webcam', 
    'weber', 'website', 'wed', 'wedding', 'weibo', 'weir', 'wf', 'whoswho', 
    'wien', 'wiki', 'williamhill', 'win', 'windows', 'wine', 'winners', 'wme', 
    'wolterskluwer', 'woodside', 'work', 'works', 'world', 'wow', 'ws', 'wtc', 
    'wtf', 'xbox', 'xerox', 'xfinity', 'xihuan', 'xin', 'xn--11b4c3d', 
    'xn--1ck2e1b', 'xn--1qqw23a', 'xn--2scrj9c', 'xn--30rr7y', 'xn--3bst00m', 
    'xn--3ds443g', 'xn--3e0b707e', 'xn--3hcrj9c', 'xn--3oq18vl8pn36a', 'xn--3pxu8k', 
    'xn--42c2d9a', 'xn--45br5cyl', 'xn--45brj9c', 'xn--45q11c', 'xn--4dbrk0ce', 
    'xn--4gbrim', 'xn--54b7fta0cc', 'xn--55qw42g', 'xn--55qx5d', 'xn--5su34j936bgsg', 
    'xn--5tzm5g', 'xn--6frz82g', 'xn--6qq986b3xl', 'xn--80adxhks', 'xn--80ao21a', 
    'xn--80aqecdr1a', 'xn--80asehdb', 'xn--80aswg', 'xn--8y0a063a', 'xn--90a3ac', 
    'xn--90ae', 'xn--90ais', 'xn--9dbq2a', 'xn--9et52u', 'xn--9krt00a', 
    'xn--b4w605ferd', 'xn--bck1b9a5dre4c', 'xn--c1avg', 'xn--c2br7g', 'xn--cck2b3b', 
    'xn--cckwcxetd', 'xn--cg4bki', 'xn--clchc0ea0b2g2a9gcd', 'xn--czr694b', 
    'xn--czrs0t', 'xn--czru2d', 'xn--d1acj3b', 'xn--d1alf', 'xn--e1a4c', 
    'xn--eckvdtc9d', 'xn--efvy88h', 'xn--fct429k', 'xn--fhbei', 'xn--fiq228c5hs',
    'xn--fiq64b', 'xn--fiqs8s', 'xn--fiqz9s', 'xn--fjq720a', 'xn--flw351e', 
    'xn--fpcrj9c3d', 'xn--fzc2c9e2c', 'xn--fzys8d69uvgm', 'xn--g2xx48c', 'xn--gckr3f0f', 
    'xn--gecrj9c', 'xn--gk3at1e', 'xn--h2breg3eve', 'xn--h2brj9c', 'xn--h2brj9c8c', 
    'xn--hxt814e', 'xn--i1b6b1a6a2e', 'xn--imr513n', 'xn--io0a7i', 'xn--j1aef', 
    'xn--j1amh', 'xn--j6w193g', 'xn--jlq480n2rg', 'xn--jlq61u9w7b', 'xn--jvr189m', 
    'xn--kcrx77d1x4a', 'xn--kprw13d', 'xn--kpry57d', 'xn--kput3i', 'xn--l1acc', 
    'xn--lgbbat1ad8j', 'xn--mgb9awbf', 'xn--mgba3a3ejt', 'xn--mgba3a4f16a', 
    'xn--mgba7c0bbn0a', 'xn--mgbaakc7dvf', 'xn--mgbaam7a8h', 'xn--mgbab2bd', 
    'xn--mgbah1a3hjkrd', 'xn--mgbai9azgqp6j', 'xn--mgbayh7gpa', 'xn--mgbbh1a', 
    'xn--mgbbh1a71e', 'xn--mgbc0a9azcg', 'xn--mgbca7dzdo', 'xn--mgbcpq6gpa1a', 
    'xn--mgberp4a5d4ar', 'xn--mgbgu82a', 'xn--mgbi4ecexp', 'xn--mgbpl2fh', 
    'xn--mgbt3dhd', 'xn--mgbtx2b', 'xn--mgbx4cd0ab', 'xn--mix891f', 'xn--mk1bu44c', 
    'xn--mxtq1m', 'xn--ngbc5azd', 'xn--ngbe9e0a', 'xn--ngbrx', 'xn--node', 'xn--nqv7f', 
    'xn--nqv7fs00ema', 'xn--nyqy26a', 'xn--o3cw4h', 'xn--ogbpf8fl', 'xn--otu796d', 
    'xn--p1acf', 'xn--p1ai', 'xn--pgbs0dh', 'xn--pssy2u', 'xn--q7ce6a', 'xn--q9jyb4c', 
    'xn--qcka1pmc', 'xn--qxa6a', 'xn--qxam', 'xn--rhqv96g', 'xn--rovu88b', 
    'xn--rvc1e0am3e', 'xn--s9brj9c', 'xn--ses554g', 'xn--t60b56a', 'xn--tckwe', 
    'xn--tiq49xqyj', 'xn--unup4y', 'xn--vermgensberater-ctb', 'xn--vermgensberatung-pwb', 
    'xn--vhquv', 'xn--vuq861b', 'xn--w4r85el8fhu5dnra', 'xn--w4rs40l', 'xn--wgbh1c', 
    'xn--wgbl6a', 'xn--xhq521b', 'xn--xkc2al3hye2a', 'xn--xkc2dl3a5ee0h', 'xn--y9a3aq', 
    'xn--yfro4i67o', 'xn--ygbi2ammx', 'xn--zfr164b', 'xxx', 'xyz', 'yachts', 'yahoo', 
    'yamaxun', 'yandex', 'ye', 'yodobashi', 'yoga', 'yokohama', 'you', 'youtube', 
    'yt', 'yun', 'za', 'zappos', 'zara', 'zero', 'zip', 'zm', 'zone', 'zuerich', 'zw'
]


#data = json.loads(open("dates/dates.json", "r").read())
#dates = []
#for i in data['dates']:
#    dates.append(i['date'])
#    
#data = json.loads(open("top_level_domains/top_lvl_domains.json", "r").read())
#top_lvl_domains = []
#for top_lvl_domain in data['top-lvl-domains']:
#    top_lvl_domains.append(top_lvl_domain['top-lvl-domain'])
    
DOMAIN = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','æ','ø','å',
          'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','Æ','Ø','Å',
          '0','1','2','3','4','5','6','7','8','9',
          '.','-','!','#','$','£','%','&','\'','*','+','/','=','?','^','_','´','{','}','|',' ',',','(',')',':','<','>','`','~','é']
LOWER_LETTER_END = 29
UPPER_LETTER_END = 58
INTEGER_END = 68
EMAIL_SIGNS_END = 85

def map_from_numeral_string(numeral_string, mapping):
    outputList = []
    for numeral in numeral_string:
        if not numeral in mapping:
            raise ValueError(f"{numeral} is not contained in the format. Accepted values: {mapping.keys()}")
        outputList.append(mapping[numeral])
    return outputList


def map_from_name(name, mapping):
    if not name in mapping:
        raise ValueError(f"{name} is not contained in the format. Accepted values: {mapping.keys()}")
    return (mapping[(name)])


def get_mapping_from_domain(domain):
    index = list(map(int, arange(0, len(domain)).tolist()))
    return [dict(zip(domain, index)), dict(zip(index, domain))]


def validateCard(cardNumber):
    sum = 0
    for index in range(len(cardNumber)):
        if (index % 2 == 0):
            sum += (int(cardNumber[index]) * 2) % 9
        else:
            sum += int(cardNumber[index])
    return str((10 - sum) % 10)

def validateCPR(CPR):
        weights = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        sum = 0
        for digit in range(len(CPR)):
            sum += (int(CPR[digit]) * weights[digit])
        if(11 - (sum % 11))%11==10:
            return '0'
        else:
            return str((11 - (sum % 11))%11)

mapping_letters = get_mapping_from_domain(DOMAIN[:UPPER_LETTER_END])
mapping_upper_letters = get_mapping_from_domain(DOMAIN[LOWER_LETTER_END:UPPER_LETTER_END])
mapping_lower_letters = get_mapping_from_domain(DOMAIN[:LOWER_LETTER_END])
mapping_email_tail = get_mapping_from_domain(DOMAIN[:INTEGER_END+2])
mapping_letters_integer = get_mapping_from_domain(DOMAIN[:INTEGER_END])
mapping_all = get_mapping_from_domain(DOMAIN)
mapping_dates = get_mapping_from_domain(dates)
mapping_top_lvl_domains = get_mapping_from_domain(top_lvl_domains)


def text_to_numeral_list(text, dataFormat):
    if dataFormat == Format.DIGITS:
        if not text.isdecimal():
            raise ValueError(f"{text} is not a valid message for the given format. only numbers are allowed.")
        return [int(x) for x in text]

    if dataFormat == Format.CREDITCARD:
        text = text.replace(' ', '')
        if not text.isdecimal():
            raise ValueError(f"{text} is not a valid message for the given format. only numbers are allowed.")

        if (text[len(text) - 1] != validateCard(text[:len(text) - 1])):
            raise ValueError(f"{text} is not a valid credit card number")

        return [int(x) for x in text[:len(text)-1]]

    if dataFormat == Format.LETTERS:

        return map_from_numeral_string(text, mapping_letters[0])

    if dataFormat == Format.STRING:
        numerals = map_from_numeral_string(text, mapping_all[0])
        
        return numerals
        
    if dataFormat == Format.EMAIL:
        first_break_index = text.find('@')
        second_break_index = text.rfind('.')

        text1 = text[:first_break_index]
        text2 = text[first_break_index+1:second_break_index]
        text3 = text[second_break_index+1:]

        numerals1 =  map_from_numeral_string(text1,mapping_letters_integer[0])
        numerals2 =  map_from_numeral_string(text2,mapping_email_tail[0])
        numerals3 =  map_from_name(text3,mapping_top_lvl_domains[0])

        return [numerals1, numerals2, numerals3] 

    if dataFormat == Format.CPR:
        if (text[len(text) - 1] != validateCPR(text[:len(text) - 1])):
            raise ValueError(f"{text} is not a valid CPR number")

        text1 = text[:4]

        numerals1 = map_from_name(text1,mapping_dates[0])
        numerals2 = [int(x) for x in text[4:]]

        return [numerals1, numerals2]


def numeral_list_to_text(numerals, dataFormat):
    if dataFormat == Format.DIGITS:
        return ''.join([str(x) for x in numerals])

    if dataFormat == Format.CREDITCARD:
        text1 = ''.join([str(x) for x in numerals[:4]])
        text2 = ''.join([str(x) for x in numerals[4:8]])
        text3 = ''.join([str(x) for x in numerals[8:12]])
        text4 = ''.join([str(x) for x in numerals[12:]])

        return text1 + ' ' + text2 + ' ' + text3 + ' ' + text4 + validateCard(text1+text2+text3+text4)

    if dataFormat == Format.LETTERS:
        return ''.join(map_from_numeral_string(numerals, mapping_letters[1]))

    if dataFormat == Format.STRING:
        return ''.join(map_from_numeral_string(numerals, mapping_all[1]))
        
    if dataFormat == Format.EMAIL:
        text1 = ''.join(map_from_numeral_string(numerals[0],mapping_letters_integer[1]))
        text2 = ''.join(map_from_numeral_string(numerals[1],mapping_email_tail[1]))
        text3 = ''.join(map_from_name(numerals[2],mapping_top_lvl_domains[1]))

        return text1 + '@' + text2 + '.' + text3
        
    if dataFormat == Format.CPR:
        text1 = ''.join(map_from_name(numerals[1],mapping_dates[1]))
        text2 = ''.join([str(x) for x in numerals[0]])

        return text1 + text2 + validateCPR(text1 + text2)

def get_radix_by_format(format):
    if format == Format.DIGITS:
        return 10

    if format == Format.CREDITCARD:
        return 10

    if format == Format.LETTERS:
        return len(mapping_letters[0])

    if format == Format.STRING:
        return len(mapping_all[0])

    if format == Format.EMAIL:        
        radix1 = len(mapping_letters_integer[0])
        radix2 = len(mapping_email_tail[0])
        radix3 = len(mapping_top_lvl_domains[0])
        return [radix1, radix2, radix3]

    if format == Format.CPR:
        radix1 = len(mapping_dates[0])
        radix2 = 10
        return [radix1, radix2]