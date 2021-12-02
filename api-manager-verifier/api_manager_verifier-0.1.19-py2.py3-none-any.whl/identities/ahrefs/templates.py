def login_template(username,password):
    template={
        'amember_login':username,
        'amember_pass':password,
        '_referer':'https://toolszap.com/'
    }
    return template

def organic_chart_template(domain):
    template={
        "mode": "subdomains",
        "url": domain
    }
    return template