# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Study comparing datasheet vs measured energy consumption for BB84, E91 and MDI-QKD.
"""

import matplotlib.pyplot as plt
from qenergy.experiments_dv import (
    BB84Experiment,
    EntanglementBasedExperiment,
    MDIQKDExperiment,
)

from studies import FIGSIZE_HALF, EXPORT_DIR, GIGABIT, MJ, make_dv_setups

dist = list(range(120))
hw = make_dv_setups()

sourcerate = 80e6
pcoupling = 0.9
mu = 0.1
QBER = 0.01
wavelength = 1550
pbsm = 0.5

Experiment01 = BB84Experiment(
    sourcerate, pcoupling, mu, wavelength, QBER,
    hw["laser_1550"], hw["detector_snspd"], dist, hw["other_bb84"],
)
Experiment02 = EntanglementBasedExperiment(
    sourcerate, pcoupling, mu, wavelength, QBER,
    hw["laser_780"], hw["detector_snspd"], hw["detector_snspd"], dist, hw["other_e91"],
)
Experiment03 = MDIQKDExperiment(
    sourcerate, pcoupling, mu, wavelength, QBER,
    hw["laser_1550"], hw["laser_1550"], hw["detector_snspd"], dist, pbsm, hw["other_mdi"],
)

tskr = Experiment01.time_skr(GIGABIT)
tskr2 = Experiment02.time_skr(GIGABIT)
tskr3 = Experiment03.time_skr(GIGABIT)

EnergyBB84 = [Experiment01.total_energy(t) / MJ for t in tskr]
EnergyE91 = [Experiment02.total_energy(t) / MJ for t in tskr2]
EnergyMDI = [Experiment03.total_energy(t) / MJ for t in tskr3]

EnergyBB84meas = [Experiment01.total_energy_measured(t) / MJ for t in tskr]
EnergyE91meas = [Experiment02.total_energy_measured(t) / MJ for t in tskr2]
EnergyMDImeas = [Experiment03.total_energy_measured(t) / MJ for t in tskr3]

fig, ax = plt.subplots(1, figsize=FIGSIZE_HALF)
ax.plot(dist, EnergyBB84, label="BB84", color="red")
ax.plot(dist, EnergyBB84meas, label="BB84 measured", linestyle="--", color="red")
ax.plot(dist, EnergyE91, label="E91", color="blue")
ax.plot(dist, EnergyE91meas, label="E91 measured", linestyle="--", color="blue")
ax.plot(dist, EnergyMDI, label="MDI", color="green")
ax.plot(dist, EnergyMDImeas, label="MDI measured", linestyle="--", color="green")

ax.set(xlabel="Distance [km]", ylabel="Energy consumption [MJ]")
ax.tick_params(axis="both", which="major")
ax.set_title("$N_{\\rm target} = 1$ GBit")
ax.legend(loc="upper left")
fig.savefig(EXPORT_DIR / "MeasuredValues.pdf", format="pdf")
plt.show()
