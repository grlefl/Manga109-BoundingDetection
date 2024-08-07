import cv2
import numpy as np
import torch
from torch.utils.data import Dataset


# custom dataset to augment images, bounding boxes, and labels from dataframe
class CustomDataset(Dataset):
    def __init__(self, img_df, transform=None):
        self.img_df = img_df
        self.transform = transform

    def __len__(self):
        return len(self.img_df)

    def __getitem__(self, idx):
        img_path = self.img_df.iloc[idx]['img_path']
        bboxes = self.img_df.iloc[idx]['bboxes']  # [[box#1], [box#2], [box#3]]
        labels = self.img_df.iloc[idx]['labels']  # [label#1, label#2, label#3]

        image = cv2.imread(img_path)                            # load the image as numpy array (BGR format)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)          # convert BGR image to RGB format
        image = image.astype(np.float32) / 255.                 # normalize image for pixel range [0, 1]

        target = {'boxes': None, 'labels': None}  # prepare target tensor dictionary

        # apply the image transforms
        if self.transform:
            transformed = self.transform(image=image, bboxes=bboxes, labels=labels)

            image = transformed['image']
            target['labels'] = torch.tensor(transformed['labels'], dtype=torch.int64)

            if len(transformed['bboxes']) == 0:
                target['boxes'] = torch.zeros((0, 4), dtype=torch.float32)
            else:
                target['boxes'] = torch.tensor(transformed['bboxes'], dtype=torch.float32)

        return image, target


def collate_fn(batch):
    """
    To handle the data loading as different images may have different number
    of objects and to handle varying size tensors as well.
    """
    return tuple(zip(*batch))
