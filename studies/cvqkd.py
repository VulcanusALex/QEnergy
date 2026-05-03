# Copyright (c) 2024 Raja Yehia, Yoann Piétri, Carlos Pascual García, Pascal Lefebvre, Federico Centrone
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Study of the energetic consumption of the CV-QKD protocol:
Gaussian modulation, PSK modulation, and nCV-QKD for CKA.
"""

import matplotlib.pyplot as plt
from qenergy.experiments_cv import CVQKDProtocol

from studies import FIGSIZE_HALF, EXPORT_DIR, GIGABIT, MJ, make_cv_source, make_cv_detectors

# Parameters of the plot
dist_PSK = [d / 100 for d in range(850)]
dist_GM = [d / 10 for d in range(2000)]
dist_nCV = [d / 10 for d in range(1500)]

# Parameters of the implementation
eta = 0.7
Vel = 0.005
beta_PSK = 0.95
beta_GM = 0.95
sourcerate = 1e8
xi = 0.005

source = make_cv_source()
cv_det = make_cv_detectors()

detector_configs = [
    ("Hom, 1P", cv_det["homodyne_1p"]),
    ("Hom, 2P", cv_det["homodyne_2p"]),
    ("Het, 1P", cv_det["heterodyne_1p"]),
    ("Het, 2P", cv_det["heterodyne_2p"]),
]

# PSK experiments
fig, ax = plt.subplots(1, figsize=FIGSIZE_HALF)
for label, det in detector_configs:
    exp = CVQKDProtocol(eta, Vel, beta_PSK, sourcerate, source, det, xi, dist_PSK, "PSK")
    tsk = exp.time_skr(GIGABIT)
    energy = [exp.total_energy(t) / MJ for t in tsk]
    ax.plot(dist_PSK[:len(energy)], energy, label=label)

ax.set(xlabel="Distance [km]", ylabel="Energy consumption [MJ]")
ax.tick_params(axis="both", which="major")
ax.legend(loc="upper left")
ax.set_title("$N_{\\rm target} = 1$ GBit")
plt.ylim(0, 30)
plt.savefig(EXPORT_DIR / "PSKstudy.pdf", format="pdf")
plt.show()


# GM experiments
fig, ax = plt.subplots(1, figsize=FIGSIZE_HALF)
for label, det in detector_configs:
    exp = CVQKDProtocol(eta, Vel, beta_GM, sourcerate, source, det, xi, dist_GM, "Gauss")
    tsk = exp.time_skr(GIGABIT)
    energy = [exp.total_energy(t) / MJ for t in tsk]
    ax.plot(dist_GM[:len(energy)], energy, label=label)

ax.set(xlabel="Distance [km]", ylabel="Energy consumption [MJ]")
ax.tick_params(axis="both", which="major")
ax.legend(loc="upper left")
ax.set_title("$N_{\\rm target} = 1$ GBit")
plt.ylim(0, 60)
fig.savefig(EXPORT_DIR / "GMstudy.pdf", format="pdf")
plt.show()


# nCV-QKD protocol
Nusers = list(range(3, 7))

fig, ax = plt.subplots(1, figsize=FIGSIZE_HALF)
for N in Nusers:
    exp = CVQKDProtocol(
        eta, Vel, beta_GM, sourcerate, source, cv_det["homodyne_2p"], xi, dist_nCV, "Gauss"
    )
    tsk = exp.time_skr(GIGABIT)
    energy = [exp.total_energy(t) * (N - 1) / MJ for t in tsk]
    plt.plot(dist_nCV[:len(energy)], energy, label=f"{N} users")

ax.set(xlabel="Distance [km]", ylabel="Energy consumption [MJ]")
ax.tick_params(axis="both", which="major")
ax.legend(loc="upper left")
ax.set_title(r"$N_{{\mathrm{{target}}}}$ = {0} GBit".format(int(GIGABIT / 1e9)))
plt.ylim(0, 20)
fig.savefig(EXPORT_DIR / "nCV.pdf", format="pdf")
plt.show()
