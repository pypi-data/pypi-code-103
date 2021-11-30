import os


try:
    import bs4
    import requests
    import tqdm

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


__func_alias__ = {"type_": "type"}


def parse(hub, api_url: str):
    plugins = {}

    with requests.get(f"{api_url}/en-us/rest/api") as response:
        html = response.text
    soup = bs4.BeautifulSoup(html, "lxml")

    resources = []
    num = 1
    while num:
        q = soup.find("meta", {"name": f"quickFilterColumn{num}"})

        if q:
            r = q.attrs["content"].split(",")
            resources.extend(r)
        else:
            break
        num += 1

    for r in tqdm.tqdm(resources):
        ref = f"{r}"
        if ref.lower() == "azure":
            file_path = os.path.dirname(__file__) + "/resource/azure-rest-api.html"
        else:
            hub.log.error(f"{ref} is not a supported resource.")
            continue
        # url = f"https://docs.microsoft.com/en-us/rest/api/?view={r}"
        new_plugins = hub.pop_create.azure.api_reference.parse(file_path)

        for k, v in new_plugins.items():
            ref = f"{hub.tool.format.case.snake(r)}.{hub.tool.format.case.snake(k)}"
            plugins[ref] = v

    return plugins
