from typing import Callable, Sequence, List, Tuple

import numpy as np
from torch import Tensor

from treeboost_autograd.pytorch_objective import PytorchObjective


class SklearnStyleObjective(PytorchObjective):
    def __init__(self, loss_function: Callable[[Tensor, Tensor], Tensor]):
        super().__init__(loss_function, use_minus_loss_as_objective=False)

    def __call__(self, targets: np.ndarray, preds: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return self.calculate_derivatives(preds, targets)


class LightGbmObjective(SklearnStyleObjective):
    pass


class XgboostObjective(SklearnStyleObjective):
    pass


class CatboostObjective(PytorchObjective):
    def __init__(self, loss_function: Callable[[Tensor, Tensor], Tensor]):
        super().__init__(loss_function, use_minus_loss_as_objective=True)

    def calc_ders_range(self,
                        preds: Sequence[float],
                        targets: Sequence[float],
                        weights: Sequence[float] = None
                        ) -> List[Tuple[float, float]]:
        deriv1, deriv2 = self.calculate_derivatives(preds, targets, weights)
        result = list(zip(deriv1, deriv2))
        return result
