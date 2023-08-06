from typing import Any

import torch


def combine_initial_dims(tensor: torch.Tensor) -> torch.Tensor:
    """
    Given a (possibly higher order) tensor of ids with shape
    (d1, ..., dn, sequence_length)
    Return a view that's (d1 * ... * dn, sequence_length).
    If original tensor is 1-d or 2-d, return it as is.
    """
    if tensor.dim() <= 2:
        return tensor
    else:
        return tensor.view(-1, tensor.size(-1))


def uncombine_initial_dims(tensor: torch.Tensor, original_size: torch.Size) -> torch.Tensor:
    """
    Given a tensor of embeddings with shape
    (d1 * ... * dn, sequence_length, embedding_dim)
    and the original shape
    (d1, ..., dn, sequence_length),
    return the reshaped tensor of embeddings with shape
    (d1, ..., dn, sequence_length, embedding_dim).
    If original size is 1-d or 2-d, return it as is.
    """
    if len(original_size) <= 2:
        return tensor
    view_args = list(original_size) + [tensor.size(-1)]
    return tensor.view(*view_args)


def has_tensor(obj: Any) -> bool:
    """
    Given a possibly complex data structure,
    check if it has any torch.Tensors in it.
    """
    if isinstance(obj, torch.Tensor):
        return True
    elif isinstance(obj, dict):
        return any(has_tensor(value) for value in obj.values())
    elif isinstance(obj, (list, tuple)):
        return any(has_tensor(item) for item in obj)
    return False


def move_to_device(obj: Any, cuda_device: int) -> Any:
    """
    Given a structure (possibly) containing Tensors on the CPU,
    move all the Tensors to the specified GPU (or do nothing, if they should be on the CPU).
    """
    # pylint: disable=too-many-return-statements
    if cuda_device < 0 or not has_tensor(obj):
        return obj
    elif isinstance(obj, torch.Tensor):
        return obj.to(device=f"cuda:{cuda_device}")
    elif isinstance(obj, dict):
        return {key: move_to_device(value, cuda_device) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [move_to_device(item, cuda_device) for item in obj]
    elif isinstance(obj, tuple) and hasattr(obj, "_fields"):
        # This is the best way to detect a NamedTuple, it turns out.
        return obj.__class__(*[move_to_device(item, cuda_device) for item in obj])
    elif isinstance(obj, tuple):
        return tuple([move_to_device(item, cuda_device) for item in obj])
    return obj


def get_device_of(tensor: torch.Tensor) -> int:
    """
    Returns the device of the tensor.
    """
    device: int = tensor.get_device() if tensor.is_cuda else -1
    return device


def device_mapping(cuda_device: int) -> str:
    """
    In order to `torch.load()` a GPU-trained model onto a CPU (or specific GPU),
    you have to supply a `map_location` function. Call this with
    the desired `cuda_device` to get the function that `torch.load()` needs.
    """

    if cuda_device < 0:
        return "cpu"
    return f"cuda:{cuda_device}"


def clamp_tensor(tensor: torch.Tensor, minimum: float, maximum: float) -> torch.Tensor:
    """
    Supports dense tensors.
    Returns a tensor with values clamped between the provided minimum and maximum,
    without modifying the original tensor.
    """
    return tensor.clamp(minimum, maximum)
