from pathlib import Path
from typing import Callable, List, Tuple

import h5py  # type: ignore
import numpy as np
import open3d  # type: ignore
import torch
import torch.utils.data as data
from torch import Tensor

from pycarus.geometry.pcd import get_o3d_pcd_from_tensor
from pycarus.transforms.var import Compose

T_ITEM = Tuple[str, str, Tensor, Tensor]


class MVP(data.Dataset):
    def __init__(
        self,
        root: Path,
        split: str,
        num_points: int = 2048,
        novel_input: bool = True,
        novel_input_only: bool = False,
        categories: List[str] = [],
        download: bool = False,
        transforms_complete: List[Callable] = [],
        transforms_incomplete: List[Callable] = [],
        transforms_all: List[Callable] = [],
    ) -> None:
        """Class implementing the Completion3D dataset as proposed in:

        Pan, L., Chen, X., Cai, Z., Zhang, J., Zhao, H., Yi, S., & Liu, Z. (2021).
        Variational Relational Point Completion Network.
        In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 8524-8533).

        Args:
            root: The path to the folder containing the dataset.
            split: The name of the split to load. Allowed values: train, val, test.
            num_points: The resolution for groundtruth clouds. Allowed values: 2048, 4096, 8192, 16384.
            novel_input: Use the novel shapes introduced in MVP paper. Default True.
            novel_input_only: Use only the novel shapes introduced in MVP paper. Default True.
            categories: A list of categories id to select. Defaults to [].
            download: If True download the dataset using the "tmp" folder. Defaults to False.
            transforms_complete: The transform to apply to the complete cloud. Defaults to [].
            transforms_incomplete: The transform to apply to the incomplete cloud. Defaults to [].
            transforms_all: The transform to apply to both the complete
                            and the incomplete cloud. Defaults to [].

        Raises:
            FileNotFoundError: If the folder does not exist.
            ValueError: If the chosen split is not allowed.
            ValueError: If the chosen resolution is not allowed.
        """
        splits = ["train", "val", "test"]
        if split not in splits:
            raise ValueError(f"Split {split} not allowed, only {splits} are allowed.")

        val = split == "val"
        self.split = split if split != "val" else "train"

        self.num_points = num_points
        res_gt = [2048, 4096, 8192, 16384]
        if self.num_points not in res_gt:
            raise ValueError(f"{self.num_points} value not allowed, only {res_gt} are allowed.")

        self.root = root
        if not download and not self.root.is_dir():
            raise FileNotFoundError(f"{self.root} not found.")

        if download:
            if self.root.exists():
                print("Dataset root already exists, not downloading.")
            else:
                raise ValueError(
                    "Download not avaible for this dataset."
                    " You can manually download it at "
                    "https://paul007pl.github.io/projects/VRCNet.html"
                )

        self.transform_complete = Compose(transforms_complete)
        self.transform_incomplete = Compose(transforms_incomplete)
        self.transform_all = Compose(transforms_all)

        self.path_inc = self.root / f"mvp_{self.split}_input.h5"
        file_inc = h5py.File(self.path_inc, "r")
        self.incompletes = np.array(file_inc.get("incomplete_pcds"))
        self.labels = np.array(file_inc.get("labels"))
        incompletes_novel = np.array(file_inc.get("novel_incomplete_pcds"))
        labels_novel = np.array(file_inc.get("novel_labels"))
        file_inc.close()

        self.path_comp = self.root / f"mvp_{self.split}_gt_{self.num_points}pts.h5"
        file_comp = h5py.File(self.path_comp, "r")
        self.completes = np.array(file_comp.get("complete_pcds"))
        completes_novel = np.array(file_comp.get("novel_complete_pcds"))
        file_comp.close()

        if novel_input_only:
            self.incompletes = incompletes_novel
            self.completes = completes_novel
            self.labels = labels_novel
        elif novel_input:
            self.incompletes = np.concatenate((self.incompletes, incompletes_novel), axis=0)  # type: ignore
            self.completes = np.concatenate((self.completes, completes_novel), axis=0)  # type: ignore
            self.labels = np.concatenate((self.labels, labels_novel), axis=0)  # type: ignore

        self.indices = list(range(self.incompletes.shape[0]))
        if self.split != "test":
            val_indices = list(range(0, len(self.indices), 10))
            if val:
                self.indices = val_indices
            else:
                self.indices = [i for i in self.indices if i not in val_indices]

        self.all_categories = [
            "02691156",
            "02933112",
            "02958343",
            "03001627",
            "03636649",
            "04256520",
            "04379243",
            "04530566",
            "02818832",
            "02828884",
            "02871439",
            "02924116",
            "03467517",
            "03790512",
            "03948459",
            "04225987",
        ]
        self.categories = categories if categories else self.all_categories
        self.indices = self.filter_indices()

    def filter_indices(self) -> List[int]:
        filtered_indices = []
        for index in self.indices:
            label = int(self.labels[index])
            if self.all_categories[label] in self.categories:
                filtered_indices.append(index)
        return filtered_indices

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, index: int) -> T_ITEM:
        idx = self.indices[index]
        idx_complete = idx // 26
        idx_view = idx - idx_complete

        incomplete = torch.from_numpy((self.incompletes[idx]))
        complete = torch.from_numpy((self.completes[idx_complete]))

        incomplete = self.transform_all(self.transform_incomplete(incomplete))
        complete = self.transform_all(self.transform_complete(complete))

        label = torch.tensor(self.labels[idx], dtype=torch.long)
        category = self.all_categories[label]
        name = f"s{idx_complete}_v{idx_view:02d}"

        return category, name, incomplete, complete

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
