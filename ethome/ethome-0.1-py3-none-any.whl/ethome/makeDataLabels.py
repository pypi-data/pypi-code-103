def makeDataLabels(modality):
    if modality:
        if modality.shape[0]>1:
            dataLabels = []
            for k in range (1, modality.shape[0]):
                pass
        else:
            modality = modality[0]


    if modality == 'Suit':
        self.dataLabels = np.zeros(shape=(2, 66))
