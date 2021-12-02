# Imports
from PyWebValidators import textValidators, miscValidators


# Text Validators
def test_html():
    print("[+] Testing HTML")

    html_test_1 = "<h1>Test Case</h1>"  # True
    html_test_2 = "<a href='google.com'>Here</a>"  # True
    html_test_3 = "</br>"  # False
    html_test_4 = "<img src='#'/>"  # True
    html_test_5 = "<p>"  # False

    assert textValidators.validate_html(html=html_test_1) is True
    assert textValidators.validate_html(html=html_test_2) is True
    assert textValidators.validate_html(html=html_test_3) is False
    assert textValidators.validate_html(html=html_test_4) is True
    assert textValidators.validate_html(html=html_test_5) is False

    print("[+] HTML Test Completed")


def test_xml():
    print("[+] Testing XML")

    xml_test_1 = "<?xml version=\"1.0\"?><country name=\"Afghanistan\"><population>32225560</population>" \
                 "<area>652000</area><capital>Kabul</capital></country>"  # True
    xml_test_2 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><note><to>Tove</to><from>Jani</from>" \
                 "<heading>Reminder</heading><body>Don't forget me this weekend!</body></note>"  # True
    xml_test_3 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><note><to>Tove</to><from>Jani</from>" \
                 "<heading>Reminder</pheading><body>Don't forget me this weekend!</body></note>"  # False
    xml_test_4 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"  # False
    xml_test_5 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><user><name>John Doe</name>" \
                 "<phone><id>1</id</user>"  # False

    assert textValidators.validate_xml(xml=xml_test_1) is True
    assert textValidators.validate_xml(xml=xml_test_2) is True
    assert textValidators.validate_xml(xml=xml_test_3) is False
    assert textValidators.validate_xml(xml=xml_test_4) is False
    assert textValidators.validate_xml(xml=xml_test_5) is False

    print("[+] XML Test Completed")


def test_json():
    print("[+] Testing JSON")

    json_test_1 = "{\"description\": \"Hello world!\",\"status\": true,\"value_a\": 1,\"value_b\": 3.14}"  # True
    json_test_2 = "{\"a\": 123,'b': 456}"  # False
    json_test_3 = "{'level': {'updatedAt': '1970-01-01T00:00:00.000Z','value': 1},}"  # False
    json_test_4 = "{\"response1\": [{\"some\": \"object\"},{\"some\": \"object\"}],\"response2\": " \
                  "[{\"some\": \"object\"},{\"some\": \"object\"}]}"  # True
    json_test_5 = "{\"id\": 10,\"name\": \"DonOfDen\",\"contact_number\": 1234567890}"  # True

    assert textValidators.validate_json(data=json_test_1) is True
    assert textValidators.validate_json(data=json_test_2) is False
    assert textValidators.validate_json(data=json_test_3) is False
    assert textValidators.validate_json(data=json_test_4) is True
    assert textValidators.validate_json(data=json_test_5) is True

    print("[+] JSON Test Completed")


def test_text():
    print("[+] Testing Texts")

    txt_test_1 = "Hi, This is a sample Text!"  # True
    txt_test_2 = "How @r3 YoU Doing?"  # False
    txt_test_3 = "Another"  # False
    txt_test_4 = "s@MpL3"  # False
    txt_test_5 = "T3Xt_15_H3re"  # True

    assert textValidators.validate_text(text=txt_test_1) is True
    assert textValidators.validate_text(text=txt_test_2, special_characters=False) is False
    assert textValidators.validate_text(text=txt_test_3, min_length=8) is False
    assert textValidators.validate_text(text=txt_test_4, max_length=3) is False
    assert textValidators.validate_text(text=txt_test_5, min_length=4, max_length=20) is True

    print("[+] Text Test Completed")


# File Validators


# Misc Validators
def test_ip():
    print("[+] Testing IP Addresses")

    ip_test_1 = "192.168.0.1"  # True
    ip_test_2 = "110.234.52.124"  # True
    ip_test_3 = "666.1.2.2"  # False
    ip_test_4 = "25.99.208.255"  # True
    ip_test_5 = "366.1.2.2.4"  # False

    assert miscValidators.validate_ip(ip=ip_test_1) is True
    assert miscValidators.validate_ip(ip=ip_test_2) is True
    assert miscValidators.validate_ip(ip=ip_test_3) is False
    assert miscValidators.validate_ip(ip=ip_test_4) is True
    assert miscValidators.validate_ip(ip=ip_test_5) is False

    print("[+] IP Test Completed")


def test_mac():
    print("[+] Testing MAC Addresses")

    mac_test_1 = "01-23-45-67-89-AB"  # True
    mac_test_2 = "01:23:45:67:89:AB"  # True
    mac_test_3 = "0123.4567.89AB"  # True
    mac_test_4 = "01-23-45-67-89-AH"  # False
    mac_test_5 = "01-23-45-67-AH"  # False

    assert miscValidators.validate_mac(mac=mac_test_1) is True
    assert miscValidators.validate_mac(mac=mac_test_2) is True
    assert miscValidators.validate_mac(mac=mac_test_3) is True
    assert miscValidators.validate_mac(mac=mac_test_4) is False
    assert miscValidators.validate_mac(mac=mac_test_5) is False

    print("[+] MAC Test Completed")


def test_date():
    print("[+] Testing Date Formats")

    date_test_1, format_1 = "12-25-2018", "%Y-%m-d"  # False
    date_test_2, format_2 = "04-01-1997", "%d-%m-%Y"  # True
    date_test_3, format_3 = "04-14-1997", "%d-%m-%Y"  # False
    date_test_4, format_4 = "2017-12-31", "%Y-%m-%d"  # True
    date_test_5, format_5 = "03-17-2021", "%Y-%m-%d"  # False

    assert miscValidators.validate_date(date=date_test_1, date_format=format_1) is False
    assert miscValidators.validate_date(date=date_test_2, date_format=format_2) is True
    assert miscValidators.validate_date(date=date_test_3, date_format=format_3) is False
    assert miscValidators.validate_date(date=date_test_4, date_format=format_4) is True
    assert miscValidators.validate_date(date=date_test_5, date_format=format_5) is False

    print("[+] Date Test Completed")


def test_email():
    print("[+] Testing E-Mail Addresses")

    email_test_1 = "ankitrai326@gmail.com"  # True
    email_test_2 = "my.ownsite@ourearth.org"  # True
    email_test_3 = "ankitrai326.com"  # False
    email_test_4 = "rohit.gupta@mcnsolutions.net"  # True
    email_test_5 = "praveen@c-sharpcorner.com"  # False

    assert miscValidators.validate_email(email=email_test_1) is True
    assert miscValidators.validate_email(email=email_test_2) is True
    assert miscValidators.validate_email(email=email_test_3) is False
    assert miscValidators.validate_email(email=email_test_4) is True
    assert miscValidators.validate_email(email=email_test_5) is False

    print("[+] E-Mail Test Completed")
