from flask import json

QUERY = """{
  webConfig {
    id_
    json
  }
}"""


##__________________________________________________________________||
def test_graphql(client, snapshot):
    path = "/graphql"

    response = client.get(path, query_string=dict(query=QUERY))
    assert 200 == response.status_code

    un_jsonified = json.loads(response.data)
    snapshot.assert_match(un_jsonified)
    # print(json.dumps(un_jsonified, indent=2))


##__________________________________________________________________||
