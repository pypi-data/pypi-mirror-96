import logging
import math
import os
from itertools import chain
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Sequence, Union

import torch
from clearml import Task
from fastprogress import master_bar, progress_bar
from torch.optim.lr_scheduler import _LRScheduler

from ..common.checks import ConfigurationError
from ..common.utils import lazy_groups_of, set_seed
from ..nn import utils as nn_util
from ..training import util as training_util
from ..training.callbacks import Callbacks, ClearMLReporter, EarlyStopping
from ..training.trainer_base import TrainerBase

if TYPE_CHECKING:
    from ..data.instance import Instance  # noqa: F401
    from ..data.iterators.data_iterator import DataIterator
    from ..models.model import Model

logger = logging.getLogger(__name__)

try:
    from apex import amp
except ImportError:
    logger.info("Apex is not found. So you can't use fp16 training.")


class Trainer(TrainerBase):
    def __init__(
        self,
        model: "Model",
        optimizer: torch.optim.Optimizer,  # type: ignore
        serialization_dir: str,
        iterator: "DataIterator",
        train_dataset: Iterable["Instance"],
        validation_dataset: Optional[Iterable["Instance"]] = None,
        early_stopping: bool = False,
        patience: Optional[int] = None,
        early_stopping_metric: str = "-loss",
        validation_iterator: Optional["DataIterator"] = None,
        shuffle: bool = True,
        num_epochs: int = 20,
        accumulation_steps: int = 0,
        experiment_name: Optional[str] = None,
        cuda_device: Union[int, List[int]] = -1,
        grad_norm: Optional[float] = 1.0,
        get_lr_scheduler: Optional[Callable[[torch.optim.Optimizer, float, int], _LRScheduler]] = None,  # type: ignore
        scheduler_warm_up: float = 0.1,
        fp16: bool = False,
        fp16_opt_level: str = "O1",
        gradual_unfreezing_steps: Optional[List[List[str]]] = None,
        checkpoint_steps: Optional[int] = None,
        run_validation_each_global_steps: Optional[int] = None,
        clearml_logging: bool = True,
        clearml_task: Optional[Task] = None,
        clearml_additional_params_to_log: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        A trainer for doing supervised learning. It just takes a labeled dataset
        and a ``DataIterator``, and uses the supplied ``Optimizer`` to learn the weights
        for your model over some fixed number of epochs. You can also pass in a validation
        dataset and enable early stopping. There are many other bells and whistles as well.

        Parameters
        ----------
        model : ``Model``, required.
            An Vtorch model to be optimized. Pytorch Modules can also be optimized if
            their ``forward`` method returns a dictionary with a "loss" key, containing a
            scalar tensor representing the loss function to be optimized.
            If you are training your model using GPUs, your model should already be
            on the correct device.
        optimizer : ``torch.nn.Optimizer``, required.
            An instance of a Pytorch Optimizer, instantiated with the parameters of the
            model to be optimized.
        iterator : ``DataIterator``, required.
            A method for iterating over a ``Dataset``, yielding padded indexed batches.
        train_dataset : ``Dataset``, required.
            A ``Dataset`` to train on. The dataset should have already been indexed.
        validation_dataset : ``Dataset``, optional, (default = None).
            A ``Dataset`` to evaluate on. The dataset should have already been indexed.
        patience : Optional[int] > 0, optional (default=None)
            Number of epochs to be patient before early stopping: the training is stopped
            after ``patience`` epochs with no improvement. If given, it must be ``> 0``.
            If None, early stopping is disabled.
        early_stopping_metric : str, optional (default=["-loss"])
            Validation metric for early stopping
        validation_iterator : ``DataIterator``, optional (default=None)
            An iterator to use for the validation set.  If ``None``, then
            use the training `iterator`.
        shuffle : ``bool``, optional (default=True)
            Whether to shuffle the instances in the iterator or not.
        num_epochs : int, optional (default = 20)
            Number of training epochs.
        serialization_dir : str, optional (default=None)
            Path to directory for saving and loading model files. Models will not be saved if
            this parameter is not passed.
        accumulation_steps : int, optional (default = 0)
            Number of training steps to accumulate gradients
        cuda_device : ``Union[int, List[int]]``, optional (default = -1)
            An integer or list of integers specifying the CUDA device(s) to use. If -1, the CPU is used.
        grad_norm : ``float``, optional, (default = None).
            If provided, gradient norms will be rescaled to have a maximum of this value.
        clearml_logging : ``bool``, optional (default = True)
        clearml_task: ``Task``, optional  (default = None). Will be created automatically if clearml_logging is True
        """
        super().__init__(serialization_dir, cuda_device)

        # I am not calling move_to_gpu here, because if the model is
        # not already on the GPU then the optimizer is going to be wrong.
        self._model = model
        if self._model.metrics is None:
            raise ConfigurationError("You train a model without any metrics")
        self._validation_metrics: List[str] = ["loss"] + list(
            chain(*[metric.NAMES for metric in self._model.metrics.values()])
        )

        self._iterator = iterator
        self._validation_iterator = validation_iterator or iterator
        self._shuffle = shuffle
        self._optimizer = optimizer
        self._train_data = train_dataset
        self._validation_data = validation_dataset

        if patience is not None and (not isinstance(patience, int) or patience <= 0):
            raise ConfigurationError(
                f'{patience} is an invalid value for "patience": it must be a positive integer '
                "or None (if you want to disable early stopping)"
            )

        early_stopping_configuration: Optional[EarlyStopping] = None
        if self._validation_data is not None and early_stopping:
            if early_stopping_metric[1:] not in self._validation_metrics:
                raise ConfigurationError("Your validation metric should be in model metrics list.")
            if patience is None:
                raise ConfigurationError("You should set patience if you want to use early_stopping")
            early_stopping_configuration = EarlyStopping(
                patience=patience,
                metric_name=early_stopping_metric[1:],
                should_decrease=early_stopping_metric.startswith("-"),
            )

        self._num_epochs = num_epochs
        self._experiment_name = experiment_name or self._model.MODEL_NAME

        # For tracking is_best_so_far and should_stop_early
        clearml_reporter: Optional[ClearMLReporter] = None
        if clearml_logging:
            if clearml_task is None:
                clearml_reporter = ClearMLReporter.create(
                    self._experiment_name, separate_language=experiment_name is not None
                )
            else:
                clearml_reporter = ClearMLReporter(clearml_task)

        self._callbacks = Callbacks(early_stopping=early_stopping_configuration, clearml_reporter=clearml_reporter)
        self._serialization_dir = serialization_dir
        if not os.path.exists(self._serialization_dir):
            os.makedirs(self._serialization_dir)

        self._accumulation_steps = accumulation_steps
        self._checkpoint_steps = checkpoint_steps
        self._run_validation_each_global_steps = run_validation_each_global_steps

        self._grad_norm = grad_norm
        self._fp16 = fp16
        self._gradual_unfreezing_steps = gradual_unfreezing_steps or ()
        if self._fp16:
            self._model, self._optimizer = amp.initialize(
                self._model, self._optimizer, opt_level=fp16_opt_level, verbosity=0
            )

        self._lr_scheduler = None
        if get_lr_scheduler is not None:
            total_number_of_steps = self._iterator.get_num_batches(self._train_data) * self._num_epochs
            self._lr_scheduler = get_lr_scheduler(
                self._optimizer, int(scheduler_warm_up * total_number_of_steps), total_number_of_steps
            )

        clearml_init_params = {
            "optimizer": optimizer.__class__.__name__,
            "early_stopping": early_stopping,
            "patience": patience,
            "early_stopping_metric": early_stopping_metric,
            "shuffle": shuffle,
            "num_epochs": num_epochs,
            "accumulation_steps": accumulation_steps,
            "grad_norm": grad_norm,
            "scheduler_warm_up": scheduler_warm_up,
            "fp16": fp16,
            "fp16_opt_level": fp16_opt_level,
            "gradual_unfreezing_steps": gradual_unfreezing_steps,
            "checkpoint_steps": checkpoint_steps,
            "run_validation_each_global_steps": run_validation_each_global_steps,
        }
        clearml_init_params.update(self._model.get_serializable_params())
        if clearml_additional_params_to_log is not None:
            clearml_init_params.update(clearml_additional_params_to_log)
        self._callbacks.clearml_update_parameters(clearml_init_params)

    def _batch_outputs_and_loss(
        self, model: "Model", batch_group: List[Dict[str, torch.Tensor]]
    ) -> Sequence[torch.Tensor]:
        """
        Does a forward pass on the given batches and returns the ``loss`` value in the result.
        """
        assert len(batch_group) == 1
        batch = batch_group[0]
        batch = nn_util.move_to_device(batch, self._cuda_devices[0])
        output: Sequence[torch.Tensor] = model(**batch)

        return output

    def _train_epoch(self, master_bar_logger: master_bar, epoch: int, global_steps: int = 0) -> Dict[str, float]:
        """
        Trains one epoch and returns metrics.
        """

        train_loss = 0.0
        # Set the model to "train" mode.
        self._train_mode()
        num_gpus = len(self._cuda_devices)

        raw_train_generator = self._iterator(self._train_data, num_epochs=1, shuffle=self._shuffle)
        train_generator = lazy_groups_of(raw_train_generator, num_gpus)
        num_training_batches = math.ceil(self._iterator.get_num_batches(self._train_data) / num_gpus)

        batches_this_epoch = 0
        for batch_group in progress_bar(
            train_generator, total=num_training_batches, parent=master_bar_logger, leave=False
        ):
            batches_this_epoch += 1

            _, loss = self._batch_outputs_and_loss(self._model, batch_group)
            if self._accumulation_steps > 1:
                loss = loss / self._accumulation_steps

            if torch.isnan(loss):
                raise ValueError("nan loss encountered")

            if self._fp16:
                with amp.scale_loss(loss, self._optimizer) as scaled_loss:
                    scaled_loss.backward()
                torch.nn.utils.clip_grad_norm_(amp.master_params(self._optimizer), self._grad_norm)  # type: ignore
            else:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self._model.parameters(), self._grad_norm)  # type: ignore

            train_loss += loss.item()
            if batches_this_epoch % self._accumulation_steps == 0:
                self._optimizer.step()
                if self._lr_scheduler is not None:
                    self._lr_scheduler.step()  # type: ignore
                self._model.zero_grad()

                self._callbacks.clearml_report_scalar(
                    title="Training", series="loss", value=loss.item(), iteration=global_steps
                )

                global_steps += 1

                master_bar_logger.child.comment = f"loss: {round(train_loss / batches_this_epoch, 4)}"

            if self._checkpoint_steps is not None and batches_this_epoch % self._checkpoint_steps == 0:
                checkpoint_folder = os.path.join(
                    self._serialization_dir, f"epoch_{epoch}_checkpoint_{batches_this_epoch}"
                )
                if not os.path.exists(checkpoint_folder):
                    os.makedirs(checkpoint_folder)

                self._model.save(checkpoint_folder)
                with open(os.path.join(checkpoint_folder, "model.th"), "wb") as f:
                    torch.save(self._model.state_dict(), f)  # type: ignore

            if (
                self._run_validation_each_global_steps is not None
                and (global_steps + 1) % self._run_validation_each_global_steps == 0
            ):
                self._validation_run(master_bar_logger=master_bar_logger, global_steps=global_steps)
                self._train_mode()

        metrics = training_util.get_metrics(self._model, train_loss, batches_this_epoch, reset=True)
        return metrics

    def _train_mode(self) -> None:
        self._model.train()
        self._model.zero_grad()

    def _eval_mode(self) -> None:
        self._model.eval()

    def _validation_run(self, master_bar_logger: master_bar, global_steps: int = 0) -> Optional[Dict[str, float]]:
        """
        Computes the validation metrics. Returns it and the number of batches.
        """
        if self._validation_data is None:
            return None

        logger.info("Validating")

        with torch.no_grad():
            self._eval_mode()
            num_gpus = len(self._cuda_devices)

            raw_val_generator = self._validation_iterator(self._validation_data, num_epochs=1, shuffle=False)
            val_generator = lazy_groups_of(raw_val_generator, num_gpus)
            num_training_batches = math.ceil(self._iterator.get_num_batches(self._validation_data) / num_gpus)

            batches_this_epoch = 0
            val_loss = 0
            for batch_group in progress_bar(
                val_generator, total=num_training_batches, parent=master_bar_logger, leave=False
            ):
                _, loss = self._batch_outputs_and_loss(self._model, batch_group)
                batches_this_epoch += 1
                val_loss += loss.detach().cpu().numpy()
            val_metrics = training_util.get_metrics(self._model, val_loss, batches_this_epoch, reset=True)

        for metric_name, metric_value in val_metrics.items():
            self._callbacks.clearml_report_scalar(
                title="Validation", series=metric_name, value=metric_value, iteration=global_steps
            )
        return val_metrics

    def _gradual_unfreezing(self, step: int) -> None:
        if self._gradual_unfreezing_steps:
            for name, param in self._model.named_parameters():
                if any(
                    list(chain(*[[i in name for i in group] for group in self._gradual_unfreezing_steps[: step + 1]]))
                ):
                    param.requires_grad = True
                else:
                    param.detach_()
                    param.requires_grad = False

    def train(self) -> None:
        """
        Trains the supplied model with the supplied parameters.
        """
        global_steps = 0
        logger.info("Beginning training.")
        mb = master_bar(range(self._num_epochs))
        mb.first_bar.comment = f"{self._model.MODEL_NAME} training"
        mb_elements = ["epoch"] + [f"train_{metrics_name}" for metrics_name in self._validation_metrics]
        if self._validation_data is not None:
            mb_elements.extend([f"val_{metrics_name}" for metrics_name in self._validation_metrics])

        mb.write(mb_elements, table=True)
        set_seed(12, len(self._cuda_devices))
        for epoch in mb:
            mb_results = [str(epoch)]
            self._gradual_unfreezing(epoch)

            train_metrics = self._train_epoch(mb, epoch, global_steps=global_steps)
            mb_results.extend([str(round(train_metrics[metric], 4)) for metric in self._validation_metrics])
            for metric_name, metric_value in train_metrics.items():
                self._callbacks.clearml_report_scalar(
                    title="Training", series=metric_name, value=metric_value, iteration=global_steps
                )

                val_metrics = self._validation_run(mb, global_steps=global_steps)
                if val_metrics is not None:
                    self._callbacks.add_metric(val_metrics)
                    mb_results.extend([str(round(val_metrics[metric], 4)) for metric in self._validation_metrics])

            mb.write(mb_results, table=True)

            if self._callbacks.should_stop_early():
                return None
            elif self._callbacks.is_best_so_far():
                self._model.save(self._serialization_dir)

        return None
