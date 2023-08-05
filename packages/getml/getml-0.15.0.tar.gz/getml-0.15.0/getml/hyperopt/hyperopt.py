# Copyright 2021 The SQLNet Company GmbH

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
Contains hyperparameter optimization routines.
"""

import copy
import json
import time

import getml.communication as comm
from getml.data import DataFrame
from getml.data.helpers import _is_typed_list, _remove_trailing_underscores
from getml.helpers import _str
from getml.pipeline import delete, exists, load, scores
from getml.pipeline.helpers import _make_id, _print_time_taken, _transform_peripheral

from .burn_in import latin_hypercube, random
from .kernels import matern52
from .optimization import nelder_mead
from .validation import _validate_hyperopt

# -----------------------------------------------------------------------------


def _get_json_obj(name):
    """
    Retrieves a JSON representation of the hyperopt object *name*
    from the engine.
    """

    # ------------------------------------------------------------
    # Send JSON command to getml engine

    cmd = dict()
    cmd["name_"] = name
    cmd["type_"] = "Hyperopt.refresh"

    sock = comm.send_and_receive_socket(cmd)

    # ------------------------------------------------------------
    # Make sure everything went well and close
    # connection.

    msg = comm.recv_string(sock)

    sock.close()

    if msg[0] != "{":
        comm.engine_exception_handler(msg)

    # ------------------------------------------------------------
    # Parse results.

    json_obj = json.loads(msg)

    return json_obj


# -----------------------------------------------------------------------------


class _Hyperopt:
    """
    Base class that is not meant to be called directly by the user.
    """

    def __init__(
        self,
        param_space,
        pipeline,
        score,
        n_iter,
        seed,
        ratio_iter=1.0,
        optimization_algorithm=nelder_mead,
        optimization_burn_in_algorithm=latin_hypercube,
        optimization_burn_ins=15,
        surrogate_burn_in_algorithm=latin_hypercube,
        gaussian_kernel=matern52,
        gaussian_optimization_burn_in_algorithm=latin_hypercube,
        gaussian_optimization_algorithm=nelder_mead,
        gaussian_optimization_burn_ins=50,
        gaussian_nugget=50,
    ):

        self._id = "NOT SENT TO ENGINE"
        self._type = "_Hyperopt"
        self._score = score

        self._original_param_space = param_space

        self.evaluations = []

        self.pipeline = copy.deepcopy(pipeline)
        self.param_space = param_space
        self.n_iter = n_iter
        self.seed = seed

        self.ratio_iter = ratio_iter
        self.optimization_algorithm = optimization_algorithm
        self.optimization_burn_in_algorithm = optimization_burn_in_algorithm
        self.optimization_burn_ins = optimization_burn_ins
        self.surrogate_burn_in_algorithm = surrogate_burn_in_algorithm
        self.gaussian_kernel = gaussian_kernel
        self.gaussian_optimization_algorithm = gaussian_optimization_algorithm
        self.gaussian_optimization_burn_in_algorithm = (
            gaussian_optimization_burn_in_algorithm
        )
        self.gaussian_optimization_burn_ins = gaussian_optimization_burn_ins
        self.gaussian_nugget = gaussian_nugget

        # ------------------------------------------------------------

        _Hyperopt._supported_params = list(self.__dict__.keys())

    # ----------------------------------------------------------------

    def __repr__(self):
        return str(self)

    # ------------------------------------------------------------

    def _append_underscore(self, some_dict):
        """Helper functions that returns a trailing underscore to all keys in a dict"""

        cmd = dict()

        for kkey in some_dict:
            if kkey == "evaluations":
                cmd[kkey + "_"] = some_dict[kkey]

            elif isinstance(some_dict[kkey], dict):
                cmd[kkey + "_"] = self._append_underscore(some_dict[kkey])

            elif isinstance(some_dict[kkey], list):
                cmd[kkey + "_"] = [
                    self._append_underscore(elem) if isinstance(elem, dict) else elem
                    for elem in some_dict[kkey]
                ]

            else:
                cmd[kkey + "_"] = some_dict[kkey]

        return cmd

    # ------------------------------------------------------------

    def _best_pipeline_name(self):
        if not self.evaluations:
            raise ValueError("The hyperparameter optimization has not been fitted!")

        key = lambda x: x["evaluation"]["score"]

        # The hyperparameter optimization always minimizes.
        # Scores like AUC or RSquared are multiplied by -1.
        return min(self.evaluations, key=key)["pipeline_name"]

    # ------------------------------------------------------------

    def _getml_deserialize(self):
        """
        Expresses the hyperparameter optimization in a form the engine can understand.
        """
        cmd = self._append_underscore(self.__dict__)

        del cmd["_id_"]
        del cmd["_score_"]
        del cmd["_type_"]
        del cmd["_original_param_space_"]

        cmd["name_"] = self.id
        cmd["score_"] = self.score
        cmd["type_"] = self.type

        cmd["pipeline_"] = self.pipeline._getml_deserialize()

        return cmd

    # ----------------------------------------------------------------

    def _parse_json_obj(self, json_obj):

        # ------------------------------------------------------------

        pipeline = self.pipeline._parse_cmd(json_obj["pipeline_"])

        del json_obj["pipeline_"]

        # ------------------------------------------------------------

        kwargs = _remove_trailing_underscores(json_obj)

        # ------------------------------------------------------------

        evaluations = []

        if "evaluations" in kwargs:
            evaluations = kwargs["evaluations"]
            del kwargs["evaluations"]

        # ------------------------------------------------------------

        param_space = kwargs["param_space"]

        del kwargs["param_space"]

        # ------------------------------------------------------------

        del kwargs["name"]
        del kwargs["type"]

        # ------------------------------------------------------------

        id_ = self.id

        self.__init__(param_space=param_space, pipeline=pipeline, **kwargs)

        self._id = id_

        self.evaluations = evaluations

        # ------------------------------------------------------------

        return self

    # ----------------------------------------------------------------

    def _save(self):
        cmd = dict()
        cmd["type_"] = "Hyperopt.save"
        cmd["name_"] = self.id

        comm.send(cmd)

    # ------------------------------------------------------------

    def _send(self):
        self._id = _make_id()
        self.pipeline._id = self._id
        cmd = self._getml_deserialize()
        comm.send(cmd)
        return self

    # ------------------------------------------------------------

    @property
    def best_pipeline(self):
        """
        The best pipeline that is part of the hyperparameter optimization.

        This is always based on the validation
        data you have passed even if you have chosen to
        score the pipeline on other data afterwards.
        """
        name = self._best_pipeline_name()
        return load(name)

    # ------------------------------------------------------------

    def clean_up(self):
        """
        Deletes all pipelines associated with hyperparameter optimization,
        but the best pipeline.
        """
        best_pipeline = self._best_pipeline_name()
        names = [obj["pipeline_name"] for obj in self.evaluations]
        for name in names:
            if name == best_pipeline:
                continue
            if exists(name):
                delete(name)

    # ------------------------------------------------------------

    def fit(
        self,
        population_table_training,
        population_table_validation,
        peripheral_tables=None,
    ):
        """Launches the hyperparameter optimization.

        The provided :class:`~getml.data.DataFrame`
        `population_table_training`, `population_table_validation` and
        `peripheral_tables` must be consistent with the
        :class:`~getml.data.Placeholders` provided when constructing
        the base model.

        Args:
            population_table_training(:class:`~getml.data.DataFrame`):
                The population table that pipelines will be trained on.

            population_table_validation(:class:`~getml.data.DataFrame`):
                The population table that pipelines will be evaluated on.

            peripheral_tables(:class:`~getml.data.DataFrame`): The
                peripheral tables used to provide additional
                information for the population tables.

        Raises:
            TypeError: If any of `population_table_training`,
                `population_table_validation` or `peripheral_tables`
                is not of type :class:`~getml.data.DataFrame`.
            KeyError: If an unsupported instance variable is
                encountered (via
                :meth:`~getml.hyperopt._Hyperopt.validate`).
            TypeError: If any instance variable is of wrong type (via
                :meth:`~getml.hyperopt._Hyperopt.validate`).
            ValueError: If any instance variable does not match its
                possible choices (string) or is out of the expected
                bounds (numerical) (via
                :meth:`~getml.hyperopt._Hyperopt.validate`).

        """

        # -----------------------------------------------------------

        peripheral_tables = peripheral_tables or []

        # -----------------------------------------------------------

        self.pipeline.check(
            population_table=population_table_training,
            peripheral_tables=peripheral_tables,
        )

        # -----------------------------------------------------------

        peripheral_tables = _transform_peripheral(
            peripheral_tables, self.pipeline.peripheral
        )

        # -----------------------------------------------------------

        if not isinstance(population_table_training, DataFrame):
            raise TypeError(
                """'population_table_training'
                                must be a getml.data.DataFrame"""
            )

        if not isinstance(population_table_validation, DataFrame):
            raise TypeError(
                """'population_table_validation'
                                must be a getml.data.DataFrame"""
            )

        if not _is_typed_list(peripheral_tables, DataFrame):
            raise TypeError(
                """'peripheral_tables' must be a
                              getml.data.DataFrame, a list or
                              dictionary"""
            )

        # -----------------------------------------------------------

        self._send()

        cmd = dict()

        cmd["name_"] = self.id
        cmd["type_"] = "Hyperopt.launch"

        cmd["population_training_name_"] = population_table_training.name
        cmd["population_validation_name_"] = population_table_validation.name
        cmd["peripheral_names_"] = [elem.name for elem in peripheral_tables]

        sock = comm.send_and_receive_socket(cmd)

        # ------------------------------------------------------------

        begin = time.time()

        msg = comm.log(sock)

        end = time.time()

        # ------------------------------------------------------------

        if msg != "Success!":
            comm.engine_exception_handler(msg)

        print()
        _print_time_taken(begin, end, "Time taken: ")

        self._save()

        return self.refresh()

    # ------------------------------------------------------------

    @property
    def id(self):
        """
        Name of the hyperparameter optimization.
        This is used to uniquely identify it on the engine.
        """
        return self._id

    # ------------------------------------------------------------

    @property
    def name(self):
        """
        Returns the ID of the hyperparameter optimization.
        The name property is kept for backward compatibility.
        """
        return self._id

    # ------------------------------------------------------------

    def refresh(self):
        """Reloads the hyperparameter optimization from the engine.

        Raises:
            IOError:
                If the engine did not send a proper model.

        Returns:
            :class:`~getml.pipeline.Pipeline`:
                Current instance
        """
        json_obj = _get_json_obj(self.id)
        return self._parse_json_obj(json_obj)

    # ------------------------------------------------------------

    @property
    def score(self):
        """
        The score to be optimized.
        """
        return self._score

    # ------------------------------------------------------------

    @property
    def type(self):
        """
        The algorithm used for the hyperparameter optimization.
        """
        return self._type


# -----------------------------------------------------------------------------


class GaussianHyperparameterSearch(_Hyperopt):
    """Bayesian hyperparameter optimization using a Gaussian process.

    After a burn-in period,
    a Gaussian process is used to pick the most promising
    parameter combination to be evaluated next based on the knowledge gathered
    throughout previous evaluations. Accessing the quality of potential
    combinations will be done using the expected information (EI).

    Args:
        param_space (dict):
            Dictionary containing numerical arrays of length two
            holding the lower and upper bounds of all parameters which
            will be altered in `pipeline` during the hyperparameter
            optimization.

            If we have two feature learners and one predictor,
            the hyperparameter space might look like this:

            .. code-block:: python

                param_space = {
                    "feature_learners": [
                        {
                            "num_features": [10, 50],
                        },
                        {
                            "max_depth": [1, 10],
                            "min_num_samples": [100, 500],
                            "num_features": [10, 50],
                            "reg_lambda": [0.0, 0.1],
                            "shrinkage": [0.01, 0.4]
                        }],
                    "predictors": [
                        {
                            "reg_lambda": [0.0, 10.0]
                        }
                    ]
                }

            If we only want to optimize the predictor, then
            we can leave out the feature learners.

        pipeline (:class:`~getml.pipeline.Pipeline`):
            Base pipeline used to derive all models fitted and scored
            during the hyperparameter optimization. Be careful when
            constructing it since only the parameters present in
            `param_space` will be overwritten. It defines the data
            schema and any hyperparameters that are not optimized.

        score (str, optional):
            The score to optimize. Must be from
            :mod:`~getml.pipeline.scores`.

        n_iter (int, optional):
            Number of iterations in the hyperparameter optimization
            and thus the number of parameter combinations to draw and
            evaluate. Range: [1, :math:`\\infty`]

        seed (int, optional):
            Seed used for the random number generator that underlies
            the sampling procedure to make the calculation
            reproducable. Due to nature of the underlying algorithm,
            this is only the case if the fit is done without
            multithreading. To reflect this, a `seed` of None
            is only allowed to be set
            to an actual integer if both ``num_threads`` and
            ``n_jobs`` instance variables of the ``predictor`` and
            ``feature_selector`` in `model` - if they are instances of
            either :class:`~getml.predictors.XGBoostRegressor` or
            :class:`~getml.predictors.XGBoostClassifier` - are set to
            1. Internally, a `seed` of None will be mapped to
            5543. Range: [0, :math:`\\infty`]

        ratio_iter (float, optional):
            Ratio of the iterations used for the burn-in.
            For a `ratio_iter` of 1.0, all iterations will be
            spent in the burn-in period resulting in an equivalence of
            this class to
            :class:`~getml.hyperopt.LatinHypercubeSearch` or
            :class:`~getml.hyperopt.RandomSearch` - depending on
            `surrogate_burn_in_algorithm`. Range: [0, 1]

            As a *rule of thumb* at least 70 percent of the evaluations
            should be spent in the burn-in phase. The more comprehensive
            the exploration of the `param_space` during the burn-in,
            the less likely it is that the Gaussian process gets stuck in
            local minima.

        optimization_algorithm (string, optional):
            Determines the optimization algorithm used for the local
            search in the optimization of the expected information
            (EI). Must be from
            :mod:`~getml.hyperopt.optimization`.

        optimization_burn_in_algorithm (string, optional):
            Specifies the algorithm used to draw initial points in the
            burn-in period of the optimization of the expected
            information (EI). Must be from :mod:`~getml.hyperopt.burn_in`.

        optimization_burn_ins (int, optional):
            Number of random evaluation points used during the burn-in
            of the minimization of the expected information (EI).
            After the surrogate model - the Gaussian process - was
            successfully fitted to the previous parameter combination,
            the algorithm is able to calculate the EI for a given point. In
            order to get to the next combination, the EI has to be
            maximized over the whole parameter space. Much like the
            GaussianProcess itself, this requires a burn-in phase.
            Range: [3, :math:`\\infty`]

        surrogate_burn_in_algorithm (string, optional):
            Specifies the algorithm used to draw new parameter
            combinations during the burn-in period.
            Must be from :mod:`~getml.hyperopt.burn_in`.

        gaussian_kernel (string, optional):
            Specifies the 1-dimensional kernel of the Gaussian process
            which will be used along each dimension of the parameter
            space. All of the choices below will result in continuous
            sample paths and their main difference is the degree of
            smoothness of the results with 'exp' yielding the least
            and 'gauss' yielding the most smooth paths.
            Must be from :mod:`~getml.hyperopt.kernels`.

        gaussian_optimization_algorithm (string, optional):
            Determines the optimization algorithm used for the local
            search in the fitting of the Gaussian process to the
            previous parameter combinations. Must be from
            :mod:`~getml.hyperopt.optimization`.

        gaussian_optimization_burn_in_algorithm (string, optional):
            Specifies the algorithm used to draw new parameter
            combinations during the burn-in period of the optimization
            of the Gaussian process.
            Must be from :mod:`~getml.hyperopt.burn_in`.

        gaussian_optimization_burn_ins (int, optional):
            Number of random evaluation points used during the burn-in
            of the fitting of the Gaussian process. Range: [3,
            :math:`\\infty`]

    Raises:
        KeyError: If an unsupported instance variable is
            encountered (via
            :meth:`~getml.hyperopt.GaussianHyperparameterSearch.validate`).
        TypeError: If any instance variable is of wrong type (via
            :meth:`~getml.hyperopt.GaussianHyperparameterSearch.validate`).
        ValueError: If any instance variable does not match its
            possible choices (string) or is out of the expected
            bounds (numerical) (via
            :meth:`~getml.hyperopt.GaussianHyperparameterSearch.validate`).

    Note:
        A Gaussian hyperparameter search works like this:

            - It begins with a burn-in phase, usually about 70% to 90%
              of all iterations. During that burn-in phase, the hyperparameter
              space is sampled more or less at random. You can control
              this phase using ``ratio_iter`` and ``surrogate_burn_in_algorithm``.

            - Once enough information has been collected, it fits a
              Gaussian process on the hyperparameters with the ``score`` we want to
              maximize or minimize as the predicted variable. Note that the
              Gaussian process has hyperparameters itself, which are also optimized.
              You can control this phase using ``gaussian_kernel``,
              ``gaussian_optimization_algorithm``,
              ``gaussian_optimization_burn_in_algorithm`` and
              ``gaussian_optimization_burn_ins``.

            - It then uses the Gaussian process to predict the expected information
              (EI), which is how much additional information it might get from evaluating
              a particular point in the hyperparameter space. The expected information
              is to be maximized. The point in the hyperparameter space with
              the maximum expected information is the next point that is actually
              evaluated (meaning a new pipeline with these hyperparameters is trained).
              You can control this phase using ``optimization_algorithm``,
              ``optimization_burn_ins`` and ``optimization_burn_in_algorithm``.

        In a nutshell, the GaussianHyperparameterSearch behaves like human data scientists:

            - At first, it picks random hyperparameter combinations.

            - Once it has gained a better understanding of the hyperparameter space,
              it starts evaluating hyperparameter combinations that are
              particularly interesting.

    References:
        - `Carl Edward Rasmussen and Christopher K. I. Williams, MIT
          Press, 2006 <http://www.gaussianprocess.org/gpml/>`_
        - `Julien Villemonteix, Emmanuel Vazquez, and Eric Walter, 2009
          <https://arxiv.org/pdf/cs/0611143.pdf>`_

    Example:

        .. code-block:: python

            from getml import data
            from getml import datasets
            from getml import engine
            from getml import feature_learning
            from getml.feature_learning import aggregations
            from getml.feature_learning import loss_functions
            from getml import hyperopt
            from getml import pipeline
            from getml import predictors

            # ----------------

            engine.set_project("examples")

            # ----------------

            population_table, peripheral_table = datasets.make_numerical()

            # ----------------
            # Construct placeholders

            population_placeholder = data.Placeholder("POPULATION")
            peripheral_placeholder = data.Placeholder("PERIPHERAL")
            population_placeholder.join(peripheral_placeholder, "join_key", "time_stamp")

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            fe1 = feature_learning.MultirelModel(
                aggregation=[
                    aggregations.Count,
                    aggregations.Sum
                ],
                loss_function=loss_functions.SquareLoss,
                num_features=10,
                share_aggregations=1.0,
                max_length=1,
                num_threads=0
            )

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            fe2 = feature_learning.RelboostModel(
                loss_function=loss_functions.SquareLoss,
                num_features=10
            )

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            predictor = predictors.LinearRegression()

            # ----------------

            pipe = pipeline.Pipeline(
                population=population_placeholder,
                peripheral=[peripheral_placeholder],
                feature_learners=[fe1, fe2],
                predictors=[predictor]
            )

            # ----------------
            # Build a hyperparameter space.
            # We have two feature learners and one
            # predictor, so this is how we must
            # construct our hyperparameter space.
            # If we only wanted to optimize the predictor,
            # we could just leave out the feature_learners.

            param_space = {
                "feature_learners": [
                    {
                        "num_features": [10, 50],
                    },
                    {
                        "max_depth": [1, 10],
                        "min_num_samples": [100, 500],
                        "num_features": [10, 50],
                        "reg_lambda": [0.0, 0.1],
                        "shrinkage": [0.01, 0.4]
                    }],
                "predictors": [
                    {
                        "reg_lambda": [0.0, 10.0]
                    }
                ]
            }

            # ----------------
            # Wrap a GaussianHyperparameterSearch around the reference model

            gaussian_search = hyperopt.GaussianHyperparameterSearch(
                pipeline=pipe,
                param_space=param_space,
                n_iter=30,
                score=pipeline.scores.rsquared
            )

            gaussian_search.fit(
                population_table_training=population_table,
                population_table_validation=population_table,
                peripheral_tables=[peripheral_table]
            )

            # ----------------

            # We want 5 additional iterations.
            gaussian_search.n_iter = 5

            # We do not want another burn-in-phase,
            # so we set ratio_iter to 0.
            gaussian_search.ratio_iter = 0.0

            # This widens the hyperparameter space.
            gaussian_search.param_space["feature_learners"][1]["num_features"] = [10, 100]

            # This narrows the hyperparameter space.
            gaussian_search.param_space["predictors"][0]["reg_lambda"] = [0.0, 0.0]

            # This continues the hyperparameter search using the previous iterations as
            # prior knowledge.
            gaussian_search.fit(
                population_table_training=population_table,
                population_table_validation=population_table,
                peripheral_tables=[peripheral_table]
            )

            # ----------------

            all_hyp = hyperopt.list_hyperopts()

            best_pipeline = gaussian_search.best_pipeline
    """

    def __init__(
        self,
        param_space,
        pipeline,
        score=scores.rmse,
        n_iter=100,
        seed=5483,
        ratio_iter=0.80,
        optimization_algorithm=nelder_mead,
        optimization_burn_in_algorithm=latin_hypercube,
        optimization_burn_ins=500,
        surrogate_burn_in_algorithm=latin_hypercube,
        gaussian_kernel=matern52,
        gaussian_optimization_burn_in_algorithm=latin_hypercube,
        gaussian_optimization_algorithm=nelder_mead,
        gaussian_optimization_burn_ins=500,
        gaussian_nugget=50,
    ):

        super().__init__(
            param_space=param_space,
            pipeline=pipeline,
            score=score,
            n_iter=n_iter,
            seed=seed,
            ratio_iter=ratio_iter,
            optimization_algorithm=optimization_algorithm,
            optimization_burn_in_algorithm=optimization_burn_in_algorithm,
            optimization_burn_ins=optimization_burn_ins,
            surrogate_burn_in_algorithm=surrogate_burn_in_algorithm,
            gaussian_kernel=gaussian_kernel,
            gaussian_optimization_algorithm=gaussian_optimization_algorithm,
            gaussian_optimization_burn_in_algorithm=gaussian_optimization_burn_in_algorithm,
            gaussian_optimization_burn_ins=gaussian_optimization_burn_ins,
            gaussian_nugget=gaussian_nugget,
        )

        self._type = "GaussianHyperparameterSearch"

        self.validate()

    # ----------------------------------------------------------------

    def __str__(self):
        obj_dict = copy.deepcopy(self.__dict__)
        del obj_dict["pipeline"]
        del obj_dict["param_space"]
        del obj_dict["evaluations"]
        obj_dict["type"] = self.type
        obj_dict["score"] = self.score
        return _str(obj_dict)

    # ------------------------------------------------------------

    def validate(self):
        """
        Validate the parameters of the hyperparameter optimization.
        """
        _validate_hyperopt(_Hyperopt._supported_params, **self.__dict__)


# -----------------------------------------------------------------------------


class LatinHypercubeSearch(_Hyperopt):
    """Latin hypercube sampling of the hyperparameters.

    Uses a multidimensional, uniform cumulative distribution function
    to drawn the random numbers from. For drawing `n_iter` samples,
    the distribution will be divided in `n_iter`*`n_iter` hypercubes
    of equal size (`n_iter` per dimension). `n_iter` of them will be
    selected in such a way only one per dimension is used and an
    independent and identically-distributed (iid) random number is
    drawn within the boundaries of the hypercube.

    A latin hypercube search can be seen as a compromise between
    a grid search, which iterates through the entire hyperparameter
    space, and a random search, which draws completely random samples
    from the hyperparameter space.

    Args:
        param_space (dict):
            Dictionary containing numerical arrays of length two
            holding the lower and upper bounds of all parameters which
            will be altered in `pipeline` during the hyperparameter
            optimization.

            If we have two feature learners and one predictor,
            the hyperparameter space might look like this:

            .. code-block:: python

                param_space = {
                    "feature_learners": [
                        {
                            "num_features": [10, 50],
                        },
                        {
                            "max_depth": [1, 10],
                            "min_num_samples": [100, 500],
                            "num_features": [10, 50],
                            "reg_lambda": [0.0, 0.1],
                            "shrinkage": [0.01, 0.4]
                        }],
                    "predictors": [
                        {
                            "reg_lambda": [0.0, 10.0]
                        }
                    ]
                }

            If we only want to optimize the predictor, then
            we can leave out the feature learners.

        pipeline (:class:`~getml.pipeline.Pipeline`):
            Base pipeline used to derive all models fitted and scored
            during the hyperparameter optimization. Be careful in
            constructing it since only those parameters present in
            `param_space` will be overwritten. It defines the data
            schema and any hyperparameters that are not optimized.

        score (str, optional):
            The score to optimize. Must be from
            :mod:`~getml.pipeline.scores`.

        n_iter (int, optional):
            Number of iterations in the hyperparameter optimization
            and thus the number of parameter combinations to draw and
            evaluate. Range: [1, :math:`\\infty`]

        seed (int, optional):
            Seed used for the random number generator that underlies
            the sampling procedure to make the calculation
            reproducible. Due to nature of the underlying algorithm
            this is only the case if the fit is done without
            multithreading. To reflect this, a `seed` of None
            represents an unreproducible and is only allowed to be set
            to an actual integer if both ``num_threads`` and
            ``n_jobs`` instance variables of the ``predictor`` and
            ``feature_selector`` in `model` - if they are instances of
            either :class:`~getml.predictors.XGBoostRegressor` or
            :class:`~getml.predictors.XGBoostClassifier` - are set to
            1. Internally, a `seed` of None will be mapped to
            5543. Range: [0, :math:`\\infty`]

    Raises:
        KeyError: If an unsupported instance variable is
            encountered.
        TypeError: If any instance variable is of wrong type.
        ValueError: If any instance variable does not match its
            possible choices (string) or is out of the expected
            bounds (numerical).
        ValueError: If no ``predictor`` is present in the provided
            ``pipeline``.

    Example:

        .. code-block:: python

            from getml import data
            from getml import datasets
            from getml import engine
            from getml import feature_learning
            from getml.feature_learning import aggregations
            from getml.feature_learning import loss_functions
            from getml import hyperopt
            from getml import pipeline
            from getml import predictors

            # ----------------

            engine.set_project("examples")

            # ----------------

            population_table, peripheral_table = datasets.make_numerical()

            # ----------------
            # Construct placeholders

            population_placeholder = data.Placeholder("POPULATION")
            peripheral_placeholder = data.Placeholder("PERIPHERAL")
            population_placeholder.join(peripheral_placeholder, "join_key", "time_stamp")

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            fe1 = feature_learning.MultirelModel(
                aggregation=[
                    aggregations.Count,
                    aggregations.Sum
                ],
                loss_function=loss_functions.SquareLoss,
                num_features=10,
                share_aggregations=1.0,
                max_length=1,
                num_threads=0
            )

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            fe2 = feature_learning.RelboostModel(
                loss_function=loss_functions.SquareLoss,
                num_features=10
            )

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            predictor = predictors.LinearRegression()

            # ----------------

            pipe = pipeline.Pipeline(
                population=population_placeholder,
                peripheral=[peripheral_placeholder],
                feature_learners=[fe1, fe2],
                predictors=[predictor]
            )

            # ----------------
            # Build a hyperparameter space.
            # We have two feature learners and one
            # predictor, so this is how we must
            # construct our hyperparameter space.
            # If we only wanted to optimize the predictor,
            # we could just leave out the feature_learners.

            param_space = {
                "feature_learners": [
                    {
                        "num_features": [10, 50],
                    },
                    {
                        "max_depth": [1, 10],
                        "min_num_samples": [100, 500],
                        "num_features": [10, 50],
                        "reg_lambda": [0.0, 0.1],
                        "shrinkage": [0.01, 0.4]
                    }],
                "predictors": [
                    {
                        "reg_lambda": [0.0, 10.0]
                    }
                ]
            }

            # ----------------
            # Wrap a LatinHypercubeSearch around the reference model

            latin_search = hyperopt.LatinHypercubeSearch(
                pipeline=pipe,
                param_space=param_space,
                n_iter=30,
                score=pipeline.scores.rsquared
            )

            latin_search.fit(
                population_table_training=population_table,
                population_table_validation=population_table,
                peripheral_tables=[peripheral_table]
            )
    """

    def __init__(
        self, param_space, pipeline, score=scores.rmse, n_iter=100, seed=5483, **kwargs
    ):

        super().__init__(
            param_space=param_space,
            pipeline=pipeline,
            score=score,
            n_iter=n_iter,
            seed=seed,
            **kwargs
        )

        self._type = "LatinHypercubeSearch"

        self.surrogate_burn_in_algorithm = latin_hypercube

        self.validate()

    # ----------------------------------------------------------------

    def __str__(self):
        obj_dict = dict()
        obj_dict["type"] = self.type
        obj_dict["score"] = self.score
        obj_dict["n_iter"] = self.n_iter
        obj_dict["seed"] = self.seed
        return _str(obj_dict)

    # ------------------------------------------------------------

    def validate(self):
        """
        Validate the parameters of the hyperparameter optimization.
        """
        _validate_hyperopt(_Hyperopt._supported_params, **self.__dict__)

        if self.surrogate_burn_in_algorithm != latin_hypercube:
            raise ValueError(
                "'surrogate_burn_in_algorithm' must be '" + latin_hypercube + "'."
            )

        if self.ratio_iter != 1.0:
            raise ValueError("'ratio_iter' must be 1.0.")


# -----------------------------------------------------------------------------


class RandomSearch(_Hyperopt):
    """Uniformly distributed sampling of the hyperparameters.

    During every iteration, a new set of hyperparameters is chosen at random
    by uniformly drawing a random value in between the lower and upper
    bound for each dimension of `param_space` independently.

    Args:
        param_space (dict):
            Dictionary containing numerical arrays of length two
            holding the lower and upper bounds of all parameters which
            will be altered in `pipeline` during the hyperparameter
            optimization.

            If we have two feature learners and one predictor,
            the hyperparameter space might look like this:

            .. code-block:: python

                param_space = {
                    "feature_learners": [
                        {
                            "num_features": [10, 50],
                        },
                        {
                            "max_depth": [1, 10],
                            "min_num_samples": [100, 500],
                            "num_features": [10, 50],
                            "reg_lambda": [0.0, 0.1],
                            "shrinkage": [0.01, 0.4]
                        }],
                    "predictors": [
                        {
                            "reg_lambda": [0.0, 10.0]
                        }
                    ]
                }

            If we only want to optimize the predictor, then
            we can leave out the feature learners.

        pipeline (:class:`~getml.pipeline.Pipeline`):
            Base pipeline used to derive all models fitted and scored
            during the hyperparameter optimization. Be careful in
            constructing it since only those parameters present in
            `param_space` will be overwritten. It defines the data
            schema and any hyperparameters that are not optimized.

        score (str, optional):
            The score to optimize. Must be from
            :mod:`~getml.pipeline.scores`.

        n_iter (int, optional):
            Number of iterations in the hyperparameter optimization
            and thus the number of parameter combinations to draw and
            evaluate. Range: [1, :math:`\\infty`]

        seed (int, optional):
            Seed used for the random number generator that underlies
            the sampling procedure to make the calculation
            reproducible. Due to nature of the underlying algorithm
            this is only the case if the fit is done without
            multithreading. To reflect this, a `seed` of None
            represents an unreproducible and is only allowed to be set
            to an actual integer if both ``num_threads`` and
            ``n_jobs`` instance variables of the ``predictor`` and
            ``feature_selector`` in `model` - if they are instances of
            either :class:`~getml.predictors.XGBoostRegressor` or
            :class:`~getml.predictors.XGBoostClassifier` - are set to
            1. Internally, a `seed` of None will be mapped to
            5543. Range: [0, :math:`\\infty`]

    Raises:
        KeyError: If an unsupported instance variable is
            encountered.
        TypeError: If any instance variable is of wrong type.
        ValueError: If any instance variable does not match its
            possible choices (string) or is out of the expected
            bounds (numerical).
        ValueError: If no ``predictor`` is present in the provided
            ``pipeline``.

    Example:

        .. code-block:: python

            from getml import data
            from getml import datasets
            from getml import engine
            from getml import feature_learning
            from getml.feature_learning import aggregations
            from getml.feature_learning import loss_functions
            from getml import hyperopt
            from getml import pipeline
            from getml import predictors

            # ----------------

            engine.set_project("examples")

            # ----------------

            population_table, peripheral_table = datasets.make_numerical()

            # ----------------
            # Construct placeholders

            population_placeholder = data.Placeholder("POPULATION")
            peripheral_placeholder = data.Placeholder("PERIPHERAL")
            population_placeholder.join(peripheral_placeholder, "join_key", "time_stamp")

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            fe1 = feature_learning.MultirelModel(
                aggregation=[
                    aggregations.Count,
                    aggregations.Sum
                ],
                loss_function=loss_functions.SquareLoss,
                num_features=10,
                share_aggregations=1.0,
                max_length=1,
                num_threads=0
            )

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            fe2 = feature_learning.RelboostModel(
                loss_function=loss_functions.SquareLoss,
                num_features=10
            )

            # ----------------
            # Base model - any parameters not included
            # in param_space will be taken from this.

            predictor = predictors.LinearRegression()

            # ----------------

            pipe = pipeline.Pipeline(
                population=population_placeholder,
                peripheral=[peripheral_placeholder],
                feature_learners=[fe1, fe2],
                predictors=[predictor]
            )

            # ----------------
            # Build a hyperparameter space.
            # We have two feature learners and one
            # predictor, so this is how we must
            # construct our hyperparameter space.
            # If we only wanted to optimize the predictor,
            # we could just leave out the feature_learners.

            param_space = {
                "feature_learners": [
                    {
                        "num_features": [10, 50],
                    },
                    {
                        "max_depth": [1, 10],
                        "min_num_samples": [100, 500],
                        "num_features": [10, 50],
                        "reg_lambda": [0.0, 0.1],
                        "shrinkage": [0.01, 0.4]
                    }],
                "predictors": [
                    {
                        "reg_lambda": [0.0, 10.0]
                    }
                ]
            }

            # ----------------
            # Wrap a RandomSearch around the reference model

            random_search = hyperopt.RandomSearch(
                pipeline=pipe,
                param_space=param_space,
                n_iter=30,
                score=pipeline.scores.rsquared
            )

            random_search.fit(
                population_table_training=population_table,
                population_table_validation=population_table,
                peripheral_tables=[peripheral_table]
            )
    """

    def __init__(
        self, param_space, pipeline, score=scores.rmse, n_iter=100, seed=5483, **kwargs
    ):

        super().__init__(
            param_space=param_space,
            pipeline=pipeline,
            score=score,
            n_iter=n_iter,
            seed=seed,
            **kwargs
        )

        self._type = "RandomSearch"

        self.surrogate_burn_in_algorithm = random

        self.validate()

    # ----------------------------------------------------------------

    def __str__(self):
        obj_dict = dict()
        obj_dict["type"] = self.type
        obj_dict["score"] = self.score
        obj_dict["n_iter"] = self.n_iter
        obj_dict["seed"] = self.seed
        return _str(obj_dict)

    # ------------------------------------------------------------

    def validate(self):
        """
        Validate the parameters of the hyperparameter optimization.
        """
        _validate_hyperopt(_Hyperopt._supported_params, **self.__dict__)

        if self.surrogate_burn_in_algorithm != random:
            raise ValueError("'surrogate_burn_in_algorithm' must be '" + random + "'.")

        if self.ratio_iter != 1.0:
            raise ValueError("'ratio_iter' must be 1.0.")


# -----------------------------------------------------------------------------
