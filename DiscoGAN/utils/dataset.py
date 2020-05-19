import torch
import numpy as np
import torch.utils.data as data
from os import listdir
from os.path import join
from utils import is_image_file
import os
from PIL import Image
import random
def default_loader(path):
	return Image.open(path).convert("RGB")
def ToTensor(pic):
	"""Converts a PIL.Image or numpy.ndarray (H x W x C) in the range
    [0, 255] to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0].
    """
	if isinstance(pic, np.ndarray):
		img = torch.from_numpy(pic.transpose((2, 0, 1)))
		return img.float().div(255)
	if pic.mode == "I":
		img = torch.from_numpy(np.array(pic, np.int32, copy=False))
	elif pic.mode == "I;16":
		img = torch.from_numpy(np.array(pic, np.int16, copy=False))
	else:
		img = torch.ByteTensor(torch.ByteStorage.from_buffer(pic.tobytes()))
	if pic.mode == "YCbCr":
		nchannel = 3
	elif pic.mode == "I;16":
		nchannel = 1
	else:
		nchannel = len(pic.mode)
	img = img.view(pic.size[1], pic.size[0], nchannel)
	img = img.transpose(0, 1).transpose(0, 2).contiguous()
	if isinstance(img, torch.ByteTensor):
		return img.float().div(255)
	else:
		return img
class DATASET(data.Dataset):
	def __init__(self, dataPath="", loadSize=72, fineSize=64, flip=1):
		super(DATASET, self).__init__()
		self.list = [x for x in listdir(dataPath) if is_image_file(x)]
		self.dataPath = dataPath
		self.loadSize = loadSize
		self.fineSize = fineSize
		self.flip = flip
	def __getitem__(self, index):
		path = os.path.join(self.dataPath, self.list[index])
		img = default_loader(path)
		w, h = img.size
		if h != self.loadSize:
			img = img.resize((self.loadSize, self.loadSize), Image.BILINEAR)
		if self.loadSize != self.fineSize:
			x1 = random.randint(0, self.loadSize - self.fineSize)
			y1 = random.randint(0, self.loadSize - self.fineSize)
			img = img.crop((x1, y1, x1 + self.fineSize, y1 + self.fineSize))
		if self.flip == 1:
			if random.random() < 0.5:
				img = img.transpose(Image.FLIP_LEFT_RIGHT)
		img = ToTensor(img)
		img = img.mul_(2).add_(-1)
		return img
	def __len__(self):
		return len(self.list)