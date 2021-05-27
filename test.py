import sys,os,time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import scipy.ndimage
from skimage.io import imread, imsave
from skimage.transform import rotate

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from utils import LARGE_CHIP_SIZE, CHIP_SIZE, MixedLoss, NUM_WORKERS, joint_transform, mixed_loss
from tqdm import tqdm

from dataloader import AirbusShipPatchDataset, AirbusShipDataset
from streaming_dataloader import StreamingShipDataset, StreamingShipValTestDataset
import joblib

import rasterio
import fiona
import shapely.geometry
import cv2
import rasterio.features

import segmentation_models_pytorch as smp


def main():
    ENCODER = 'resnet34'
    ENCODER_WEIGHTS = 'imagenet'
    ACTIVATION = 'sigmoid'
    CLASSES=1
    BATCH_SIZE=1

    device = torch.device("cuda:%d" % 0)

    model = smp.Unet(
        encoder_name=ENCODER,
        encoder_weights=ENCODER_WEIGHTS,
        activation=ACTIVATION,
        classes=CLASSES
    )

    preprocessing_fn = smp.encoders.get_preprocessing_fn(ENCODER, ENCODER_WEIGHTS)

    loss = MixedLoss(10.0, 2.0)
    loss.__name__ = "MixedLoss"

    metrics = [
        smp.utils.metrics.IoU(threshold=0.5),
    ]

    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, amsgrad=True)
    
    # streaming_train_dataset = StreamingShipDataset("./data/train_df.csv", "./data", 
    #     large_chip_size=LARGE_CHIP_SIZE, chip_size=CHIP_SIZE, transform=joint_transform, preprocessing_fn=preprocessing_fn,
    #     rotation_augmentation=True, give_mask_id=False, only_ships=True)
    
    # train_loader = DataLoader(dataset=streaming_train_dataset, batch_size = 8, num_workers=4)
    streaming_test_dataset = StreamingShipValTestDataset("./data/test_df.csv", "./data/train_v2/", 
        large_chip_size=LARGE_CHIP_SIZE, chip_size=CHIP_SIZE, transform=joint_transform, preprocessing_fn=preprocessing_fn,
        rotation_augmentation=False, only_ships=True)

    streaming_test_aug_dataset = StreamingShipValTestDataset("./data/test_df.csv", "./data/train_v2/", 
        large_chip_size=LARGE_CHIP_SIZE, chip_size=CHIP_SIZE, transform=joint_transform, preprocessing_fn=preprocessing_fn,
        rotation_augmentation=True, only_ships=True)

    test_loader = DataLoader(dataset=streaming_test_dataset, batch_size = 8, num_workers=4)

    test_aug_loader = DataLoader(dataset=streaming_test_aug_dataset, batch_size = 8, num_workers=4)

    # Num img, mask
    for i, (img, mask) in enumerate(test_aug_loader):
        if i == 15: break
        # print(img.min(), img.max())

    pass


main()