import requests
from getpass import getpass
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz


class QueryError(Exception):
    pass


class Query:
    def __init__(self, username: str = None, password: str = None, **_):
        self.username = username or input("Username: ")
        self.password = password or getpass("Password: ")

    def __call__(self, oname: str = None, surname: str = None, type_="any", **_):
        """Query durham's directory for email matches for the user in question."""
        if not any((oname, surname)):
            raise ValueError("At least one of oname or surname must be provided.")
        type_ = type_ or "any"
        if type_ not in ["any", "staff", "student"]:
            raise ValueError("type_ must be one of 'any', 'staff', 'student' or unset.")
        args = dict(
            mode="finda",
            ss={"staff": "s", "student": "u", "any": None}[type_],
            on=oname,
            sn=surname,
        )
        URL = "https://www.dur.ac.uk/directory/password"
        resp = requests.get(URL, params=args, auth=(self.username, self.password))
        if "No results found for this search" in resp.text:
            name = " ".join(x for x in (oname, surname) if x)
            raise QueryError(f"No results found for {name} of type {type_}.")

        soup = BeautifulSoup(resp.text, features="lxml")
        err = soup.find(class_="error")
        if err:
            raise QueryError(err.text)

        results = soup.find("table", id="directoryresults")
        keys, *rows = results.find_all("tr")
        keys = [x.text for x in keys.find_all("th")]
        return [dict(zip(keys, (x.text for x in row.find_all("td")))) for row in rows]


def select(options: list[str], target: str):
    def _fuzzy_sort_results(result):
        name = result[1].split(" ", 1)[1]
        return fuzz.token_sort_ratio(name, target)

    print(f"Multiple options for {target}, please choose:")
    options = sorted(enumerate(options), key=_fuzzy_sort_results, reverse=True)[:30]
    while True:
        for i, (_, row) in enumerate(options):
            print(f"[{i}] {row}")
        try:
            choice = input("Choice: ")
            choice = int(choice)
        except Exception:
            if choice.lower().strip() == "q":
                raise QueryError("Selection Aborted")
        else:
            if choice in range(len(options)):
                return options[choice][0]

        print("Invalid input")


class QueryOne(Query):
    """Query and return only *one* candidate."""

    def __call__(self, **kwargs):
        results = super().__call__(**kwargs)
        if not results:
            return None
        if len(results) == 1:
            return results[0]
        else:
            target = " ".join((kwargs.get("oname", ""), kwargs.get("surname", "")))
            choice = select(
                [
                    f'{row["Name"]} {row.get("Course") or row["Job/Role"]}'
                    for row in results
                ],
                target.strip(),
            )
            return results[choice]


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--surname", help="Surname")
    parser.add_argument("--oname", help="Other name[s] or initial[s]")
    parser.add_argument("--user", dest="username", help="Username for login.")
    parser.add_argument("--password", help="Password for login.")
    parser.add_argument(
        "--type", dest="type_", help="Student, Staff or Any (default is any)"
    )
    args = parser.parse_args()
    query = Query(**args.__dict__)
    resp = query(**args.__dict__)
    if resp:
        widths = {"Name": 25, "Department": 30, "Job/Role": 40, "Telephone": 8}
        headers = resp[0].keys()
        print(" ".join(f"{k:<{widths.get(k, 30)}}" for k in headers))
        print("-" * sum(widths.values()), end="")
        print("-" * 30 * (len(headers) - len(widths)), end="")
        print("-" * len(headers))

        for row in resp:
            for k, v in row.items():
                width = widths.get(k, 30)
                print(f"{v[:width]:<{width}} ", end="")
            print()
    else:
        print("No results found...")
