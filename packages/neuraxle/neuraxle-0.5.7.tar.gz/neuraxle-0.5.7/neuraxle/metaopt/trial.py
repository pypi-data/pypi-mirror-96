"""
Neuraxle's Trial Classes
====================================
Trial objects used by AutoML algorithm classes.

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


"""

import datetime
import hashlib
import traceback
from enum import Enum
from typing import Dict, List, Callable, Iterable

from typing import Dict, List, Tuple
import numpy as np

from neuraxle.base import BaseStep, ExecutionContext
from neuraxle.data_container import DataContainer
from neuraxle.hyperparams.space import HyperparameterSamples

TRIAL_DATETIME_STR_FORMAT = '%m/%d/%Y, %H:%M:%S'


class Trial:
    """
    Trial data container for :class:`AutoML`.
    A Trial contains the results for each validation split.
    Each trial split contains both the training set results, and the validation set results.

    .. seealso::
        :class:`AutoML`,
        :class:`TrialSplit`,
        :class:`HyperparamsRepository`,
        :class:`BaseHyperparameterSelectionStrategy`,
        :class:`RandomSearchHyperparameterSelectionStrategy`,
        :class:`DataContainer`
    """

    def __init__(
            self,
            hyperparams: HyperparameterSamples,
            main_metric_name: str,
            save_trial_function: Callable,
            status: 'TRIAL_STATUS' = None,
            pipeline: BaseStep = None,
            validation_splits: List['TrialSplit'] = None,
            cache_folder: str = None,
            error: str = None,
            error_traceback: str = None,
            start_time: datetime.datetime = None,
            end_time: datetime.datetime = None,
    ):
        self.save_trial_function: Callable = save_trial_function
        if status is None:
            status = TRIAL_STATUS.PLANNED
        if validation_splits is None:
            validation_splits = []

        self.main_metric_name: str = main_metric_name
        self.status: TRIAL_STATUS = status
        self.hyperparams: HyperparameterSamples = hyperparams
        self.pipeline: BaseStep = pipeline
        self.validation_splits: List['TrialSplit'] = validation_splits
        self.cache_folder: str = cache_folder
        self.error_traceback: str = error_traceback
        self.error: str = error
        self.start_time: datetime.datetime = start_time
        self.end_time: datetime.datetime = end_time

    def save_trial(self) -> 'Trial':
        """
        Update trial with the hyperparams repository.

        :return:
        """
        self.save_trial_function(self)
        return self

    def new_validation_split(self, pipeline: BaseStep, delete_pipeline_on_completion: bool = True) -> 'TrialSplit':
        """
        Create a new trial split.
        A trial has one split when the validation splitter function is validation split.
        A trial has one or many split when the validation splitter function is kfold_cross_validation_split.

        :param delete_pipeline_on_completion: bool to delete pipeline on completion or not
        :type pipeline: pipeline to execute
        :return: one trial split
        """
        trial_split: TrialSplit = TrialSplit(
            trial=self,
            split_number=len(self.validation_splits),
            main_metric_name=self.main_metric_name,
            pipeline=pipeline,
            delete_pipeline_on_completion=delete_pipeline_on_completion
        )
        self.validation_splits.append(trial_split)

        self.save_trial()
        return trial_split

    def save_model(self):
        """
        Save fitted model in the trial hash folder.
        """
        hyperparams = self.hyperparams.to_flat_as_dict_primitive()
        trial_hash = self._get_trial_hash(hyperparams)
        self.pipeline.set_name(trial_hash).save(ExecutionContext(self.cache_folder), full_dump=True)

    def set_main_metric_name(self, name: str) -> 'Trial':
        """
        Set trial main metric name.

        :return: self
        """
        self.main_metric_name = name
        return self

    def set_hyperparams(self, hyperparams: HyperparameterSamples) -> 'Trial':
        """
        Set trial hyperparams.

        :param hyperparams: trial hyperparams
        :return:
        """
        self.hyperparams = hyperparams

        return self

    def is_higher_score_better(self) -> bool:
        """
        Return True if higher scores are better for the main metric.

        :return: if higher score is better
        """
        return self.validation_splits[0].is_higher_score_better()

    def get_validation_score(self) -> float:
        """
        Return the latest validation score for the main scoring metric.
        Returns the average score for all validation splits.

        :return: validation score
        """
        scores = [
            validation_split.get_validation_score()
            for validation_split in self.validation_splits if validation_split.is_success()
        ]

        score = sum(scores) / len(scores)

        return score

    def set_success(self) -> 'Trial':
        """
        Set trial status to success.

        :return: self
        """
        self.status = TRIAL_STATUS.SUCCESS
        self.save_trial()

        return self

    def update_final_trial_status(self):
        """
        Set trial status to success.
        """
        success = True
        for validation_split in self.validation_splits:
            if not validation_split.is_success():
                success = False

        if success:
            self.status = TRIAL_STATUS.SUCCESS
        else:
            self.status = TRIAL_STATUS.FAILED

        self.save_trial()

    def set_failed(self, error: Exception) -> 'Trial':
        """
        Set failed trial with exception.

        :param error: catched exception
        :return: self
        """
        self.status = TRIAL_STATUS.FAILED
        self.error = str(error)
        self.error_traceback = traceback.format_exc()

        self.save_trial()

        return self

    def get_trained_pipeline(self, split_number: int = 0):
        """
        Get trained pipeline inside the validation splits.

        :param split_number: split number to get trained pipeline from
        :return:
        """
        return self.validation_splits[split_number].get_pipeline()

    def _get_trial_hash(self, hp_dict: Dict):
        """
        Hash hyperparams with md5 to create a trial hash.

        :param hp_dict: hyperparams dict
        :return:
        """
        current_hyperparameters_hash = hashlib.md5(str.encode(str(hp_dict))).hexdigest()
        return current_hyperparameters_hash

    def to_json(self):
        return {
            'status': self.status.value,
            'hyperparams': self.hyperparams.to_flat_as_dict_primitive(),
            'validation_splits': [v.to_json() for v in self.validation_splits],
            'error': self.error,
            'error_traceback': self.error_traceback,
            'start_time': self.start_time.strftime(TRIAL_DATETIME_STR_FORMAT) if self.start_time is not None else '',
            'end_time': self.end_time.strftime(TRIAL_DATETIME_STR_FORMAT) if self.end_time is not None else '',
            'main_metric_name': self.main_metric_name
        }

    @staticmethod
    def from_json(update_trial_function: Callable, trial_json: Dict) -> 'Trial':
        trial: Trial = Trial(
            main_metric_name=trial_json['main_metric_name'],
            status=TRIAL_STATUS(trial_json['status']),
            hyperparams=HyperparameterSamples(trial_json['hyperparams']),
            save_trial_function=update_trial_function,
            error=trial_json['error'],
            error_traceback=trial_json['error_traceback'],
            start_time=datetime.datetime.strptime(trial_json['start_time'], TRIAL_DATETIME_STR_FORMAT),
            end_time=datetime.datetime.strptime(trial_json['start_time'], TRIAL_DATETIME_STR_FORMAT)
        )

        trial.validation_splits = [
            TrialSplit.from_json(
                trial=trial,
                trial_split_json=validation_split_json
            ) for validation_split_json in trial_json['validation_splits']
        ]

        return trial

    def __getitem__(self, item) -> 'TrialSplit':
        return self.validation_splits[item]

    def __enter__(self):
        """
        Start trial, and set the trial status to PLANNED.
        """
        self.start_time = datetime.datetime.now()
        self.status = TRIAL_STATUS.STARTED
        self.save_trial()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stop trial, and save end time.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.end_time = datetime.datetime.now()
        del self.pipeline
        if exc_type is not None:
            self.set_failed(exc_val)
            self.save_trial()
            raise exc_val

        self.save_trial()
        return self


