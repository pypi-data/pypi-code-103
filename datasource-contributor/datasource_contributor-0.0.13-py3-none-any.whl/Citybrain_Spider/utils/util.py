import requests


def none2nil(row):
    """
    将字典val为None的转化为""
    :param row:
    :return:
    """
    for key in row:
        if row[key] is None:
            row[key] = ""
    return row

TEST_SSO_DOMAIN = "http://192.168.12.156:32003"
TEST_DOMAIN = "http://192.168.12.156:32002"
PRODUCTION_SSO_DOMAIN = "http://sso.citybrain.org"
PRODUCTION_DOMAIN = "http://www.citybrain.org"
CURRENT_SSO_DOMAIN = ""
CURRENT_DOMAIN = ""

def save_results(row):
    """
    save result to database via http interface
    :return:
    """
    row = none2nil(row)
    CURRENT_DOMAIN = TEST_DOMAIN
    data = {
        "name": row['Name'],
        "description": row['Description'],
        "category": row['Category'],
        "link_url": row['Link_url'],
        "rows": int(row['Rows']),
        "tags": str(row['Tags']),
        "owner": row['Dataset_Owner'],
        "source_link_url": row['Source_Link'],
        "license": "",
        "creator_id": -1
    }
    print("data: %s" % data)
    url = "%s%s" % (CURRENT_DOMAIN, "/api/st_data_source/create/import")
    print("url: %s" % url)
    resp = requests.post(url, json=data)
    data = resp.json()
    print(data)
    # return data['data']
