"""
Pipeline Steps Based on Scikit-Learn
=====================================
Those steps works with scikit-learn (sklearn) transformers and estimators.

..
    Copyright 2019, Neuraxio Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

..
    Thanks to Umaneo Technologies Inc. for their contributions to this Machine Learning
    project, visit https://www.umaneo.com/ for more information on Umaneo Technologies Inc.

"""
import inspect
from typing import Any

from sklearn.base import BaseEstimator
from sklearn.linear_model import Ridge

from neuraxle.base import BaseStep
from neuraxle.hyperparams.distributions import LogUniform, Boolean
from neuraxle.hyperparams.space import HyperparameterSpace, HyperparameterSamples, RecursiveDict
from neuraxle.steps.numpy import NumpyTranspose
from neuraxle.union import ModelStacking


class SKLearnWrapper(BaseStep):
    def __init__(
        self,
        wrapped_sklearn_predictor,
        hyperparams_space: HyperparameterSpace = None,
        return_all_sklearn_default_params_on_get: bool = False,
        use_partial_fit: bool = False,
        use_predict_proba: bool = False
    ):
        if not isinstance(wrapped_sklearn_predictor, BaseEstimator):
            raise ValueError("The wrapped_sklearn_predictor must be an instance of scikit-learn's BaseEstimator.")
        self.wrapped_sklearn_predictor = wrapped_sklearn_predictor
        params: HyperparameterSamples = HyperparameterSamples(wrapped_sklearn_predictor.get_params())
        BaseStep.__init__(self, hyperparams=params, hyperparams_space=hyperparams_space)
        self.return_all_sklearn_default_params_on_get = return_all_sklearn_default_params_on_get
        self.name += "_" + wrapped_sklearn_predictor.__class__.__name__
        self.partial_fit: bool = use_partial_fit
        self.use_predict_proba: bool = use_predict_proba

    def fit_transform(self, data_inputs, expected_outputs=None) -> ('BaseStep', Any):
        if hasattr(self.wrapped_sklearn_predictor, 'fit_transform'):
            if expected_outputs is None or len(inspect.getfullargspec(self.wrapped_sklearn_predictor.fit).args) < 3:
                out = self._sklearn_fit_transform_without_expected_outputs(data_inputs)
            else:
                out = self._sklearn_fit_transform_with_expected_outputs(data_inputs, expected_outputs)
            return self, out

        self.fit(data_inputs, expected_outputs)

        return self, self.transform(data_inputs)

    def _sklearn_fit_transform_with_expected_outputs(self, data_inputs, expected_outputs):
        if self.partial_fit:
            self.wrapped_sklearn_predictor = self.wrapped_sklearn_predictor.partial_fit(data_inputs, expected_outputs)
        else:
            self.wrapped_sklearn_predictor = self.wrapped_sklearn_predictor.fit(data_inputs, expected_outputs)
        return self.transform(data_inputs)

    def _sklearn_fit_transform_without_expected_outputs(self, data_inputs):
        if self.partial_fit:
            self.wrapped_sklearn_predictor = self.wrapped_sklearn_predictor.partial_fit(data_inputs)
            out = self.transform(data_inputs)
        else:
            out = self.wrapped_sklearn_predictor.fit_transform(data_inputs)
        return out

    def fit(self, data_inputs, expected_outputs=None) -> 'SKLearnWrapper':
        if expected_outputs is None or len(inspect.getfullargspec(self.wrapped_sklearn_predictor.fit).args) < 3:
            self._sklearn_fit_without_expected_outputs(data_inputs)
        else:
            self._sklearn_fit_with_expected_outputs(data_inputs, expected_outputs)
        return self

    def _sklearn_fit_with_expected_outputs(self, data_inputs, expected_outputs):
        if self.partial_fit:
            self.wrapped_sklearn_predictor = self.wrapped_sklearn_predictor.partial_fit(data_inputs, expected_outputs)
        else:
            self.wrapped_sklearn_predictor = self.wrapped_sklearn_predictor.fit(data_inputs, expected_outputs)

    def _sklearn_fit_without_expected_outputs(self, data_inputs):
        if self.partial_fit:
            self.wrapped_sklearn_predictor = self.wrapped_sklearn_predictor.partial_fit(data_inputs)
        else:
            self.wrapped_sklearn_predictor = self.wrapped_sklearn_predictor.fit(data_inputs)

    def transform(self, data_inputs):
        if self.use_predict_proba and hasattr(self.wrapped_sklearn_predictor, 'predict_proba'):
            return self.wrapped_sklearn_predictor.predict_proba(data_inputs)
        elif hasattr(self.wrapped_sklearn_predictor, 'predict'):
            return self.wrapped_sklearn_predictor.predict(data_inputs)
        return self.wrapped_sklearn_predictor.transform(data_inputs)

    def _set_hyperparams(self, hyperparams: HyperparameterSamples) -> BaseStep:
        """
        Set hyperparams for base step, and the wrapped sklearn_predictor.

        :param hyperparams:
        :return: self
        """
        # flatten the step hyperparams, and set the wrapped sklearn predictor params
        hyperparams = HyperparameterSamples(hyperparams)
        BaseStep._set_hyperparams(self, hyperparams.to_flat())
        self.wrapped_sklearn_predictor.set_params(
            **hyperparams.with_separator(RecursiveDict.DEFAULT_SEPARATOR).to_flat_as_dict_primitive()
        )

        return self.hyperparams.to_flat()

    def _update_hyperparams(self, hyperparams: HyperparameterSamples) -> BaseStep:
        """
        Update hyperparams for base step, and the wrapped sklearn_predictor.

        :param hyperparams:
        :return: self
        """
        # flatten the step hyperparams, and update the wrapped sklearn predictor params
        hyperparams = HyperparameterSamples(hyperparams)
        BaseStep._update_hyperparams(self, hyperparams.to_flat())
        self.wrapped_sklearn_predictor.set_params(
            **self.hyperparams.with_separator(RecursiveDict.DEFAULT_SEPARATOR).to_flat_as_dict_primitive()
        )

        return self.hyperparams.to_flat()

    def _get_hyperparams(self):
        if self.return_all_sklearn_default_params_on_get:
            return HyperparameterSamples(self.wrapped_sklearn_predictor.get_params()).to_flat()
        else:
            return BaseStep._get_hyperparams(self)

    def get_wrapped_sklearn_predictor(self):
        return self.wrapped_sklearn_predictor

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        type_ = self.__class__
        module = type_.__module__
        qualname = type_.__qualname__
        wrappedname = str(self.wrapped_sklearn_predictor.__class__.__name__)
        return "<{}.{}({}(...)) object {}>".format(module, qualname, wrappedname, hex(id(self)))


class RidgeModelStacking(ModelStacking):
    def __init__(self, brothers):
        ModelStacking.__init__(
            self,
            brothers,
            SKLearnWrapper(
                Ridge(),
                HyperparameterSpace({"alpha": LogUniform(0.1, 10.0), "fit_intercept": Boolean()})
            ),
            joiner=NumpyTranspose()
        )
