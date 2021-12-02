class EmbeddingSaver:
    """
    TODO Description + Type annotations for everything
    """
    def __init__(self):
        self.feature_vector = []
        self.label_vector = []

    def __call__(self, module, input, output):
        for vec in output:
            self.feature_vector.append(vec.detach().cpu().numpy())

    def save_label(self, label):
        for lab in label:
            self.label_vector.append(lab)

    def clear(self):
        self.feature_vector = []
        self.label_vector = []
