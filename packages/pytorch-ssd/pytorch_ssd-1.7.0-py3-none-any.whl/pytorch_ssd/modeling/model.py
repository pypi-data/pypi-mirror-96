"""SSD model."""
import logging
from argparse import ArgumentParser
from typing import Any, Iterable, List, Optional, Tuple

import pytorch_lightning as pl
import torch
import torch.nn.functional as functional
import wandb
from torch.utils.data.dataloader import DataLoader
from torchvision.ops.boxes import batched_nms

from pytorch_ssd.args import comma_separated, eq2kwargs, str2bool
from pytorch_ssd.data.bboxes import (
    center_bbox_to_corner_bbox,
    convert_locations_to_boxes,
)
from pytorch_ssd.data.datasets import datasets, onehot_labels
from pytorch_ssd.data.priors import process_prior
from pytorch_ssd.data.transforms import (
    DataTransform,
    SSDTargetTransform,
    TrainDataTransform,
)
from pytorch_ssd.modeling.backbones import backbones
from pytorch_ssd.modeling.box_predictors import box_predictors
from pytorch_ssd.modeling.loss import MultiBoxLoss
from pytorch_ssd.modeling.metrics import MeanAveragePrecision
from pytorch_ssd.modeling.visualize import denormalize, get_boxes

logger = logging.getLogger(__name__)
optimizers = {"Adam": torch.optim.Adam, "SGD": torch.optim.SGD}
lr_schedulers = {
    # name: optimizer, interval, var to monitor
    "StepLR": (torch.optim.lr_scheduler.StepLR, "step", None),
    "MultiStepLR": (torch.optim.lr_scheduler.MultiStepLR, "step", None),
    "ExponentialLR": (torch.optim.lr_scheduler.ExponentialLR, "epoch", None),
    "CosineAnnealingLR": (torch.optim.lr_scheduler.CosineAnnealingLR, "step", None),
    "ReduceLROnPlateau": (
        torch.optim.lr_scheduler.ReduceLROnPlateau,
        "epoch",
        "val_loss",
    ),
    "CyclicLR": (torch.optim.lr_scheduler.CyclicLR, "step", None),
    "CosineAnnealingWarmRestarts": (
        torch.optim.lr_scheduler.CosineAnnealingWarmRestarts,
        "step",
        None,
    ),
}


