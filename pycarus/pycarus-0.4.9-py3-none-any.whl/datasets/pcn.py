from pathlib import Path
from typing import Callable, List, Tuple

import open3d  # type: ignore
import torch
from torch.utils.data import Dataset

from pycarus.geometry.pcd import get_o3d_pcd_from_tensor
from pycarus.transforms.var import Compose

T_ITEM = Tuple[str, str, torch.Tensor, torch.Tensor]


class PCN(Dataset):
    def __init__(
        self,
        root: Path,
        split: str,
        categories: List[str] = [],
        download: bool = False,
        transforms_complete: List[Callable] = [],
        transforms_incomplete: List[Callable] = [],
        transforms_all: List[Callable] = [],
    ) -> None:
        """Class implementing the Point Completion Network dataset as proposed in:

        Yuan, W., Khot, T., Held, D., Mertz, C., & Hebert, M. (2018, September).
        Pcn: Point completion network.
        In 2018 International Conference on 3D Vision (3DV) (pp. 728-737). IEEE.

        Args:
            root: The path to the folder containing the dataset.
            split: The name of the split to load.
            categories: A list of categories id to select. Defaults to [].
            download: Defaults to False. Download not available for this dataset.
            transforms_complete: The transform to apply to the complete cloud. Defaults to [].
            transforms_incomplete: The transform to apply to the incomplete cloud. Defaults to [].
            transforms_all: The transform to apply to both the complete
                            and the incomplete cloud. Defaults to [].

        Raises:
            FileNotFoundError: If the folder does not exist.
            ValueError: If the chosen split is not allowed.
        """
        super().__init__()
        self.split = split
        self.splits = ["train", "val", "test", "test_novel"]
        if self.split not in self.splits:
            raise ValueError(f"{self.split} value not allowed, only allowed {self.splits}.")

        self.split = split if split != "val" else "valid"
        self.root = root
        if not download and not self.root.is_dir():
            raise FileNotFoundError(f"{self.root} not found.")

        self.transform_complete = Compose(transforms_complete)
        self.transform_incomplete = Compose(transforms_incomplete)
        self.transform_all = Compose(transforms_all)

        if download:
            if self.root.exists():
                print("Dataset root already exists, not downloading.")
            else:
                raise ValueError(
                    "Download not avaible for this dataset."
                    " You can manually download it at "
                    "https://drive.google.com/drive/folders/1P_W1tz5Q4ZLapUifuOE4rFAZp6L1XTJz"
                )

        self.list_file, cat_in_file = self.read_samples(
            self.root / f"{self.split}.list", categories
        )
        self.categories = categories if categories else cat_in_file

        new_list_file = []
        if self.split == "train":
            for f in self.list_file:
                for i in range(8):
                    file_name = f"{f}/{i:02d}.pcd"
                    new_list_file.append(file_name)
            self.list_file = new_list_file

    def __getitem__(self, index: int) -> T_ITEM:
        sample = self.list_file[index]
        id_category, name = sample.split("/")[0], sample.split("/")[1]

        if self.split == "train":
            path_to_end = Path(sample)
        else:
            pcd_name = Path(name) / "00.pcd" if self.split == "valid" else f"{name}.pcd"
            path_to_end = Path(id_category) / str(pcd_name)

        path_incomplete = self.root / self.split / "partial" / path_to_end
        pcd_o3d = open3d.io.read_point_cloud(str(path_incomplete))
        incomplete = torch.tensor(pcd_o3d.points, dtype=torch.float)

        incomplete = self.transform_all(self.transform_incomplete(incomplete))

        path_complete = self.root / self.split / "complete" / id_category / f"{name}.pcd"
        pcd_o3d = open3d.io.read_point_cloud(str(path_complete))
        complete = torch.tensor(pcd_o3d.points, dtype=torch.float)

        complete = self.transform_all(self.transform_complete(complete))

        return id_category, name, incomplete, complete

    def __len__(self) -> int:
        return len(self.list_file)

    @staticmethod
    def read_samples(path: Path, filter_categories: List[str]) -> Tuple[List[str], List[str]]:
        """Read a text file.

        Args:
            path: the path to the file to read.

        Returns:
            A tuple containing:
            - The list with one line of the file as sample.
            - The list of categories.
        """
        list_files: List[str] = []
        list_categories: List[str] = []
        with open(path, "rt") as f:
            for line in f.readlines():
                name_sample = line.rstrip()
                category = name_sample.split("/")[0]
                if category not in list_categories:
                    list_categories.append(category)

                if filter_categories:
                    if category in filter_categories:
                        list_files.append(name_sample)
                else:
                    list_files.append(name_sample)

        return list_files, list_categories

    @classmethod
    def show_item(cls, sample: T_ITEM) -> open3d.geometry.PointCloud:
        """Prepare one item in order to be visualized using open3D draw geometries.
        Args:
            sample: The sample to show.
        Returns:
            The point cloud to draw with open 3D.
        """
        _, _, incomplete, complete = sample
        pcd_incomplete = get_o3d_pcd_from_tensor(incomplete)

        complete = complete + torch.tensor([1.0, 0.0, 0.0])
        pcd_complete = get_o3d_pcd_from_tensor(complete)

        return pcd_complete + pcd_incomplete

    def get_categories(self) -> List[str]:
        """Get the list of loaded categories.

        Returns:
            A list containing the ids of the loaded categories.
        """
        return self.categories
