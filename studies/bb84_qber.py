# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Study of the influence of QBER on the energetic consumption of BB84.
"""

import matplotlib.pyplot as plt
from qenergy.experiments_dv import BB84Experiment

from studies import FIGSIZE_HALF, EXPORT_DIR, GIGABIT, MJ, make_dv_setups

dist = list(range(100))
hw = make_dv_setups()

sourcerate = 80e6
pcoupling = 0.9
mu = 0.1
wavelength = 1550

qber_values = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10]
labels = ["1\\%", "2\\%", "4\\%", "6\\%", "8\\%", "10\\%"]

fig, ax = plt.subplots(1, figsize=FIGSIZE_HALF)

for qber, label in zip(qber_values, labels):
    exp = BB84Experiment(
        sourcerate, pcoupling, mu, wavelength, qber,
        hw["laser_1550"], hw["detector_snspd"], dist, hw["other_bb84"],
    )
    tskr = exp.time_skr(GIGABIT)
    energy = [exp.total_energy(t) / MJ for t in tskr]
    ax.plot(dist[:len(energy)], energy, label=label)

ax.set(xlabel="Distance [km]", ylabel="Energy consumption [MJ]")
ax.tick_params(axis="both", which="major")
ax.legend(loc="upper left", title="QBER", ncols=2)
ax.set_title("$N_{\\rm target} = 1$ GBit")

fig.savefig(EXPORT_DIR / "BB84QBERstudy.pdf", format="pdf")
plt.show()
