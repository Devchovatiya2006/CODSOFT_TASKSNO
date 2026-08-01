import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset import Flickr8kDataset, collate_fn
from model import ImageCaptioner

# ── Config ──────────────────────────────────────────────────────────────────
IMAGES_DIR   = "data/Images"
CAPTIONS_FILE = "data/captions.txt"
EMBED_SIZE   = 256
HIDDEN_SIZE  = 512
NUM_LAYERS   = 1
BATCH_SIZE   = 16
EPOCHS       = 5
LR           = 3e-4
CHECKPOINT   = "checkpoint.pth"
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"
# ────────────────────────────────────────────────────────────────────────────


def train():
    dataset = Flickr8kDataset(IMAGES_DIR, CAPTIONS_FILE)
    loader  = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True,
                         collate_fn=collate_fn, num_workers=2, pin_memory=False)

    vocab_size = len(dataset.vocab)
    model = ImageCaptioner(EMBED_SIZE, HIDDEN_SIZE, vocab_size, NUM_LAYERS).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss(ignore_index=dataset.vocab.stoi["<PAD>"])

    model.train()
    for epoch in range(1, EPOCHS + 1):
        total_loss = 0
        for imgs, captions in tqdm(loader, desc=f"Epoch {epoch}/{EPOCHS}"):
            imgs, captions = imgs.to(DEVICE), captions.to(DEVICE)
            outputs = model(imgs, captions)          # (B, seq_len, vocab_size)
            loss = criterion(
                outputs.reshape(-1, vocab_size),
                captions.reshape(-1)
            )
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item()

        avg = total_loss / len(loader)
        print(f"Epoch {epoch} | Loss: {avg:.4f}")

    torch.save({"model": model.state_dict(),
                "vocab": dataset.vocab}, CHECKPOINT)
    print(f"Saved checkpoint → {CHECKPOINT}")


if __name__ == "__main__":
    train()
