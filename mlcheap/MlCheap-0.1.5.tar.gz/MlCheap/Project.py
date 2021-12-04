class Project:
    def __init__(self, name, labels_per_task, icon_id=""):
        self.name = name
        self.labels_per_task = labels_per_task
        self.icon_id = icon_id

    def to_dic(self):
        return {"project_name": self.name,
                "labels_per_task": self.labels_per_task,
                "icon_id": self.icon_id}
