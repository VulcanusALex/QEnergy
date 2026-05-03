# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Study of the energy efficiency (EE) metric with DV-QKD protocols.
"""

import matplotlib.pyplot as plt
from qenergy.experiments_dv import (
    BB84Experiment,
    EntanglementBasedExperiment,
    MDIQKDExperiment,
)

from studies import FIGSIZE_FULL, EXPORT_DIR, PETABIT, MJ, make_dv_setups

dist = list(range(120))
hw = make_dv_setups()

sourcerate = 80e6
pcoupling = 0.9
mu = 0.1
QBER = 0.01
wavelength = 1550
pbsm = 0.5

# Extra MDI component: 3 computers instead of 2
from qenergy import components as comp

other_mdi_ee = [
    comp.MotorizedWavePlate(),
    comp.MotorizedWavePlate(),
    comp.Computer(),
    comp.Computer(),
    comp.Computer(),
    comp.SwitchIntensityModulator(),
    comp.TimeTagger(),
]

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
    hw["laser_1550"], hw["laser_1550"], hw["detector_snspd"], dist, pbsm, other_mdi_ee,
)

power01 = Experiment01.total_power()
rate01 = Experiment01.compute_secret_key_rate()
power02 = Experiment02.total_power()
rate02 = Experiment02.compute_secret_key_rate()
power03 = Experiment03.total_power()
rate03 = Experiment03.compute_secret_key_rate()

tskr = Experiment01.time_skr(PETABIT)
tskr2 = Experiment02.time_skr(PETABIT)
tskr3 = Experiment03.time_skr(PETABIT)

EnergyBB84 = [Experiment01.total_energy(t) / MJ for t in tskr]
EnergyE91 = [Experiment02.total_energy(t) / MJ for t in tskr2]
EnergyMDI = [Experiment03.total_energy(t) / MJ for t in tskr3]

EEBB84 = [r / power01 for r in rate01]
EEE91 = [r / power02 for r in rate02]
EEMDI = [r / power03 for r in rate03]

fig, ax1 = plt.subplots(1, figsize=FIGSIZE_FULL)
left, bottom, width, height = [0.55, 0.35, 0.38, 0.38]
ax2 = fig.add_axes([left, bottom, width, height])
ax1.plot(dist, EEBB84, label="BB84")
ax1.plot(dist, EEE91, label="E91")
ax1.plot(dist, EEMDI, label="MDI")
ax2.plot(dist, EnergyBB84, label="BB84")
ax2.plot(dist, EnergyE91, label="E91")
ax2.plot(dist, EnergyMDI, label="MDI")

ax1.set(xlabel="Distance [km]", ylabel="Energy efficiency [Rate/Watt]")
ax2.set(xlabel="Distance [km]", ylabel="$E^{\\text{1 Petabit}}$ [MJ]")
ax1.tick_params(axis="both", which="major")

ax1.legend(loc="best")
fig.savefig(EXPORT_DIR / "EE.pdf", format="pdf")
plt.show()
