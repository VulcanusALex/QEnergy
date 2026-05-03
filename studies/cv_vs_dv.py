# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Study to compare the energetic cost of DV protocols with CV ones.
"""

import numpy as np
import matplotlib.pyplot as plt
from qenergy.experiments_cv import CVQKDProtocol
from qenergy.experiments_dv import BB84Experiment

from studies import (
    FIGSIZE_FULL, EXPORT_DIR, GIGABIT, MJ,
    make_dv_setups, make_cv_source, make_cv_detectors,
)

dist = list(range(200))
hw = make_dv_setups()

sourcerate = 80e6
pcoupling = 0.9
mu = 0.1
wavelength = 1550
cvqkd_rate = 100e6

# CV parameters
eta = 0.7
Vel = 0.005
beta = 0.95
xi = 0.005
source = make_cv_source()
cv_det = make_cv_detectors()

# DV experiments
ExperimentBB84SNSPD = BB84Experiment(
    sourcerate, pcoupling, mu, wavelength, 0.01,
    hw["laser_1550"], hw["detector_snspd"], dist, hw["other_bb84"],
)
ExperimentBB84APD = BB84Experiment(
    sourcerate, pcoupling, mu, wavelength, 0.01,
    hw["laser_1550"], hw["detector_ingaas"], dist, hw["other_bb84"],
)

tskr = ExperimentBB84SNSPD.time_skr(GIGABIT)
tskr2 = ExperimentBB84APD.time_skr(GIGABIT)
Energysnspd = [ExperimentBB84SNSPD.total_energy(t) / MJ for t in tskr]
Energyingaas = [ExperimentBB84APD.total_energy(t) / MJ for t in tskr2]

# CV experiment: Gaussian Het 2P
Experiment_GM_Ht2P = CVQKDProtocol(
    eta, Vel, beta, cvqkd_rate, source, cv_det["heterodyne_2p"], xi, dist, "Gauss"
)
tsk_GM_Ht2P = Experiment_GM_Ht2P.time_skr(GIGABIT)
Energy_GM_Ht2P = [Experiment_GM_Ht2P.total_energy(t) / MJ for t in tsk_GM_Ht2P]

# DSP energy contributions
skrCV = Experiment_GM_Ht2P.compute_secret_key_rate()
dsp_taus = [0.006, 0.018, 0.0003]
dsp_labels = ["$\\tau_{DSP}=0.006$", "$\\tau_{DSP}=0.018$", "$\\tau_{DSP}=0.0003$"]
dsp_styles = ["--", "-.", ":"]

Energy_with_DSP = {}
for tau in dsp_taus:
    Edsp = [tau * GIGABIT / r * cvqkd_rate / MJ for r in skrCV]
    Energy_with_DSP[tau] = [e + d for e, d in zip(Energy_GM_Ht2P, Edsp)]

fig, ax = plt.subplots(1, figsize=FIGSIZE_FULL)
ax.plot(dist[:len(Energysnspd)], Energysnspd, color="tab:blue", ls="--", label="BB84 with SNSPDs")
ax.plot(dist[:len(Energyingaas)], Energyingaas, color="tab:blue", label="BB84 with APDs")
ax.plot(dist[:len(Energy_GM_Ht2P)], Energy_GM_Ht2P, color="tab:orange", label="CV-QKD $\\tau_{DSP}=0$")

for tau, label, ls in zip(dsp_taus, dsp_labels, dsp_styles):
    e = Energy_with_DSP[tau]
    ax.plot(dist[:len(e)], e, color="tab:orange", ls=ls, label=f"CV-QKD {label}")

ax.set(xlabel="Distance [km]", ylabel="Energy consumption [MJ]")
ax.tick_params(axis="both", which="major")
ax.legend(loc="upper left", ncols=2)
ax.set_xlim(left=0, right=200)
ax.set_title("$N_{\\rm target} = 1$ GBit")
ax.set_yscale("log")
ax.set_ylim(top=1e6)

fig.savefig(EXPORT_DIR / "CVVSDVstudy.pdf", format="pdf")
plt.show()
