# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
from typing import Any, List

import click
from pydantic.main import BaseModel

from lean.components.util.logger import Logger
from lean.models.api import QCParameter
from lean.models.optimizer import (OptimizationConstraint, OptimizationConstraintOperator, OptimizationExtremum,
                                   OptimizationParameter, OptimizationTarget)


class Option(BaseModel):
    """The Option class represents a choosable option with an internal id and a display-friendly label."""
    id: Any
    label: str


class OptimizerConfigManager:
    """The OptimizationConfigurer contains methods to interactively configure parts of the optimizer."""

    def __init__(self, logger: Logger) -> None:
        """Creates a new OptimizationConfigurer instance.

        :param logger: the logger to use when printing messages
        """
        self._logger = logger

        # The targets that are available in the cloud
        self._available_targets = [
            ("TotalPerformance.PortfolioStatistics.SharpeRatio", "Sharpe Ratio"),
            ("TotalPerformance.PortfolioStatistics.CompoundingAnnualReturn", "Compounding Annual Return"),
            ("TotalPerformance.PortfolioStatistics.ProbabilisticSharpeRatio", "Probabilistic Sharpe Ratio"),
            ("TotalPerformance.PortfolioStatistics.Drawdown", "Drawdown")
        ]

    def configure_strategy(self, cloud: bool) -> str:
        """Asks the user for the optimization strategy to use.

        :param cloud: True if the optimization will be ran in the cloud, False if not
        :return: the class name of the optimization strategy to use
        """
        options = [
            Option(id="QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy", label="Grid Search")
        ]

        if not cloud:
            options.append(
                Option(id="QuantConnect.Optimizer.Strategies.EulerSearchOptimizationStrategy", label="Euler Search")
            )

        return self._choose_from_list("Select the optimization strategy to use", options)

    def configure_target(self) -> OptimizationTarget:
        """Asks the user for the optimization target.

        :return: the chosen optimization target
        """
        # Create a list of options containing a "<target> (min)" and "<target> (max)" option for every target
        options = list(itertools.product(self._available_targets,
                                         [OptimizationExtremum.Minimum, OptimizationExtremum.Maximum]))
        options = [Option(id=OptimizationTarget(target=option[0][0], extremum=option[1]),
                          label=f"{option[0][1]} ({option[1]})") for option in options]

        return self._choose_from_list("Select an optimization target", options)

    def configure_parameters(self, project_parameters: List[QCParameter]) -> List[OptimizationParameter]:
        """Asks the user which parameters need to be optimized and with what constraints.

        :param project_parameters: the parameters of the project that will be optimized
        :return: the chosen optimization parameters
        """
        results: List[OptimizationParameter] = []

        for parameter in project_parameters:
            if not click.confirm(f"Should the '{parameter.key}' parameter be optimized?", default=True):
                continue

            minimum = click.prompt(f"Minimum value for '{parameter.key}'", type=click.FLOAT)
            maximum = click.prompt(f"Maximum value for '{parameter.key}'", type=click.FloatRange(min=minimum))
            step_size = click.prompt(f"Step size for '{parameter.key}'", type=click.FloatRange(min=0.0), default=1.0)

            results.append(OptimizationParameter(name=parameter.key, min=minimum, max=maximum, step=step_size))

        return results

    def configure_constraints(self) -> List[OptimizationConstraint]:
        """Asks the user for the optimization constraints.

        :return: the chosen optimization constraints
        """
        self._logger.info("Constraints can be used to filter out backtests from the results")
        self._logger.info("When a backtest doesn't comply with the constraints it is dropped from the results")
        self._logger.info("Example constraint: Drawdown < 0.25 (Drawdown less than 25%)")

        results: List[OptimizationConstraint] = []

        while True:
            results_str = ", ".join([str(result) for result in results])
            results_str = results_str or "None"
            self._logger.info(f"Current constraints: {results_str}")

            if not click.confirm("Do you want to add a constraint?", default=False):
                return results

            target_options = [Option(id=target[0], label=target[1]) for target in self._available_targets]
            target = self._choose_from_list("Select a constraint target", target_options)

            operator = self._choose_from_list("Select a constraint operator (<value> will be asked after this)", [
                Option(id=OptimizationConstraintOperator.Less, label="Less than <value>"),
                Option(id=OptimizationConstraintOperator.LessOrEqual, label="Less than or equal to <value>"),
                Option(id=OptimizationConstraintOperator.Greater, label="Greater than <value>"),
                Option(id=OptimizationConstraintOperator.GreaterOrEqual, label="Greater than or equal to <value>"),
                Option(id=OptimizationConstraintOperator.Equals, label="Equal to <value>"),
                Option(id=OptimizationConstraintOperator.NotEquals, label="Not equal to <value>")
            ])

            value = click.prompt("Set the <value> for the selected operator", type=click.FLOAT)

            results.append(OptimizationConstraint(**{"target": target, "operator": operator, "target-value": value}))

    def _choose_from_list(self, text: str, options: List[Option]) -> Any:
        """Asks the user to select an option from a list of possible options.

        The user will not be prompted for input if there is only a single option.

        :param text: the text to display before prompting
        :param options: the available options
        :return: the chosen option's id
        """
        if len(options) == 1:
            return options[0]

        self._logger.info(f"{text}:")

        for i, option in enumerate(options):
            self._logger.info(f"{i + 1}) {option.label}")

        number = click.prompt("Enter a number", type=click.IntRange(min=1, max=len(options)))
        return options[number - 1].id
