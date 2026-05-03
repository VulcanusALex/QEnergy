# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import math
import unittest

from qenergy.components.base import Component, ActiveComponent, PassiveComponent
from qenergy.components.others import Fiber, Computer, Oven, MotorizedWavePlate
from qenergy.components.lasers import (
    Laser,
    LaserNKTkoheras1550,
    LaserVerdiC532,
    LaserCVPPCL590,
)
from qenergy.components.detectors import (
    DetectorSNSPD1550,
    DetectorInGAs1550,
    DetectorSiAPD780,
)


class TestComponent(unittest.TestCase):
    def test_total_energy_zero_time(self):
        c = Component()
        self.assertEqual(c.total_energy(0), c.fixed_energy)

    def test_total_energy_positive_time(self):
        c = Component()
        c.fixed_energy = 100
        c.power = 50
        self.assertEqual(c.total_energy(10), 100 + 50 * 10)

    def test_total_energy_measured_fallback(self):
        c = Component()
        c.power = 10
        c.fixed_energy = 5
        c.meas_power = 0
        self.assertEqual(c.total_energy_measured(10), 5 + 10 * 10)

    def test_total_energy_measured_none_fallback(self):
        c = Component()
        c.power = 10
        c.fixed_energy = 5
        c.meas_power = None
        self.assertEqual(c.total_energy_measured(10), 5 + 10 * 10)

    def test_total_energy_measured_with_meas(self):
        c = Component()
        c.meas_power = 20
        c.fixed_energy_meas = 50
        self.assertEqual(c.total_energy_measured(10), 50 + 20 * 10)

    def test_repr(self):
        c = Component()
        r = repr(c)
        self.assertIn("component", r)

    def test_passive_is_component(self):
        self.assertTrue(issubclass(PassiveComponent, Component))

    def test_active_is_component(self):
        self.assertTrue(issubclass(ActiveComponent, Component))


class TestFiber(unittest.TestCase):
    def test_1550nm_attenuation(self):
        f = Fiber(1550)
        self.assertAlmostEqual(f.attenuation_fiber_db_km, 0.18)

    def test_780nm_attenuation(self):
        f = Fiber(780)
        self.assertEqual(f.attenuation_fiber_db_km, 4)

    def test_523nm_attenuation(self):
        f = Fiber(523)
        self.assertEqual(f.attenuation_fiber_db_km, 30)

    def test_532nm_attenuation(self):
        f = Fiber(532)
        self.assertEqual(f.attenuation_fiber_db_km, 30)

    def test_unsupported_wavelength(self):
        with self.assertRaises(ValueError):
            Fiber(900)

    def test_transmission_zero_distance(self):
        f = Fiber(1550, length=0)
        self.assertAlmostEqual(f.T, 1.0)

    def test_transmission_decreases_with_distance(self):
        f = Fiber(1550, length=10)
        t10 = f.T
        f.length = 50
        t50 = f.T
        self.assertGreater(t10, t50)

    def test_length_setter_rejects_negative(self):
        f = Fiber(1550)
        with self.assertRaises(ValueError):
            f.length = -5

    def test_length_setter_rejects_string(self):
        f = Fiber(1550)
        with self.assertRaises(ValueError):
            f.length = "abc"

    def test_attenuation_distance_initialized(self):
        f = Fiber(1550)
        self.assertGreater(f.attenuation_distance, 0)

    def test_attenuation_distance_setter(self):
        f = Fiber(1550)
        original_db = f.attenuation_fiber_db_km
        f.attenuation_distance = 50
        self.assertNotEqual(f.attenuation_fiber_db_km, original_db)


class TestLasers(unittest.TestCase):
    def test_laser_init_time(self):
        laser = Laser()
        expected = math.ceil(1e9 / laser.frequency)
        self.assertEqual(laser.init_time, expected)

    def test_nkt_koheras_values(self):
        laser = LaserNKTkoheras1550()
        self.assertEqual(laser.wavelength, 1550)
        self.assertEqual(laser.power, 4)
        self.assertGreater(laser.fixed_energy, 0)

    def test_verdi_c532_meas_power_none(self):
        laser = LaserVerdiC532()
        self.assertIsNone(laser.meas_power)
        energy = laser.total_energy_measured(100)
        self.assertEqual(energy, laser.fixed_energy + 100 * laser.power)


class TestDetectors(unittest.TestCase):
    def test_snspd_1550_efficiency(self):
        d = DetectorSNSPD1550()
        self.assertEqual(d.efficiency, 0.95)
        self.assertTrue(d.require_cryo)

    def test_ingaas_1550_efficiency(self):
        d = DetectorInGAs1550()
        self.assertEqual(d.efficiency, 0.25)

    def test_siapd_780_efficiency(self):
        d = DetectorSiAPD780()
        self.assertEqual(d.efficiency, 0.80)


if __name__ == "__main__":
    unittest.main()
