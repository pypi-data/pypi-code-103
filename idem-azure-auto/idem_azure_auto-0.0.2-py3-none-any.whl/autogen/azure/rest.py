import re


try:
    import bs4
    import requests

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0"
}


def parse(hub, url: str, desc: str):
    """
    Parse a url like this: https://docs.microsoft.com/en-us/rest/api/power-bi/available-features
    Check all the "Operations" for Get, List, Delete, and Create
    If we have all of those then create a plugin with "present", "absent", and "describe" functions
    """
    plugin = {}
    api_plugin = {}
    relative_links = set()

    # Define a helper function to determine resources available given a URL
    def resource_(url, page):
        """
        Find the primary API group given a URL.

        Since the URL has the primary candidate for a valid API, check the page itself
        and determine if it's modified. If so, return the correct format.
        :return:
        """
        potential = None
        tag = None
        op_groups = []
        candidate = url.strip("/").split("/")[-1]

        # Find a secondary candidate and cache the operation tag objects while we have them
        if page.find("h2", text="REST operation groups"):
            op_groups = page.find("h2", text="REST operation groups").parent.find_all(
                "td"
            )
            tag = op_groups[0]
        elif page.find("h2", {"id": "rest-operation-groups"}):
            op_groups = page.find(
                "h2", {"id": "rest-operation-groups"}
            ).parent.find_all("td")
            tag = op_groups[0]
        else:
            pass

        try:
            name_dict = tag.contents[0].attrs
        except Exception:
            hub.log.debug(f"We caught a general error for {url}")
        else:
            potential = name_dict.get("href")

        # Determine if modifications are needed and send them back
        temp = re.sub(r"\W+", "", candidate)
        if not potential or temp in potential:
            base_url = url.split(candidate)[0]
            url = base_url + temp
            candidate = temp
        return candidate, op_groups, url

    with requests.get(url) as response:
        html = response.text

    page = bs4.BeautifulSoup(html, "lxml")
    api, operation_groups, url = resource_(url, page)

    for tag in operation_groups:
        try:
            temp = tag.contents[0].attrs.get("href").split(api)[-1].strip("/")
        except (
            AttributeError,
            IndexError,
        ):
            # Exception thrown because parsing a tag doesn't contain a valid resource so skip it
            hub.log.debug(
                f"We caught an AttributeError or IndexError for {url}\nThis is likely because a resource was not valid so pass."
            )
        else:
            resource = temp
            if not resource == "relative-path" and resource is not None:
                rel_link = f"{url}/{resource}"
                relative_links.add(rel_link)

    # Determine operations on a per resource basis
    operation_groups = []
    for link in relative_links:
        # Create a local list of acceptable article declarations
        resource = link.split("/")[-1]
        allowables = [
            f"{resource}/create",
            f"{resource}/create-or-update",
            f"{resource}/update",
            f"{resource}/update-tags",
            f"{resource}/get",
            f"{resource}/delete",
            f"{resource}/list",
            f"{resource}/list-all",
        ]
        with requests.get(link, headers=HEADERS) as resp:
            html = resp.text
        page = bs4.BeautifulSoup(html, "lxml")

        # Create a local cache of links to build return after we find all available
        api_cache = []
        for item in page.find_all("a", {"data-linktype": "relative-path"}):
            resource_ext = item.attrs["href"]
            plugin["resource"] = resource
            if resource_ext in allowables:
                api_cache.append(resource_ext)
        for entry in api_cache:
            entry = f"{url}/{entry}"
            # Build out the return dict
            if "create" in entry:
                plugin["create"] = entry
            elif "update" in entry:
                plugin["update"] = entry
            elif "get" in entry:
                plugin["get"] = entry
            elif "delete" in entry:
                plugin["delete"] = entry
            elif "list-all" in entry:
                plugin["list"] = entry
            elif "list" in entry:
                plugin["list"] = entry
        operation_groups.append(plugin.copy())
    api_plugin[api] = operation_groups
    return api_plugin
