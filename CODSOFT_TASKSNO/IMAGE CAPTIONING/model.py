import torch
import torch.nn as nn
import torchvision.models as models


class EncoderCNN(nn.Module):
    def __init__(self, embed_size):
        super().__init__()
        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        modules = list(resnet.children())[:-1]  # Remove final FC layer
        self.resnet = nn.Sequential(*modules)
        self.embed = nn.Linear(resnet.fc.in_features, embed_size)
        self.dropout = nn.Dropout(0.5)

        for param in self.resnet.parameters():
            param.requires_grad = False  # Freeze CNN

    def forward(self, images):
        with torch.no_grad():
            features = self.resnet(images)
        features = features.reshape(features.size(0), -1)
        return self.dropout(self.embed(features))


class DecoderRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers=2):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, batch_first=True, dropout=0.5 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, vocab_size)
        self.dropout = nn.Dropout(0.5)

    def forward(self, features, captions):
        embeddings = self.dropout(self.embed(captions[:, :-1]))  # Exclude <EOS>
        inputs = torch.cat((features.unsqueeze(1), embeddings), dim=1)
        hiddens, _ = self.lstm(inputs)
        return self.fc(hiddens)


class ImageCaptioner(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers=2):
        super().__init__()
        self.encoder = EncoderCNN(embed_size)
        self.decoder = DecoderRNN(embed_size, hidden_size, vocab_size, num_layers)

    def forward(self, images, captions):
        features = self.encoder(images)
        return self.decoder(features, captions)

    def caption_image(self, image, vocab, max_len=50, device="cpu"):
        self.eval()
        result = []
        with torch.no_grad():
            x = self.encoder(image.to(device)).unsqueeze(0)
            states = None
            for _ in range(max_len):
                hiddens, states = self.decoder.lstm(x, states)
                output = self.decoder.fc(hiddens.squeeze(1))
                token = output.argmax(1).item()
                if token == vocab.stoi["<EOS>"]:
                    break
                result.append(vocab.itos[token])
                x = self.decoder.embed(output.argmax(1)).unsqueeze(1)
        return " ".join(result)
