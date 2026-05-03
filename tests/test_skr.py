# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import unittest
import numpy as np

from qenergy.skr_cv import (
    G,
    skr_asymptotic_homodyne,
    skr_asymptotic_heterodyne,
    skr_asymptotic_homodyne_psk,
    skr_asymptotic_heterodyne_psk,
    skr_asymptotic_cka,
    iab_asymptotic_homodyne,
    iab_asymptotic_heterodyne,
)


class TestG(unittest.TestCase):
    def test_g_zero(self):
        self.assertEqual(G(0), 0)

    def test_g_positive(self):
        result = G(1)
        expected = 2 * np.log2(2) - 1 * np.log2(1)
        self.assertAlmostEqual(result, expected)

    def test_g_monotonic(self):
        self.assertGreater(G(2), G(1))


class TestMutualInformation(unittest.TestCase):
    def test_homodyne_positive(self):
        result = iab_asymptotic_homodyne(Va=1, T=0.5, xi=0.01, eta=0.7, Vel=0.005)
        self.assertGreater(result, 0)

    def test_heterodyne_positive(self):
        result = iab_asymptotic_heterodyne(Va=1, T=0.5, xi=0.01, eta=0.7, Vel=0.005)
        self.assertGreater(result, 0)

    def test_zero_transmission(self):
        result = iab_asymptotic_homodyne(Va=1, T=0, xi=0.01, eta=0.7, Vel=0.005)
        self.assertEqual(result, 0)


class TestSecretKeyRates(unittest.TestCase):
    def test_skr_homodyne_nonnegative(self):
        result = skr_asymptotic_homodyne(
            Va=1, T=0.5, xi=0.005, eta=0.7, Vel=0.005, beta=0.95,
            _number_states=None, _number_users=None,
        )
        self.assertGreaterEqual(result, 0)

    def test_skr_heterodyne_nonnegative(self):
        result = skr_asymptotic_heterodyne(
            Va=1, T=0.5, xi=0.005, eta=0.7, Vel=0.005, beta=0.95,
            _number_states=None, _number_users=None,
        )
        self.assertGreaterEqual(result, 0)

    def test_skr_homodyne_psk_nonnegative(self):
        result = skr_asymptotic_homodyne_psk(
            Va=1, T=0.5, xi=0.005, eta=0.7, Vel=0.005, beta=0.95,
            number_states=4, _number_users=None,
        )
        self.assertGreaterEqual(result, 0)

    def test_skr_heterodyne_psk_nonnegative(self):
        result = skr_asymptotic_heterodyne_psk(
            Va=1, T=0.5, xi=0.005, eta=0.7, Vel=0.005, beta=0.95,
            number_states=4, _number_users=None,
        )
        self.assertGreaterEqual(result, 0)

    def test_skr_cka_nonnegative(self):
        result = skr_asymptotic_cka(
            Va=1, T=0.5, xi=0.005, eta=0.7, Vel=0.005, beta=0.95,
            _number_states=None, number_users=3,
        )
        self.assertGreaterEqual(result, 0)

    def test_skr_zero_at_high_loss(self):
        result = skr_asymptotic_homodyne(
            Va=0.5, T=1e-10, xi=0.1, eta=0.5, Vel=0.1, beta=0.8,
            _number_states=None, _number_users=None,
        )
        self.assertEqual(result, 0)

    def test_skr_decreases_with_loss(self):
        params = dict(Va=2, xi=0.005, eta=0.7, Vel=0.005, beta=0.95,
                      _number_states=None, _number_users=None)
        high_T = skr_asymptotic_homodyne(T=0.8, **params)
        low_T = skr_asymptotic_homodyne(T=0.2, **params)
        self.assertGreaterEqual(high_T, low_T)


class TestDVExperiments(unittest.TestCase):
    def test_bb84_skr_positive(self):
        from qenergy.components.lasers import LaserNKTkoheras1550
        from qenergy.components.detectors import DetectorSNSPD1550
        from qenergy.experiments_dv import BB84Experiment

        laser = LaserNKTkoheras1550()
        det = DetectorSNSPD1550()
        exp = BB84Experiment(80e6, 0.9, 0.1, 1550, 0.01, laser, det, [0, 10, 50])
        skr = exp.compute_secret_key_rate()
        self.assertEqual(len(skr), 3)
        self.assertGreater(skr[0], skr[1])
        self.assertGreater(skr[1], skr[2])

    def test_bb84_time_skr_filters_zero(self):
        from qenergy.components.lasers import LaserNKTkoheras1550
        from qenergy.components.detectors import DetectorSNSPD1550
        from qenergy.experiments_dv import BB84Experiment

        laser = LaserNKTkoheras1550()
        det = DetectorSNSPD1550()
        dist = list(range(0, 500, 10))
        exp = BB84Experiment(80e6, 0.9, 0.1, 1550, 0.01, laser, det, dist)
        tskr = exp.time_skr(1e9)
        self.assertLessEqual(len(tskr), len(dist))
        for t in tskr:
            self.assertGreater(t, 0)

    def test_mutable_default_not_shared(self):
        from qenergy.components.lasers import LaserNKTkoheras1550
        from qenergy.components.detectors import DetectorSNSPD1550
        from qenergy.experiments_dv import BB84Experiment

        laser = LaserNKTkoheras1550()
        det = DetectorSNSPD1550()
        exp1 = BB84Experiment(80e6, 0.9, 0.1, 1550, 0.01, laser, det, [10])
        exp2 = BB84Experiment(80e6, 0.9, 0.1, 1550, 0.01, laser, det, [10])
        self.assertIsNot(exp1.othercomponent, exp2.othercomponent)


if __name__ == "__main__":
    unittest.main()
