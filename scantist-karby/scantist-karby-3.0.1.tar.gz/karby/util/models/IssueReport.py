class IssueReport:
    def __init__(self, library, library_version, public_id):
        self.field_names = [
            "Library",
            "Library Version",
            "Public ID",
            "Score",
            "Description",
            "File Path",
            "Patched Version",
            "Latest Component Version",
            "Issue Source",
            "Issue Type",
            "Priority",
            "Comments",
        ]
        self.info = {
            "Library": library,
            "Library Version": library_version,
            "Public ID": public_id,
            "Score": "",
            "Description": "",
            "File Path": "",
            "Patched Version": "",
            "Latest Component Version": "",
            "Issue Source": "",
            "Issue Type": "",
            "Priority": "",
            "Comments": "",
        }

    def set_field(self, key, value):
        if self.info.__contains__(key):
            self.info[key] = value
            return 0
        else:
            return 1

    def get_hash(self):
        return f"{self.info['Library']} {self.info['Library Version']} {self.info['Public ID']}"
