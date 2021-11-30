import logging

try:
    import bs4
    import tqdm

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def parse(hub, file_path: str, base_url="https://docs.microsoft.com"):
    """
    Parse a page such as this one: https://docs.microsoft.com/en-us/rest/api/?view=Azure

    Create a pretty version of a list of Azure services"
    """
    plugins = {}
    with open(file_path) as f:
        html = f.read()
    soup = bs4.BeautifulSoup(html, "lxml")

    # Parse page and get links, names, and descriptions of each Azure service
    parsing_results = []
    api_table = soup.find(class_="api-search-results")
    table_body = api_table.find("tbody")
    for row in table_body.find_all("tr"):
        try:
            cols = row.find_all("td")
            parsing_result = {
                "name": cols[0].find("a").text,
                "url": base_url + cols[0].find("a")["href"],
                "description": cols[1].text,
            }
            parsing_results.append(parsing_result)
        except [AttributeError, KeyError] as parse_error:
            logging.error(
                f"Fail to parse table from file {file_path} at row {str(row)}. Error: {parse_error}"
            )

    for api_reference_data in tqdm.tqdm(parsing_results):
        plugins[api_reference_data["name"]] = hub.pop_create.azure.rest.parse(
            url=api_reference_data["url"], desc=api_reference_data["description"]
        )

    return plugins
