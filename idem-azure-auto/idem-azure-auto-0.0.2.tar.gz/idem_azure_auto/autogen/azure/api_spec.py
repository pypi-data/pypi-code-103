import logging
import re


try:
    import bs4
    import requests

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def parse(hub, url: str):
    """
    Parse a page such as this one:
    https://docs.microsoft.com/en-us/rest/api/network-gateway/local-network-gateways/create-or-update
    Return a dictionary of a REST api spec"
    """
    plugin = {}
    with requests.get(url) as response:
        html = response.text

    soup = bs4.BeautifulSoup(html, "lxml")

    dts = soup.find_all("dt")
    for dt in dts:
        # Fetch the name of the service that the api belongs to
        if re.sub(r"[\t\n]", "", dt.text) == "Service:":
            plugin.update(
                {"service": re.sub(r"[\t\n]", "", dt.find_next_sibling("dd").text)}
            )
        # Fetch the api version
        if re.sub(r"[\t\n]", "", dt.text) == "API Version:":
            plugin.update(
                {"api_version": re.sub(r"[\t\n]", "", dt.find_next_sibling("dd").text)}
            )

    http_spec = soup.find(class_="lang-http").text
    if http_spec is not None:
        api_method = http_spec.split()[0]
        hub.tool.validators.http.request_method(api_method)
        plugin.update({"api_method": api_method})
        api_url = http_spec.split()[1]
        hub.tool.validators.http.url(api_url)
        plugin.update({"api_url": api_url})
    else:
        err_msg = f"Cannot find api's http specs at {url}"
        logging.error("Error: " + err_msg)
        raise RuntimeError(err_msg)

    # Fetch uri parameters of the api url
    uri_param_header = soup.find(id="uri-parameters")
    if uri_param_header is not None:
        uri_parameters = parse_uri_parameters(
            uri_param_header.find_next_sibling("table")
        )
        if uri_parameters:
            plugin.update({"uri_parameters": uri_parameters})
            # Update api url to snake case
            for uri_parameter in uri_parameters:
                api_url = api_url.replace(
                    uri_parameter.get("name"), uri_parameter.get("name_formatted")
                )
            plugin.update({"api_url": api_url})

    # Fetch the request body of the api
    request_body_header = soup.find(id="request-body")
    if request_body_header is not None:
        request_body = parse_request_body(
            request_body_header.find_next_sibling("table")
        )
        if request_body:
            plugin.update({"request_body": request_body})

    # Fetch the response of the api
    responses_header = soup.find(id="response")
    if responses_header is not None:
        responses = parse_responses(responses_header.find_next_sibling("table"))
        if responses:
            plugin.update({"responses": responses})

    # Fetch definitions of object types used in the api
    definitions_header = soup.find(id="definitions")
    definitions = {}
    if definitions_header is not None:
        definitions_name = parse_definitions(
            definitions_header.find_next_sibling("table")
        )
        definition_header_list = soup.find_all("h3")
        for definition_name in definitions_name:
            definition_header = next(
                filter(
                    lambda h3: definition_name == re.sub(r"[\t\n]", "", h3.text),
                    definition_header_list,
                ),
                None,
            )
            if definition_header is not None:
                definition = parse_definition(
                    definition_header.find_next_sibling("table")
                )
                definitions.update({definition_name: definition})
    if definitions:
        plugin.update({"definitions": definitions})

    return plugin


def parse_uri_parameters(node):
    parse_results = []
    rows = node.find_all("tr")
    for row in rows:
        if row.find("th") is not None:
            continue
        cols = row.find_all("td")
        parameter_name = re.sub(r"[\t\n]", "", cols[0].text)
        parameter_in = re.sub(r"[\t\n]", "", cols[1].text)
        parameter_required = re.sub(r"[\t\n]", "", cols[2].text)
        parameter_type = re.sub(r"[\t\n]", "", cols[3].text)
        parameter_description = re.sub(r"[\t\n]", "", cols[4].text)
        parse_results.append(
            {
                "name": parameter_name,
                "name_formatted": re.sub(
                    "(?<!^)(?=[A-Z])", "_", parameter_name
                ).lower(),
                "in": parameter_in,
                "required": parameter_required,
                "type": parameter_type,
                "description": parameter_description,
            }
        )
    return parse_results


def parse_request_body(node):
    parse_result = []
    rows = node.find_all("tr")
    for row in rows:
        if row.find("th") is not None:
            continue
        cols = row.find_all("td")
        request_body_name = re.sub(r"[\t\n]", "", cols[0].text)
        request_body_type = re.sub(r"[\t\n]", "", cols[1].text)
        request_body_description = re.sub(r"[\t\n]", "", cols[2].text)
        parse_result.append(
            {
                "name": request_body_name,
                "type": request_body_type,
                "description": request_body_description,
            }
        )
    return parse_result


def parse_responses(node):
    parse_results = []
    rows = node.find_all("tr")
    for row in rows:
        if row.find("th") is not None:
            continue
        cols = row.find_all("td")
        response_name = re.sub(r"[\t\n]", "", cols[0].text)
        http_status_code = None
        if response_name.split()[0].isnumeric():
            http_status_code = int(response_name.split()[0])
            http_status_info = response_name.split()[1]
        else:
            http_status_info = response_name
        response_type = re.sub(r"[\t\n]", "", cols[1].text)
        response_description = re.sub(r"[\t\n]", "", cols[2].text)
        parse_results.append(
            {
                "http_status_code": http_status_code,
                "http_status_info": http_status_info,
                "type": response_type,
                "description": response_description,
            }
        )
    return parse_results


def parse_definitions(node):
    parse_results = []
    rows = node.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        definition = re.sub(r"[\t\n]", "", cols[0].text)
        parse_results.append(definition)
    return parse_results


def parse_definition(node):
    parse_results = []
    rows = node.find_all("tr")
    for row in rows:
        if row.find("th") is not None:
            continue
        cols = row.find_all("td")
        definition_name = re.sub(r"[\t\n]", "", cols[0].text)
        definition_type = re.sub(r"[\t\n]", "", cols[1].text)
        definition_description = re.sub(r"[\t\n]", "", cols[2].text)
        parse_results.append(
            {
                "name": definition_name,
                "type": definition_type,
                "description": definition_description,
            }
        )
    return parse_results
