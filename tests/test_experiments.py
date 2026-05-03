# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import unittest

from qenergy.components.base import Component
from qenergy.experiments import Experiment


class MockComponent(Component):
    name = "mock"
    power = 100
    fixed_energy = 500
    meas_power = 80
    fixed_energy_meas = 400


class TestExperiment(unittest.TestCase):
    def setUp(self):
        self.exp = Experiment()
        self.exp.list_components = [MockComponent(), MockComponent()]

    def test_total_energy(self):
        energy = self.exp.total_energy(10)
        expected = 2 * (500 + 100 * 10)
        self.assertEqual(energy, expected)

    def test_total_energy_measured(self):
        energy = self.exp.total_energy_measured(10)
        expected = 2 * (400 + 80 * 10)
        self.assertEqual(energy, expected)

    def test_total_power(self):
        self.assertEqual(self.exp.total_power(), 200)

    def test_total_fixed_energy(self):
        self.assertEqual(self.exp.total_fixed_energy(), 1000)

    def test_empty_experiment(self):
        exp = Experiment()
        exp.list_components = []
        self.assertEqual(exp.total_energy(100), 0)
        self.assertEqual(exp.total_power(), 0)


if __name__ == "__main__":
    unittest.main()
