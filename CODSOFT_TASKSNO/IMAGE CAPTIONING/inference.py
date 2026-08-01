import sys
import torch
import torchvision.transforms as transforms
from PIL import Image

from model import ImageCaptioner

CHECKPOINT = "checkpoint.pth"
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def load_model(checkpoint_path):
    ckpt = torch.load(checkpoint_path, map_location=DEVICE)
    vocab = ckpt["vocab"]
    vocab_size = len(vocab)
    model = ImageCaptioner(embed_size=256, hidden_size=512,
                           vocab_size=vocab_size, num_layers=2).to(DEVICE)
    model.load_state_dict(ckpt["model"])
    return model, vocab


def caption_image(image_path, checkpoint_path=CHECKPOINT):
    model, vocab = load_model(checkpoint_path)
    img = Image.open(image_path).convert("RGB")
    img_tensor = transform(img).unsqueeze(0)
    caption = model.caption_image(img_tensor, vocab, device=DEVICE)
    return caption


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inference.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]
    print("Caption:", caption_image(image_path))
