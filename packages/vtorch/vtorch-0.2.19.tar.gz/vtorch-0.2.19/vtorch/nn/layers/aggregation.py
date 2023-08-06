from typing import Sequence

import torch
from torch import nn

from vtorch.nn.packed_sequence import get_last_rnn_state

from .attention import SelfAttention
from .pooling import MaxPool, MeanPool


class Aggregation(nn.Module):  # type: ignore
    def __init__(self, layers: Sequence[str], input_dim: int) -> None:
        super().__init__()
        self.has_max_pool = "max_pool" in layers
        self.has_mean_pool = "mean_pool" in layers
        self.has_attention = "attention" in layers
        if self.has_max_pool:
            self.max_pool = MaxPool()
        if self.has_mean_pool:
            self.mean_pool = MeanPool()
        if self.has_attention:
            self.attention = SelfAttention(input_dim)

        self._n_layers = len(layers)
        self._input_dim = input_dim

    def forward(  # type: ignore
        self, x: torch.Tensor, lengths: torch.Tensor, batch_first: bool = False
    ) -> torch.Tensor:
        if self._n_layers == 0:
            if lengths is not None:
                return get_last_rnn_state(x, lengths)
            else:
                return x[-1]

        aggregations = []
        if self.has_max_pool:
            aggregations.append(self.max_pool(x))
        if self.has_mean_pool:
            aggregations.append(self.mean_pool(x))
        if self.has_attention:
            attention_output, _ = self.attention(x, lengths)
            aggregations.append(attention_output)
        return torch.cat(aggregations, dim=1)

    def get_output_dim(self) -> int:
        if self._n_layers != 0:
            return self._n_layers * self._input_dim
        return self._input_dim