class TrialSplit:
    """
    One split of a trial.

    .. seealso::
        :class:`AutoML`,
        :class:`HyperparamsRepository`,
        :class:`BaseHyperparameterSelectionStrategy`,
        :class:`RandomSearchHyperparameterSelectionStrategy`,
        :class:`DataContainer`
    """

    def __init__(
            self,
            trial: Trial,
            split_number: int,
            main_metric_name: str,
            status: 'TRIAL_STATUS' = None,
            error: Exception = None,
            error_traceback: str = None,
            metrics_results: Dict = None,
            start_time: datetime.datetime = None,
            end_time: datetime.datetime = None,
            pipeline: BaseStep = None,
            delete_pipeline_on_completion: bool = True
    ):
        if status is None:
            status = TRIAL_STATUS.PLANNED

        self.trial: Trial = trial
        self.split_number: int = split_number
        self.status: TRIAL_STATUS = status
        self.error: Exception = error
        self.error_traceback: str = error_traceback
        if metrics_results is None:
            metrics_results = {}
        self.metrics_results: Dict = metrics_results
        self.end_time: datetime.datetime = end_time
        self.start_time: datetime.datetime = start_time
        self.pipeline: BaseStep = pipeline
        self.main_metric_name: str = main_metric_name
        self.delete_pipeline_on_completion = delete_pipeline_on_completion

    def get_metric_names(self) -> List[str]:
        return list(self.metrics_results.keys())

    def save_parent_trial(self) -> 'TrialSplit':
        """
        Save parent trial.

        :return: self
        """
        self.trial.save_trial()
        return self

    def fit_trial_split(self, train_data_container: DataContainer, context: ExecutionContext) -> 'TrialSplit':
        """
        Fit the trial split pipeline with the training data container.

        :param train_data_container: training data container
        :param context: execution context
        :return: trial split with its fitted pipeline.
        """
        self.pipeline = self.pipeline.handle_fit(train_data_container, context)
        return self

    def predict_with_pipeline(self, data_container: DataContainer, context: ExecutionContext) -> 'DataContainer':
        """
        Predict data with the fitted trial split pipeline.

        :param data_container: data container to predict
        :param context: execution context
        :return: predicted data container
        """
        return self.pipeline.handle_predict(data_container, context)

    def set_main_metric_name(self, name: str) -> 'TrialSplit':
        """
        Set main metric name.

        :param name: main metric name.
        :return: self
        """
        self.main_metric_name = name

        return self

    def add_metric_results_train(self, name: str, score: float, higher_score_is_better: bool):
        """
        Add a train metric result in the metric results dictionary.

        :param name: name of the metric
        :param score: score
        :param higher_score_is_better: if higher score is better or not for this metric
        :return:
        """
        if name not in self.metrics_results:
            self.metrics_results[name] = {
                'train_values': [],
                'validation_values': [],
                'higher_score_is_better': higher_score_is_better
            }

        self.metrics_results[name]['train_values'].append(score)
        self.save_parent_trial()

    def add_metric_results_validation(self, name: str, score: float, higher_score_is_better: bool):
        """
        Add a validation metric result in the metric results dictionary.

        :param name: name of the metric
        :param score: score
        :param higher_score_is_better: if higher score is better or not for this metric
        :return:
        """
        if name not in self.metrics_results:
            self.metrics_results[name] = {
                'train_values': [],
                'validation_values': [],
                'higher_score_is_better': higher_score_is_better
            }

        self.metrics_results[name]['validation_values'].append(score)
        self.save_parent_trial()

    def get_validation_scores(self):
        """
        Return the validation scores for the main scoring metric.

        :return:
        """
        return self.metrics_results[self.main_metric_name]['validation_values']

    def get_validation_score(self):
        """
        Return the latest validation score for the main scoring metric.

        :return:
        """
        return self.metrics_results[self.main_metric_name]['validation_values'][-1]

    def get_pipeline(self):
        """
        Return the trained pipeline

        :return:
        """
        return self.pipeline

    def is_higher_score_better(self) -> bool:
        """
        Return True if higher scores are better for the main metric.

        :return:
        """
        return self.metrics_results[self.main_metric_name]['higher_score_is_better']

    def is_new_best_score(self):
        """
        Return True if the latest validation score is the new best score.

        :return:
        """
        higher_score_is_better = self.metrics_results[self.main_metric_name]['higher_score_is_better']
        validation_values = self.metrics_results[self.main_metric_name]['validation_values']
        best_score = validation_values[0]

        for score in validation_values:
            if score > best_score and higher_score_is_better:
                best_score = score

            if score < best_score and not higher_score_is_better:
                best_score = score

        if best_score == validation_values[-1]:
            return True
        return False

    def get_metric_validation_results(self, metric_name):
        return self.metrics_results[metric_name]['validation_values']

    def get_metric_train_results(self, metric_name):
        return self.metrics_results[metric_name]['train_values']

    def to_json(self) -> dict:
        """
        Return the trial in a json format.

        :return:
        """
        return {
            'status': self.status.value,
            'error': self.error,
            'metric_results': self.metrics_results,
            'error_traceback': self.error_traceback,
            'start_time': self.start_time.strftime(TRIAL_DATETIME_STR_FORMAT) if self.start_time is not None else '',
            'end_time': self.end_time.strftime(TRIAL_DATETIME_STR_FORMAT) if self.end_time is not None else '',
            'split_number': self.split_number,
            'main_metric_name': self.main_metric_name
        }

    @staticmethod
    def from_json(trial: 'Trial', trial_split_json: Dict) -> 'TrialSplit':
        """
        Create a trial split object from json.

        :param trial: parent trial
        :param trial_split_json: trial json
        :return:
        """
        return TrialSplit(
            trial=trial,
            status=TRIAL_STATUS(trial_split_json['status']),
            error=trial_split_json['error'],
            error_traceback=trial_split_json['error_traceback'],
            metrics_results=trial_split_json['metric_results'],
            start_time=datetime.datetime.strptime(trial_split_json['start_time'], TRIAL_DATETIME_STR_FORMAT),
            end_time=datetime.datetime.strptime(trial_split_json['end_time'], TRIAL_DATETIME_STR_FORMAT),
            split_number=trial_split_json['split_number'],
            main_metric_name=trial_split_json['main_metric_name']
        )

    def set_success(self) -> 'TrialSplit':
        """
        Set trial status to success.

        :return: self
        """
        self.status = TRIAL_STATUS.SUCCESS
        self.save_parent_trial()
        return self

    def is_success(self):
        """
        Set trial status to success.
        """
        return self.status == TRIAL_STATUS.SUCCESS

    def set_failed(self, error: Exception) -> 'TrialSplit':
        """
        Set failed trial with exception.

        :param error: catched exception
        :return: self
        """
        self.status = TRIAL_STATUS.FAILED
        self.error = str(error)
        self.error_traceback = traceback.format_exc()
        self.save_parent_trial()
        return self

    def __enter__(self):
        """
        Start trial, and set the trial status to PLANNED.
        """
        self.start_time = datetime.datetime.now()
        self.status = TRIAL_STATUS.STARTED
        self.save_parent_trial()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stop trial, and save end time.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.end_time = datetime.datetime.now()
        if self.delete_pipeline_on_completion:
            del self.pipeline
        if exc_type is not None:
            self.set_failed(exc_val)
            raise exc_val

        self.save_parent_trial()
        return self

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = "Trial.from_json({})".format(str(self.to_json()))
        return s


