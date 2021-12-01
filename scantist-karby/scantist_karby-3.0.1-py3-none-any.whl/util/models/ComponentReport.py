class ComponentReport:
    def __init__(self, library, version):
        self.field_names = [
            "Library",
            "Depth",
            "Version",
            "Latest Version",
            "File Path",
            "Vulnerabilities",
            "License",
            "Popularity",
            "Recommended upgrade",
            "Vulnerability List",
        ]
        self.info = {
            "Library": library,
            "Depth": "",
            "Version": version,
            "Latest Version": "",
            "File Path": "",
            "Vulnerabilities": "",
            "License": "",
            "Popularity": "",
            "Recommended upgrade": "",
            "Vulnerability List": [],
        }

    def set_field(self, key, value):
        if self.info.__contains__(key):
            self.info[key] = value
            return 0
        else:
            return 1

    def get_vul_list(self):
        return self.info["Vulnerability List"]

    def get_hash(self):
        return self.info['Library'] + " " + self.info['Version']