from typing import TYPE_CHECKING, Dict, Iterator, List, Mapping, Optional

import torch

from ..common.checks import ConfigurationError
from .fields import Field, MetadataField

if TYPE_CHECKING:
    from .vocabulary import Vocabulary


class Instance(Mapping[str, Field]):
    """
    An ``Instance`` is a collection of :class:`~vtorch.data.fields.field.Field` objects,
    specifying the inputs and outputs to
    some model.  We don't make a distinction between inputs and outputs here, though - all
    operations are done on all fields, and when we return arrays, we return them as dictionaries
    keyed by field name.  A model can then decide which fields it wants to use as inputs as which
    as outputs.
    The ``Fields`` in an ``Instance`` can start out either indexed or un-indexed.  During the data
    processing pipeline, all fields will be indexed, after which multiple instances can be combined
    into a ``Batch`` and then converted into padded arrays.
    Parameters
    ----------
    fields : ``Dict[str, Field]``
        The ``Field`` objects that will be used to produce data arrays for this instance.
    """

    def __init__(self, fields: Dict[str, Field]) -> None:
        self.fields = fields
        self.indexed = False

    def __getitem__(self, key: str) -> Field:
        return self.fields[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.fields)

    def __len__(self) -> int:
        return len(self.fields)

    def add_field(
        self,
        field_name: str,
        field: Field,
        use_pretrained_tokenizer: bool = False,
        vocab: Optional["Vocabulary"] = None,
    ) -> None:
        """
        Add the field to the existing fields mapping.
        If we have already indexed the Instance, then we also index `field`, so
        it is necessary to supply the vocab.
        """
        self.fields[field_name] = field
        if self.indexed:
            if vocab is None:
                raise ConfigurationError("You should pass Vocabulary for already indexed fields.")
            field.index(vocab, use_pretrained_tokenizer)

    def count_vocab_items(self, counter: Dict[str, Dict[str, int]], exclude_fields: List[str]) -> None:
        """
        Increments counts in the given ``counter`` for all of the vocabulary items in all of the
        ``Fields`` in this ``Instance``.
        """
        for field_name, field in self.fields.items():
            if field_name not in exclude_fields:
                field.count_vocab_items(counter)

    def index_fields(
        self, vocab: "Vocabulary", fields_with_pretrained_tokenizer: List[str], serial_index: Optional[int] = None
    ) -> None:
        """
        Indexes all fields in this ``Instance`` using the provided ``Vocabulary``.
        This `mutates` the current object, it does not return a new ``Instance``.
        A ``DataIterator`` will call this on each pass through a dataset; we use the ``indexed``
        flag to make sure that indexing only happens once.
        This means that if for some reason you modify your vocabulary after you've
        indexed your instances, you might get unexpected behavior.
        """
        if not self.indexed:
            self.indexed = True
            for field_name, field in self.fields.items():
                field.index(vocab, field_name in fields_with_pretrained_tokenizer)
            if "serial_index" not in self.fields and serial_index is not None:
                self.fields["serial_index"] = MetadataField(serial_index)

    def get_padding_lengths(self) -> Dict[str, Dict[str, int]]:
        """
        Returns a dictionary of padding lengths, keyed by field name.  Each ``Field`` returns a
        mapping from padding keys to actual lengths, and we just key that dictionary by field name.
        """
        lengths = {}
        for field_name, field in self.fields.items():
            lengths[field_name] = field.get_padding_lengths()
        return lengths

    def as_tensor_dict(self, padding_lengths: Optional[Dict[str, Dict[str, int]]] = None) -> Dict[str, torch.Tensor]:
        """
        Pads each ``Field`` in this instance to the lengths given in ``padding_lengths`` (which is
        keyed by field name, then by padding key, the same as the return value in
        :func:`get_padding_lengths`), returning a list of torch tensors for each field.
        If ``padding_lengths`` is omitted, we will call ``self.get_padding_lengths()`` to get the
        sizes of the tensors to create.
        """
        padding_lengths = padding_lengths or self.get_padding_lengths()
        tensors = {}
        for field_name, field in self.fields.items():
            tensors[field_name] = field.as_tensor(padding_lengths[field_name])
        return tensors

    def __str__(self) -> str:
        base_string = "Instance with fields:\n"
        return " ".join([base_string] + [f"\t {name}: {field} \n" for name, field in self.fields.items()])