class SSD(pl.LightningModule):
    """SSD Detector class."""

    def __init__(
        self,
        dataset_name: str,
        data_dir: str,
        optimizer: str = "Adam",
        learning_rate: float = 1e-3,
        optimizer_kwargs: Optional[List[Tuple[str, Any]]] = None,
        lr_scheduler: str = "",
        lr_scheduler_kwargs: Optional[List[Tuple[str, Any]]] = None,
        auto_lr_find: bool = False,
        batch_size: int = 32,
        num_workers: int = 8,
        pin_memory: bool = True,
        n_classes: Optional[int] = None,
        flip_train: bool = False,
        augment_colors_train: bool = False,
        strong_crop: bool = False,
        backbone_name: str = "VGG300",
        use_pretrained_backbone: bool = False,
        backbone_out_channels: Optional[List[int]] = None,
        backbone_feature_maps: Optional[List[int]] = None,
        backbone_min_sizes: Optional[List[float]] = None,
        backbone_max_sizes: Optional[List[float]] = None,
        backbone_strides: Optional[List[int]] = None,
        backbone_aspect_ratios: Optional[List[Tuple[int, ...]]] = None,
        predictor_name: str = "SSD",
        image_size: Tuple[int, int] = (300, 300),
        center_variance: float = 0.1,
        size_variance: float = 0.2,
        iou_threshold: float = 0.5,
        drop_small_boxes: bool = True,
        confidence_threshold: float = 0.8,
        nms_threshold: float = 0.45,
        max_per_image: int = 100,
        negative_positive_ratio: float = 3,
        calculate_map: bool = True,
        map_iou_threshold: float = 0.5,
        visualize: bool = True,
        **_kwargs,
    ):
        """
        :param dataset_name: used dataset name
        :param data_dir: dataset data directory path
        :param optimizer: optimizer name
        :param learning_rate: learning rate
        :param optimizer_kwargs: optimizer argumnets dictionary
        :param lr_scheduler: LR scheduler name
        :param lr_scheduler_kwargs: LR scheduler arguments dictionary
        :param auto_lr_find: perform auto lr finding
        :param batch_size: mini-batch size for training
        :param num_workers: number of workers for dataloader
        :param pin_memory: pin memory for training
        :param n_classes: number of classes (if 2 then no classification),
            defaults to number of classes in the dataset
        :param flip_train: perform random flipping on train images
        :param augment_colors_train: perform random colors augmentation on train images
        :param strong_crop: crop input images to input shape before augmentation
        :param backbone_name: used backbone name
        :param use_pretrained_backbone: download pretrained weights for backbone
        :param backbone_out_channels: output channels of backbone (None for default)
        :param backbone_feature_maps: number of feature maps in each backbone output
        :param backbone_min_sizes: minimal sizes of objects in each feature map
        :param backbone_max_sizes: maximal sizes of objects in each feature map
        :param backbone_strides: backbone strides used in each feature map
        :param backbone_aspect_ratios: aspect ratios for each backbone feature map
        :param predictor_name: used predictor name
        :param image_size: image size tuple
        :param center_variance: SSD center variance
        :param size_variance: SSD size variance
        :param iou_threshold: IOU threshold for anchors
        :param drop_small_boxes: drop small bounding boxes when training
        :param confidence_threshold: min prediction confidence to use as detection
        :param nms_threshold: non-max suppression IOU threshold
        :param max_per_image: max number of detections per image
        :param negative_positive_ratio: the ratio between the negative examples and
            positive examples for calculating loss
        :param calculate_map: calculate mean average precision during training
        :param map_iou_threshold: mean average precision iou threshold
        :param visualize: perform visualization during training
        """
        super().__init__()
        self.dataset = datasets[dataset_name]
        self.data_dir = data_dir
        if n_classes is None:
            n_classes = len(self.dataset.CLASS_LABELS) + 1
        self.class_labels = (
            self.dataset.CLASS_LABELS if n_classes != 2 else [self.dataset.OBJECT_LABEL]
        )
        backbone = backbones[backbone_name]
        backbone_kwargs = {
            "out_channels": backbone_out_channels,
            "feature_maps": backbone_feature_maps,
            "min_sizes": backbone_min_sizes,
            "max_sizes": backbone_max_sizes,
            "strides": backbone_strides,
            "aspect_ratios": backbone_aspect_ratios,
        }
        if any(kwarg is None for kwarg in backbone_kwargs):
            backbone_kwargs = {}
        self.backbone = backbone(
            use_pretrained=use_pretrained_backbone, **backbone_kwargs
        )
        predictor = box_predictors[predictor_name]
        self.predictor = predictor(
            n_classes=n_classes,
            backbone_out_channels=self.backbone.out_channels,
            backbone_boxes_per_loc=self.backbone.boxes_per_loc,
        )
        self.anchors = process_prior(
            image_size=image_size,
            feature_maps=self.backbone.feature_maps,
            min_sizes=self.backbone.min_sizes,
            max_sizes=self.backbone.max_sizes,
            strides=self.backbone.strides,
            aspect_ratios=self.backbone.aspect_ratios,
        )
        self.target_transform = SSDTargetTransform(
            anchors=self.anchors,
            image_size=image_size,
            n_classes=n_classes,
            center_variance=center_variance,
            size_variance=size_variance,
            iou_threshold=iou_threshold,
            drop_small_boxes=drop_small_boxes,
        )
        self.image_size = image_size
        self.center_variance = center_variance
        self.size_variance = size_variance
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.max_per_image = max_per_image
        self.negative_positive_ratio = negative_positive_ratio

        self.optimizer = optimizers[optimizer]
        if optimizer_kwargs is None:
            optimizer_kwargs = []
        self.optimizer_kwargs = dict(optimizer_kwargs)
        self.lr = learning_rate
        self.lr_scheduler: Optional[object]
        self.lr_freq: Optional[str]
        self.lr_metric: Optional[str]
        self.lr_scheduler, self.lr_freq, self.lr_metric = lr_schedulers.get(
            lr_scheduler, (None, None, None)
        )
        if lr_scheduler_kwargs is None:
            lr_scheduler_kwargs = []
        self.lr_scheduler_kwargs = dict(lr_scheduler_kwargs)
        self.auto_lr_find = auto_lr_find
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.n_classes = n_classes
        self.flip_train = flip_train
        self.augment_colors_train = augment_colors_train
        self.strong_crop = strong_crop
        self.calculate_map = calculate_map
        self.map_iou_threshold = map_iou_threshold
        self.visualize = visualize

        self.map = MeanAveragePrecision(iou_threshold=self.map_iou_threshold)

        self.save_hyperparameters()

    @staticmethod
    def add_model_specific_args(parent_parser: ArgumentParser):
        """Add SSD args to parent argument parser."""
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument(
            "--dataset_name",
            type=str,
            default="MNIST",
            help=f"Used dataset name. Available: {list(datasets.keys())}",
        )
        parser.add_argument(
            "--data_dir", type=str, default="data", help="Dataset files directory"
        )
        parser.add_argument(
            "--optimizer",
            type=str,
            default="Adam",
            help=f"Used optimizer. Available: {list(optimizers.keys())}",
        )
        parser.add_argument(
            "--learning_rate",
            type=float,
            default=1e-3,
            help="Learning rate used for training the model",
        )
        parser.add_argument(
            "--optimizer_kwargs",
            type=eq2kwargs,
            default=[],
            nargs="*",
            help="Optimizer kwargs in the form of key=value separated by spaces",
        )
        parser.add_argument(
            "--lr_scheduler",
            type=str,
            default="None",
            help=(
                "Used LR scheduler. "
                f"Available: {list(lr_schedulers.keys())}; default: None"
            ),
        )
        parser.add_argument(
            "--lr_scheduler_kwargs",
            type=eq2kwargs,
            default=[],
            nargs="*",
            help="LR scheduler kwargs in the form of key=value separated by spaces",
        )
        parser.add_argument(
            "--batch_size",
            type=int,
            default=32,
            help="Mini-batch size used for training the model",
        )
        parser.add_argument(
            "--num_workers",
            type=int,
            default=8,
            help="Number of workers used to load the dataset",
        )
        parser.add_argument(
            "--pin_memory",
            type=str2bool,
            nargs="?",
            const=True,
            default=True,
            help="Pin data in memory while training",
        )
        parser.add_argument(
            "--n_classes",
            type=int,
            default=None,
            help="Number of classes used for training. "
            "If == 2 then only detection without classification",
        )
        parser.add_argument(
            "--backbone_name",
            type=str,
            default="VGG300",
            help=f"Used backbone name. Available: {list(backbones.keys())}",
        )
        parser.add_argument(
            "--use_pretrained_backbone",
            type=str2bool,
            nargs="?",
            const=True,
            default=False,
            help="Start off from pretrained weights from torchvision",
        )
        parser.add_argument(
            "--backbone_out_channels",
            nargs="+",
            type=int,
            default=None,
            help="Output channels of backbone (None for default)",
        )
        parser.add_argument(
            "--backbone_feature_maps",
            nargs="+",
            type=int,
            default=None,
            help="Number of feature maps in each backbone output (None for default)",
        )
        parser.add_argument(
            "--backbone_min_sizes",
            nargs="+",
            type=float,
            default=None,
            help="Maximal sizes of objects in each feature map (None for default)",
        )
        parser.add_argument(
            "--backbone_max_sizes",
            nargs="+",
            type=float,
            default=None,
            help="Minimal sizes of objects in each feature map (None for default)",
        )
        parser.add_argument(
            "--backbone_strides",
            nargs="+",
            type=int,
            default=None,
            help="Backbone strides used in each feature map (None for default)",
        )
        parser.add_argument(
            "--backbone_aspect_ratios",
            nargs="+",
            type=comma_separated,
            default=None,
            help="Aspect ratios for each backbone feature map (None for default)",
        )
        parser.add_argument(
            "--predictor_name",
            type=str,
            default="SSD",
            help=f"Used box predictor name. Available: {list(box_predictors.keys())}",
        )
        parser.add_argument(
            "--image_size",
            nargs=2,
            type=int,
            default=[300, 300],
            help="Size of the model input image",
        )
        parser.add_argument(
            "--center_variance", type=float, default=0.1, help="SSD box center variance"
        )
        parser.add_argument(
            "--size_variance", type=float, default=0.2, help="SSD box size variance"
        )
        parser.add_argument(
            "--iou_threshold", type=float, default=0.5, help="IOU threshold for anchors"
        )
        parser.add_argument(
            "--drop_small_boxes",
            type=str2bool,
            nargs="?",
            const=True,
            default=True,
            help="Drop small bounding boxes when training",
        )
        parser.add_argument(
            "--confidence_threshold",
            type=float,
            default=0.8,
            help="Minimum prediction confidence to approve during inference",
        )
        parser.add_argument(
            "--nms_threshold",
            type=float,
            default=0.45,
            help="Non-max suppression IOU threshold",
        )
        parser.add_argument(
            "--max_per_image",
            type=int,
            default=100,
            help="Max number of detections returned per image during inference",
        )
        parser.add_argument(
            "--negative_positive_ratio",
            type=float,
            default=3,
            help="Ratio between negative and positive examples for loss",
        )
        parser.add_argument(
            "--flip_train",
            type=str2bool,
            nargs="?",
            const=True,
            default=False,
            help="Flip train images during training",
        )
        parser.add_argument(
            "--augment_colors_train",
            type=str2bool,
            nargs="?",
            const=True,
            default=False,
            help="Perform random colors augmentation during training",
        )
        parser.add_argument(
            "--strong_crop",
            type=str2bool,
            nargs="?",
            const=True,
            default=False,
            help="Crop input images to input shape before augmentation",
        )
        parser.add_argument(
            "--calculate_map",
            type=str2bool,
            nargs="?",
            const=True,
            default=True,
            help="Calculate Mean Average Precision during training",
        )
        parser.add_argument(
            "--map_iou_threshold",
            type=float,
            default=0.5,
            help="Mean Average Precision metric Intersection over Union threshold",
        )
        parser.add_argument(
            "--visualize",
            type=str2bool,
            nargs="?",
            const=True,
            default=True,
            help="Log visualizations of model predictions",
        )
        return parser

    def process_model_output(
        self, detections: Tuple[torch.Tensor, torch.Tensor], confidence_threshold: float
    ) -> Iterable[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """Process model output with non-max suppression.

        :param detections: tuple of class logits and bounding box regressions
        :param confidence_threshold: min detection confidence threshold
        :return: iterable of tuples containing bounding boxes, scores and labels
        """
        width, height = self.image_size
        scores_batches, boxes_batches = detections
        batch_size = scores_batches.size(0)
        for batch_idx in range(batch_size):
            scores = scores_batches[batch_idx]  # (N, num_classes)
            boxes = boxes_batches[batch_idx]  # (N, 4)
            n_boxes, n_classes = scores.shape

            boxes = boxes.view(n_boxes, 1, 4).expand(n_boxes, n_classes, 4)
            labels = torch.arange(n_classes)
            labels = labels.view(1, n_classes).expand_as(scores)

            # remove predictions with label == background
            boxes = boxes[:, 1:]
            scores = scores[:, 1:]
            labels = labels[:, 1:]

            # batch everything, by making every class prediction a separate instance
            boxes = boxes.reshape(-1, 4)
            scores = scores.reshape(-1)
            labels = labels.reshape(-1)

            # remove low scoring boxes
            approved_mask = (
                (scores > confidence_threshold).nonzero(as_tuple=False).squeeze(1)
            )
            boxes = boxes[approved_mask]
            scores = scores[approved_mask]
            labels = labels[approved_mask]

            # reshape boxes to image size
            boxes[:, 0::2] *= width
            boxes[:, 1::2] *= height

            # as of torchvision 0.6.0, cuda nms is broken (int overflow)
            try:
                keep_mask = batched_nms(
                    boxes=boxes,
                    scores=scores,
                    idxs=labels,
                    iou_threshold=self.nms_threshold,
                )
            except RuntimeError:
                logger.warning(
                    "Torchvision NMS CUDA int overflow. Falling back to CPU."
                )
                keep_mask = batched_nms(
                    boxes=boxes.cpu(),
                    scores=scores.cpu(),
                    idxs=labels.cpu(),
                    iou_threshold=self.nms_threshold,
                )
            # keep only top scoring predictions
            keep_mask = keep_mask[: self.max_per_image]
            boxes = boxes[keep_mask]
            scores = scores[keep_mask]
            labels = labels[keep_mask]

            yield boxes, scores, labels

    def process_model_prediction(
        self,
        cls_logits: torch.Tensor,
        bbox_pred: torch.Tensor,
        confidence_threshold: Optional[float] = None,
    ) -> List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """Get readable results from model predictions.

        :param cls_logits: class predictions from model
        :param bbox_pred: bounding box predictions from model
        :param confidence_threshold: optional param to override default threshold
        :return: list of predictions - tuples of boxes, scores and labels
        """
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
        if len(cls_logits.shape) == 3:
            scores = functional.softmax(cls_logits, dim=2)
        else:
            scores = onehot_labels(labels=cls_logits, n_classes=self.n_classes)
        boxes = convert_locations_to_boxes(
            locations=bbox_pred,
            priors=self.anchors.to(bbox_pred.device),
            center_variance=self.center_variance,
            size_variance=self.size_variance,
        )
        boxes = center_bbox_to_corner_bbox(boxes)
        detections = self.process_model_output(
            detections=(scores, boxes), confidence_threshold=confidence_threshold
        )
        return list(detections)

    def forward(
        self, images: torch.Tensor
    ) -> List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """Forward function for inference."""
        features = self.backbone(images)
        cls_logits, bbox_pred = self.predictor(features)
        return self.process_model_prediction(cls_logits, bbox_pred)

    def common_run_step(
        self,
        batch: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
        batch_nb: int,
        stage: str,
    ):
        """Common model running step for training and validation."""
        criterion = MultiBoxLoss(self.negative_positive_ratio)

        images, locations, labels = batch

        features = self.backbone(images)
        cls_logits, bbox_pred = self.predictor(features)

        regression_loss, classification_loss = criterion(
            confidence=cls_logits,
            predicted_locations=bbox_pred,
            labels=labels,
            gt_locations=locations,
        )
        loss = regression_loss + classification_loss

        self.log(f"{stage}_loss", loss, prog_bar=False, logger=True)
        self.log(
            f"{stage}_regression_loss", regression_loss, prog_bar=False, logger=True
        )
        self.log(
            f"{stage}_classification_loss",
            classification_loss,
            prog_bar=False,
            logger=True,
        )

        if batch_nb == 0:  # perform at the beginning of each epoch
            if self.calculate_map:
                predictions = self.process_model_prediction(
                    cls_logits.detach(), bbox_pred.detach()
                )
                ground_truth = self.process_model_prediction(
                    labels.detach(), locations.detach()
                )
                self.logger.experiment.log(
                    {f"{stage}_map": self.map(predictions, ground_truth)},
                    step=self.global_step,
                )

            if self.visualize:
                image = images[0].detach().permute(1, 2, 0)
                image = denormalize(
                    image,
                    pixel_mean=self.backbone.PIXEL_MEANS,
                    pixel_std=self.backbone.PIXEL_STDS,
                )

                ((gt_boxes, gt_scores, gt_labels),) = self.process_model_prediction(
                    labels[0].detach().unsqueeze(0),
                    locations[0].detach().unsqueeze(0),
                    confidence_threshold=0.0,
                )
                ((boxes, scores, labels),) = self.process_model_prediction(
                    cls_logits[0].detach().unsqueeze(0),
                    bbox_pred[0].detach().unsqueeze(0),
                    confidence_threshold=0.0,
                )
                log_boxes = get_boxes(
                    gt_boxes=gt_boxes.cpu(),
                    gt_scores=gt_scores.cpu(),
                    gt_labels=gt_labels.cpu(),
                    boxes=boxes.cpu(),
                    scores=scores.cpu(),
                    labels=labels.cpu(),
                    class_labels=self.class_labels,
                )
                log_image = wandb.Image(
                    image.cpu().numpy(),
                    boxes=log_boxes,
                    caption="object detection predictions",
                )
                self.logger.experiment.log(
                    {f"{stage}_predictions": log_image}, step=self.global_step
                )

        return loss

    def training_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor, torch.Tensor], batch_nb: int
    ):
        """Step for training."""
        return self.common_run_step(batch, batch_nb, stage="train")

    def validation_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor, torch.Tensor], batch_nb: int
    ):
        """Step for validation."""
        return self.common_run_step(batch, batch_nb, stage="val")

    def configure_optimizers(self):
        """Configure training optimizer."""
        optimizer = self.optimizer(
            self.parameters(), lr=self.lr, **self.optimizer_kwargs
        )
        configuration = {"optimizer": optimizer}
        if self.lr_scheduler is not None:
            lr_scheduler = self.lr_scheduler(
                optimizer=optimizer, **self.lr_scheduler_kwargs
            )
            configuration["lr_scheduler"] = {
                "scheduler": lr_scheduler,
                "interval": self.lr_freq,
            }
            if self.lr_metric is not None:
                configuration["lr_scheduler"]["monitor"] = self.lr_metric
        return configuration

    def train_dataloader(self) -> DataLoader:
        """Prepare train dataloader."""
        data_transform = TrainDataTransform(
            image_size=self.image_size,
            pixel_mean=self.backbone.PIXEL_MEANS,
            pixel_std=self.backbone.PIXEL_STDS,
            flip=self.flip_train,
            augment_colors=self.augment_colors_train,
            strong_crop=self.strong_crop,
        )
        dataset = self.dataset(
            self.data_dir,
            data_transform=data_transform,
            target_transform=self.target_transform,
            subset="train",
        )
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            shuffle=True,
        )

    def val_dataloader(self) -> DataLoader:
        """Prepare validation dataloader."""
        data_transform = DataTransform(
            image_size=self.image_size,
            pixel_mean=self.backbone.PIXEL_MEANS,
            pixel_std=self.backbone.PIXEL_STDS,
        )
        dataset = self.dataset(
            self.data_dir,
            data_transform=data_transform,
            target_transform=self.target_transform,
            subset="test",
        )
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
