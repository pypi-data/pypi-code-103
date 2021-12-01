# coding=utf-8
from tf_geometric.datasets.csr_npz import CSRNPZDataset


class AmazonElectronicsDataset(CSRNPZDataset):

    def __init__(self, dataset_name, dataset_root_path=None):
        """

        :param dataset_name: "amazon-computers" | "amazon-photo"
        :param dataset_root_path:
        """
        super().__init__(dataset_name=dataset_name,
                         download_urls=[
                             "https://github.com/CrawlScript/gnn_datasets/raw/master/AmazonElectronics/{}.zip".format(dataset_name),
                             "http://cdn.zhuanzhi.ai/github/{}.zip".format(dataset_name)
                         ],
                         download_file_name="{}.zip".format(dataset_name),
                         cache_name=None,
                         dataset_root_path=dataset_root_path,
                         )


class AmazonComputersDataset(AmazonElectronicsDataset):

    def __init__(self, dataset_root_path=None):
        super().__init__("amazon-computers", dataset_root_path=dataset_root_path)


class AmazonPhotoDataset(AmazonElectronicsDataset):

    def __init__(self, dataset_root_path=None):
        super().__init__("amazon-photo", dataset_root_path=dataset_root_path)
