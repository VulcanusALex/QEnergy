# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from pathlib import Path

EXPORT_DIR = Path(__file__).parent.parent / "exports"

FULL_TEXTWIDTH_PT = 510
COLUMNWIDTH_PT = 246

BASE_TEXTWIDTH_IN = FULL_TEXTWIDTH_PT / 72
COLUMNWIDTH_IN = COLUMNWIDTH_PT / 72

FIGSIZE_FULL = (BASE_TEXTWIDTH_IN, BASE_TEXTWIDTH_IN * 9 / 16)
FIGSIZE_HALF = (COLUMNWIDTH_IN, COLUMNWIDTH_IN * 3 / 4)

MJ = 1e6
GIGABIT = 1e9
PETABIT = 1e15


def make_dv_setups():
    """Create the standard DV-QKD hardware configurations used across studies."""
    from qenergy import components as comp

    laser_1550 = comp.LaserNKTkoheras1550()
    laser_780 = comp.LaserMira780Pulsed()
    detector_snspd = comp.DetectorSNSPD1550()
    detector_ingaas = comp.DetectorInGAs1550()

    other_bb84 = [
        comp.MotorizedWavePlate(),
        comp.MotorizedWavePlate(),
        comp.Computer(),
        comp.Computer(),
        comp.SwitchIntensityModulator(),
        comp.TimeTagger(),
    ]
    other_e91 = [
        comp.MotorizedWavePlate(),
        comp.MotorizedWavePlate(),
        comp.Computer(),
        comp.Computer(),
        comp.Oven(),
        comp.TimeTagger(),
        comp.TimeTagger(),
    ]
    other_mdi = [
        comp.MotorizedWavePlate(),
        comp.MotorizedWavePlate(),
        comp.Computer(),
        comp.Computer(),
        comp.SwitchIntensityModulator(),
        comp.TimeTagger(),
    ]

    return {
        "laser_1550": laser_1550,
        "laser_780": laser_780,
        "detector_snspd": detector_snspd,
        "detector_ingaas": detector_ingaas,
        "other_bb84": other_bb84,
        "other_e91": other_e91,
        "other_mdi": other_mdi,
    }


def make_cv_source():
    """Create the standard CV-QKD source component list."""
    from qenergy import components as comp

    return [
        comp.LaserCVPPCL590(),
        comp.MBC(),
        comp.DAC(),
        comp.ThorlabsPowerMeter(),
        comp.Computer(),
    ]


def make_cv_detectors():
    """Create the standard CV-QKD detector configurations."""
    from qenergy import components as comp

    homodyne_1p = [
        "Homodyne 1P",
        comp.ADC(),
        comp.LaserCVPPCL590(),
        comp.Computer(),
        comp.SwitchCVQKD(),
        comp.PolarizationController(),
        comp.ThorlabsPDB(),
    ]
    homodyne_2p = [
        "Homodyne 2P",
        comp.ADC(),
        comp.LaserCVPPCL590(),
        comp.Computer(),
        comp.SwitchCVQKD(),
        comp.PolarizationController(),
        comp.ThorlabsPDB(),
        comp.ThorlabsPDB(),
    ]
    heterodyne_1p = [
        "Heterodyne 1P",
        comp.ADC(),
        comp.LaserCVPPCL590(),
        comp.Computer(),
        comp.SwitchCVQKD(),
        comp.PolarizationController(),
        comp.ThorlabsPDB(),
        comp.ThorlabsPDB(),
    ]
    heterodyne_2p = [
        "Heterodyne 2P",
        comp.ADC(),
        comp.LaserCVPPCL590(),
        comp.Computer(),
        comp.SwitchCVQKD(),
        comp.PolarizationController(),
        comp.ThorlabsPDB(),
        comp.ThorlabsPDB(),
        comp.ThorlabsPDB(),
        comp.ThorlabsPDB(),
    ]

    return {
        "homodyne_1p": homodyne_1p,
        "homodyne_2p": homodyne_2p,
        "heterodyne_1p": heterodyne_1p,
        "heterodyne_2p": heterodyne_2p,
    }
