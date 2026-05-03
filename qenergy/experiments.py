# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Defines the base experiment object.
"""

from typing import List

from qenergy.components import Component


class Experiment:
    """
    Base experiment.

    All experiments have a list of components that can be used to derive the consumed power.
    """

    list_components: List[Component]

    def total_energy(self, time: float) -> float:
        """
        Returns the total energy required to run the experiment for a time t.

        Args:
            time (float): duration of the experiment in seconds.

        Returns:
            float: total energy in Joules.
        """
        return sum(c.total_energy(time) for c in self.list_components)

    def total_energy_measured(self, time: float) -> float:
        """
        Returns the total energy to run the experiment for a time t
        based on the measured values of the components.

        Args:
            time (float): duration of the experiment in seconds.

        Returns:
            float: total energy in Joules based on measured values.
        """
        return sum(c.total_energy_measured(time) for c in self.list_components)

    def total_power(self) -> float:
        """
        Returns the total power consumed by all the components of the setup.

        Returns:
            float: total consumed power in Watts.
        """
        return sum(c.power for c in self.list_components)

    def total_fixed_energy(self) -> float:
        """
        Returns the total fixed (startup) energy of all components.

        Returns:
            float: total fixed energy in Joules.
        """
        return sum(c.fixed_energy for c in self.list_components)
