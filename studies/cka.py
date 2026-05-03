# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
DV CKA study.
"""

import matplotlib.pyplot as plt
from qenergy import components as comp
from qenergy.experiments_dv import (
    GHZsharing,
    BB84Experiment,
    EntanglementBasedExperiment,
)

from studies import FIGSIZE_HALF, EXPORT_DIR, GIGABIT, MJ

dist = 5
pcoupling = 0.9
sourcerate = 100e6
mu = 0.1
QBER = 0
parties = range(2, 11)

## Laser and detectors
wavelength = 1550
laserspdc = comp.LaserMira780Pulsed()
laserBB84 = comp.LaserNKTkoheras1550()
detector = comp.DetectorSNSPD1550()
pbsm = 0.5

# Experiment instances
GHZexperiments = []
for i in parties:
    GHZexperiments.append(
        GHZsharing(
            sourcerate,
            pcoupling,
            mu,
            wavelength,
            QBER,
            laserspdc,
            i,
            detector,
            dist,
            othercomponent=None,
        )
    )

otherBB84 = [
    comp.MotorizedWavePlate(),
    comp.MotorizedWavePlate(),
    comp.Computer(),
    comp.Computer(),
    comp.SwitchIntensityModulator(),
    comp.TimeTagger(),
]
BB84Experiment = BB84Experiment(
    sourcerate, pcoupling, mu, wavelength, QBER, laserBB84, detector, [dist], otherBB84
)

othercomponentE91 = [
    comp.MotorizedWavePlate(),
    comp.MotorizedWavePlate(),
    comp.Computer(),
    comp.Computer(),
    comp.Oven(),
    comp.TimeTagger(),
    comp.TimeTagger(),
]
E91experiment = EntanglementBasedExperiment(
    sourcerate,
    pcoupling,
    mu,
    wavelength,
    QBER,
    laserspdc,
    detector,
    detector,
    [dist],
    othercomponentE91,
)

tGHZ = [exp.raw_time_ghz(GIGABIT) for exp in GHZexperiments]

tE91 = E91experiment.time_skr(GIGABIT)[0]
tBB84 = BB84Experiment.time_skr(GIGABIT)[0]

EnergyGHZ = [exp.total_energy(t) / MJ for exp, t in zip(GHZexperiments, tGHZ)]

e91_per_link = E91experiment.total_energy(tE91) / MJ
bb84_per_link = BB84Experiment.total_energy(tBB84) / MJ
EnergyE91 = [(i - 1) * e91_per_link for i in parties]
EnergyBB84 = [(i - 1) * bb84_per_link for i in parties]

N = 4
fig, ax = plt.subplots(1, figsize=FIGSIZE_HALF)
plt.plot(
    parties, EnergyBB84, label="BB84-CKA ", linestyle="-", marker="P", markersize=N
)
plt.plot(parties, EnergyE91, label="Bell-CKA ", linestyle="-", marker="o", markersize=N)
plt.plot(parties, EnergyGHZ, label="GHZ-CKA", linestyle="-", marker="D", markersize=N)

plt.xticks(parties)

plt.yscale("log")
ax.set(xlabel="Number of parties", ylabel="Energy consumption [MJ]")
ax.tick_params(axis="both", which="major")
ax.legend(loc="upper left")
ax.set_title("$N_{\\rm target} = 1$ GBit")
plt.savefig(EXPORT_DIR / "CKAstudy.pdf", format="pdf")

plt.show()
