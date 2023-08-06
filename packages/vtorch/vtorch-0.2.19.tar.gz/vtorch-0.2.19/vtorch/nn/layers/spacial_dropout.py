import torch
import torch.nn as nn


class SpacialDropout1d(nn.Module):  # type: ignore
    def __init__(self, dropout: float = 0.0, batch_first: bool = False) -> None:
        super().__init__()
        self.batch_first = int(batch_first)
        self.dropout2d = nn.Dropout2d(dropout)

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:  # type: ignore
        right_shape_embeddings = embeddings.unsqueeze(2).permute(1 - self.batch_first, 3, 2, self.batch_first)
        dropout_embeddings = self.dropout2d(right_shape_embeddings)
        return dropout_embeddings.permute((1 - self.batch_first) * 3, self.batch_first * 3, 2, 1).squeeze(2)