class TRIAL_STATUS(Enum):
    """
    Trial status.
    """
    FAILED = 'failed'
    STARTED = 'started'
    SUCCESS = 'success'
    PLANNED = 'planned'


class Trials:
    """
    Data object containing auto ml trials.

    .. seealso::
        :class:`AutoMLSequentialWrapper`,
        :class:`RandomSearch`,
        :class:`HyperparamsRepository`,
        :class:`MetaStepMixin`,
        :class:`BaseStep`
    """

    def __init__(
            self,
            trials: List[Trial] = None
    ):
        if trials is None:
            trials = []
        self.trials: List[Trial] = trials

    def get_best_hyperparams(self) -> HyperparameterSamples:
        """
        Get best hyperparams from all trials.

        :return:
        """
        best_score = None
        best_hyperparams = None

        if len(self) == 0:
            raise Exception('Could not get best hyperparams because there were no successful trial.')

        higher_score_is_better = self.trials[-1].is_higher_score_better()

        for trial in self.trials:
            trial_score = trial.get_validation_score()
            if best_score is None or higher_score_is_better == (trial_score > best_score):
                best_score = trial_score
                best_hyperparams = trial.hyperparams

        return best_hyperparams

    def split_good_and_bad_trials(self, quantile_threshold: float, number_of_good_trials_max_cap: int) -> Tuple['Trials', 'Trials']:
        success_trials: Trials = self.filter(TRIAL_STATUS.SUCCESS)

        # Split trials into good and bad using quantile threshold.
        trials_scores = np.array([trial.get_validation_score() for trial in success_trials])

        trial_sorted_indexes = np.argsort(trials_scores)
        if success_trials.is_higher_score_better():
            trial_sorted_indexes = list(reversed(trial_sorted_indexes))

        # In hyperopt they use this to split, where default_gamma_cap = 25. They clip the max of item they use in the good item.
        # default_gamma_cap is link to the number of recent_trial_at_full_weight also.
        # n_below = min(int(np.ceil(gamma * np.sqrt(len(l_vals)))), gamma_cap)
        n_good = int(min(np.ceil(quantile_threshold * len(trials_scores)), number_of_good_trials_max_cap))

        good_trials_indexes = trial_sorted_indexes[:n_good]
        bad_trials_indexes = trial_sorted_indexes[n_good:]

        good_trials = []
        bad_trials = []
        for trial_index, trial in enumerate(success_trials):
            if trial_index in good_trials_indexes:
                good_trials.append(trial)
            if trial_index in bad_trials_indexes:
                bad_trials.append(trial)

        return Trials(trials=good_trials), Trials(trials=bad_trials)

    def is_higher_score_better(self) -> bool:
        """
        Return true if higher score is better.

        :return
        """
        if len(self) == 0:
            return False

        return self.trials[-1].is_higher_score_better()

    def append(self, trial: Trial):
        """
        Add a new trial.

        :param trial: new trial
        :return:
        """
        self.trials.append(trial)

    def filter(self, status: 'TRIAL_STATUS') -> 'Trials':
        """
        Get all the trials with the given trial status.

        :param status: trial status
        :return:
        """
        trials = Trials()
        for trial in self.trials:
            if trial.status == status:
                trials.append(trial)

        return trials

    def get_number_of_split(self):
        if len(self) > 0:
            return len(self[0].validation_splits)
        return 0

    def get_metric_names(self) -> List[str]:
        if len(self) > 0:
            return self[0].validation_splits[0].get_metric_names()
        return []

    def __iter__(self) -> Iterable[Trial]:
        return iter(self.trials)

    def __getitem__(self, item):
        """
        Get trial at the given index.

        :param item: trial index
        :return:
        """
        return self.trials[item]

    def __len__(self):
        return len(self.trials)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = "Trials({})".format(str([str(t) for t in self.trials]))
        return s
