"""Base class for dataset."""
from abc import ABC
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import torch
import torch.utils.data as data

DataTransformType = Optional[
    Callable[
        [torch.Tensor, Optional[torch.Tensor], Optional[torch.Tensor]],
        Tuple[torch.Tensor, Optional[torch.Tensor], Optional[torch.Tensor]],
    ]
]
TargetTransformType = Optional[
    Callable[[torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]
]


class BaseDataset(data.Dataset, ABC):

    CLASS_LABELS: List[str] = []
    OBJECT_LABEL = ""

    def __init__(
        self,
        data_dir: str,
        data_transform: DataTransformType = None,
        target_transform: TargetTransformType = None,
        subset: str = "train",
    ):
        """
        :param data_dir: directory with data for the dataset
        :param data_transform: transforms to apply to both images and targets
        :param target_transform: transforms to apply to targets
        :param subset: subset to use
        """
        self.data_dir: Path = Path(data_dir)
        self.data_transform: DataTransformType = data_transform
        self.target_transform: TargetTransformType = target_transform
        self.subset = subset

    def __getitem__(self, item) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        image = self._get_image(item)
        boxes, labels = self._get_annotation(item)
        if self.data_transform is not None:
            image, boxes, labels = self.data_transform(image, boxes, labels)
        if self.target_transform is not None:
            boxes, labels = self.target_transform(boxes, labels)
        if boxes.numel() == 0:
            item += 1
            if item >= len(self):
                item = 0
            return self.__getitem__(item)
        return image, boxes, labels

    def _get_image(self, item: int) -> torch.Tensor:
        """Get image from the dataset."""
        raise NotImplementedError

    def _get_annotation(self, item: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get annotations (boxes and labels) from the dataset."""
        raise NotImplementedError

    def __len__(self):
        """Get length of the dataset."""
        raise NotImplementedError

    @classmethod
    def download(cls, path: str):
        """Download dataset files."""
        raise NotImplementedError(f"{cls.__name__} does not implement downloading.")


def onehot_labels(labels: torch.Tensor, n_classes: int):
    """Convert loaded labels to one-hot form.

    :param labels: tensor of shape (batch_size x n_cells) with integers indicating class
    :param n_classes: number of classes
    :return: tensor of shape (batch_size x n_cells x n_classes) with one-hot encodings
    """
    onehot = torch.zeros((*labels.shape[:2], n_classes), device=labels.device)
    onehot.scatter_(-1, labels.unsqueeze(-1), 1.0)
    return onehot
