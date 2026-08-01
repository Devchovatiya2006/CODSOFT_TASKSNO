import os
import pandas as pd
from PIL import Image
from collections import Counter

import torch
from torch.utils.data import Dataset
from torch.nn.utils.rnn import pad_sequence
import torchvision.transforms as transforms
import nltk

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


class Vocabulary:
    def __init__(self, freq_threshold=5):
        self.freq_threshold = freq_threshold
        self.itos = {0: "<PAD>", 1: "<SOS>", 2: "<EOS>", 3: "<UNK>"}
        self.stoi = {v: k for k, v in self.itos.items()}

    def __len__(self):
        return len(self.itos)

    def build(self, captions):
        counter = Counter()
        for caption in captions:
            counter.update(nltk.tokenize.word_tokenize(caption.lower()))
        idx = 4
        for word, freq in counter.items():
            if freq >= self.freq_threshold:
                self.stoi[word] = idx
                self.itos[idx] = word
                idx += 1

    def numericalize(self, text):
        tokens = nltk.tokenize.word_tokenize(text.lower())
        return [self.stoi.get(t, self.stoi["<UNK>"]) for t in tokens]


class Flickr8kDataset(Dataset):
    """
    Expects:
      images_dir/  — folder with all .jpg images
      captions.txt — format: image_name|caption  (Flickr8k style)
    """
    def __init__(self, images_dir, captions_file, vocab=None, freq_threshold=5, transform=None):
        self.images_dir = images_dir
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

        df = pd.read_csv(captions_file, sep=",", header=0,
                         names=["image", "caption"], skiprows=1)
        df["caption"] = df["caption"].astype(str).str.strip()
        df["image"] = df["image"].str.strip()
        self.df = df.dropna(subset=["caption"]).reset_index(drop=True)

        if vocab is None:
            self.vocab = Vocabulary(freq_threshold)
            self.vocab.build(self.df["caption"].tolist())
        else:
            self.vocab = vocab

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img = Image.open(os.path.join(self.images_dir, row["image"])).convert("RGB")
        img = self.transform(img)
        caption = (
            [self.vocab.stoi["<SOS>"]]
            + self.vocab.numericalize(row["caption"])
            + [self.vocab.stoi["<EOS>"]]
        )
        return img, torch.tensor(caption)


def collate_fn(batch):
    imgs, captions = zip(*batch)
    imgs = torch.stack(imgs)
    captions = pad_sequence(captions, batch_first=True, padding_value=0)
    return imgs, captions
