from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class EarlyStoppingI(ABC):
    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def state_dict(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def add_metric(self, metrics: Dict[str, float]) -> None:
        pass

    @abstractmethod
    def is_best_so_far(self) -> bool:
        pass

    @abstractmethod
    def should_stop_early(self) -> bool:
        pass


class EarlyStoppingNull(EarlyStoppingI):
    def clear(self) -> None:
        return None

    def state_dict(self) -> Dict[str, Any]:
        return {}

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        return None

    def add_metric(self, metrics: Dict[str, float]) -> None:
        return None

    def is_best_so_far(self) -> bool:
        return True

    def should_stop_early(self) -> bool:
        return False


class EarlyStopping(EarlyStoppingI):
    """
    This class tracks a metric during training for the dual purposes of early stopping
    and for knowing whether the current value is the best so far. It mimics the PyTorch
    `state_dict` / `load_state_dict` interface, so that it can be checkpointed along with
    your model and optimizer.

    Some metrics improve by increasing; others by decreasing. Here you can either explicitly
    supply `should_decrease`, or you can provide a `metric_name` in which case "should decrease"
    is inferred from the first character, which must be "+" or "-".

    Parameters
    ----------
    patience : int, optional (default = None)
        If provided, then `should_stop_early()` returns True if we go this
        many epochs without seeing a new best value.
    metric_name : str, optional (default = None)
        If provided, it's used to infer whether we expect the metric values to
        increase (if it starts with "+") or decrease (if it starts with "-").
        It's an error if it doesn't start with one of those. If it's not provided,
        you should specify ``should_decrease`` instead.
    should_decrease : str, optional (default = None)
        If ``metric_name`` isn't provided (in which case we can't infer ``should_decrease``),
        then you have to specify it here.
    """

    def __init__(self, patience: int, metric_name: str, should_decrease: bool = True) -> None:
        self._patience: int = patience
        self.metric_name = metric_name
        self._should_decrease = should_decrease

        self._epochs_with_no_improvement: int = 0
        self._is_best_so_far = True
        self._epoch_number: int = 0
        self.best_epoch: Optional[int] = None
        self._best_so_far: Optional[float] = None

    def clear(self) -> None:
        """
        Clears out the tracked metrics, but keeps the patience and should_decrease settings.
        """
        self._best_so_far = None
        self._epochs_with_no_improvement = 0
        self._is_best_so_far = True
        self._epoch_number = 0
        self.best_epoch = None

    def state_dict(self) -> Dict[str, Any]:
        """
        A ``Trainer`` can use this to serialize the state of the metric tracker.
        """
        return {
            "best_so_far": self._best_so_far,
            "patience": self._patience,
            "epochs_with_no_improvement": self._epochs_with_no_improvement,
            "is_best_so_far": self._is_best_so_far,
            "should_decrease": self._should_decrease,
            "epoch_number": self._epoch_number,
            "best_epoch": self.best_epoch,
        }

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        """
        A ``Trainer`` can use this to hydrate a metric tracker from a serialized state.
        """
        self._best_so_far = state_dict["best_so_far"]
        self._patience = state_dict["patience"]
        self._epochs_with_no_improvement = state_dict["epochs_with_no_improvement"]
        self._is_best_so_far = state_dict["is_best_so_far"]
        self._should_decrease = state_dict["should_decrease"]
        self._epoch_number = state_dict["epoch_number"]
        self.best_epoch = state_dict["best_epoch"]

    def add_metric(self, metrics: Dict[str, float]) -> None:
        """
        Record a new value of the metric and update the various things that depend on it.
        """
        target_metric = metrics.get(self.metric_name)
        if target_metric is None:
            raise KeyError(
                f"The metrics passed to the {self.__class__.__name__} do not contain target metric "
                f"{self.metric_name}"
            )
        new_best = (
            (self._best_so_far is None)
            or (self._should_decrease and target_metric < self._best_so_far)
            or (not self._should_decrease and target_metric > self._best_so_far)
        )

        if new_best:
            self.best_epoch = self._epoch_number
            self._is_best_so_far = True
            self._best_so_far = target_metric
            self._epochs_with_no_improvement = 0
        else:
            self._is_best_so_far = False
            self._epochs_with_no_improvement += 1
        self._epoch_number += 1

    def is_best_so_far(self) -> bool:
        """
        Returns true if the most recent value of the metric is the best so far.
        """
        return self._is_best_so_far

    def should_stop_early(self) -> bool:
        """
        Returns true if improvement has stopped for long enough.
        """
        return self._epochs_with_no_improvement >= self._patience
