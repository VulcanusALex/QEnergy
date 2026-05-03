# QEnergy Changelog

## 2026-05-03 — Code Review, Bug Fixes & Three-Round Optimization

Reviewed by Claude Code. 23 files changed, 459 insertions, 924 deletions (net -465 lines).

---

### Round 0: Bug Fixes (6 critical issues)

#### 1. Mutable Default Arguments (9 locations)

All `__init__` methods using `[]` as default parameter were changed to `None` with in-body initialization. This prevents the classic Python mutable-default-sharing bug where all instances share the same list object.

**Files:**
- `qenergy/experiments_cv.py` — `CVExperiment`, `CVQKDProtocol`, `CKAExperiment`, `CKAProtocol`
- `qenergy/experiments_dv.py` — `DVExperiment`, `BB84Experiment`, `EntanglementBasedExperiment`, `MDIQKDExperiment`, `GHZsharing`

**Before:** `def __init__(self, ..., othercomponent=[]):`
**After:** `def __init__(self, ..., othercomponent=None):` + `self.othercomponent = othercomponent if othercomponent is not None else []`

#### 2. `meas_power = None` causes TypeError

`LaserVerdiC532` and `LaserDLC780` set `meas_power = None`, but `Component.total_energy_measured()` checked `if self.meas_power == 0`. Since `None == 0` is `False`, the code would try `time * None` and crash.

**File:** `qenergy/components/base.py`
**Fix:** Changed check to `if not self.meas_power:` which handles both `0` and `None`.

#### 3. `Cryostat.fixed_energy` numerical error

Was `72000` (72 kJ = 24 seconds at 3 kW). Should be 24 hours at 3 kW, matching `DetectorSNSPD` which uses `24 * 60 * 60 * 3000`.

**File:** `qenergy/components/others.py`
**Before:** `fixed_energy = 72000`
**After:** `fixed_energy = 24 * 60 * 60 * 3000`  (259,200,000 J)

#### 4. `all_to_all.py` E91 energy accumulation bug

Two issues: (a) inner `for i` shadowed outer loop variable `i`; (b) `tot` was never reset between parties, causing cumulative energy across all parties.

**File:** `studies/all_to_all.py`
**Before:**
```python
tot = 0
for i in parties:
    n = int(i * (i - 1) / 2)
    for i in range(n):       # shadows outer i
        tot += energy         # never resets
    EnergyE91.append(tot)
```
**After:**
```python
for num_parties in parties:
    num_pairs = num_parties * (num_parties - 1) // 2
    EnergyE91.append(num_pairs * energy_per_pair)
```

#### 5. `Fiber.__init__` crashes on unsupported wavelength

Only 1550, 780, 523 nm were handled. Any other wavelength (e.g. 532 nm from `LaserVerdiC532`) left `_attenuation_fiber_db_km` uninitialized, causing `AttributeError` later.

**File:** `qenergy/components/others.py`
**Fix:** Replaced if/elif chain with dictionary lookup (`ATTENUATION_DB_KM`). Added 532 nm. Raises `ValueError` for unsupported wavelengths. Also initialized `_attenuation_distance` in `__init__` (was never set, causing `AttributeError` on `.attenuation_distance` access).

#### 6. `piecharts.py` typo + show/save order

- Dictionary key `"Time taggecomp.r"` → `"Time tagger"`
- `plt.show()` was called before `fig.savefig()`, which can clear the figure on some backends.

**File:** `studies/piecharts.py`

---

### Round 1: Structural Improvements

#### `Experiment.total_energy()` now delegates to `Component.total_energy()`

Previously inlined `component.power * time + component.fixed_energy`, bypassing any subclass override of `Component.total_energy()`.

**File:** `qenergy/experiments.py`
**Before:** `tot += component.power * time + component.fixed_energy`
**After:** `return sum(c.total_energy(time) for c in self.list_components)`

Same fix applied to `total_energy_measured()`.

#### `power()` renamed to `total_power()`

The method name `power()` shadowed the `Component.power` attribute when accessed on experiment objects. Renamed to `total_power()` for clarity.

**Files:** `qenergy/experiments.py`, `studies/energy_efficiency.py`

#### New `total_fixed_energy()` method

Added to `Experiment` base class for convenience.

#### `Fiber.length` setter: `type()` → `isinstance()`

`type(value) not in [int, float]` rejects `numpy.float64` and other numeric types. Changed to `isinstance(value, (int, float))`.

**File:** `qenergy/components/others.py`

#### `skr_cv.py` cleanup

- Removed duplicate `g = lambda ...` definitions inside `holevo_asymptotic_heterodyne_psk` and `holevo_asymptotic_homodyne_psk`; now uses module-level `G()` consistently.
- Removed dead imports (`# import scipy`, `# from numba import njit`), commented-out `@njit` decorators, and stale commented-out code.
- Fixed typo "Schimdt" → "Schmidt".
- Added missing type annotation on `skr_asymptotic_cka` parameter `T`.

#### `GHZsharing.__init__` defensive copy

`self.list_components = self.othercomponent` was aliasing the input list and mutating it via `.append()`. Changed to `self.list_components = list(self.othercomponent)`.

#### All DV `time_skr()` now filter `R > 0`

`BB84Experiment`, `EntanglementBasedExperiment`, `MDIQKDExperiment`, and `MDIQKDExperiment.raw_time()` now skip zero-rate entries (previously would cause `ZeroDivisionError`). CV experiments already had this.

#### `components/__init__.py` — removed leaky `__all__`

`__all__ = [s for s in dir() if not s.startswith("_")]` exposed imported modules (numpy, math, etc.) as public API. Replaced with explicit imports of `Component`, `PassiveComponent`, `ActiveComponent`.

---

### Round 2: Code Deduplication in `studies/`

#### Shared configuration factory functions

Added to `studies/__init__.py`:
- `make_dv_setups()` — returns dict with `laser_1550`, `laser_780`, `detector_snspd`, `detector_ingaas`, `other_bb84`, `other_e91`, `other_mdi`
- `make_cv_source()` — returns standard CV-QKD source component list
- `make_cv_detectors()` — returns dict with `homodyne_1p/2p`, `heterodyne_1p/2p`

#### Shared constants

`MJ = 1e6`, `GIGABIT = 1e9`, `PETABIT = 1e15` added to `studies/__init__.py`. Replaced all local `gigabit = 1e9` / `1000000` magic numbers across study scripts.

#### Refactored study scripts

6 scripts rewritten to use shared configurations (net -465 lines):
- `qkd_protocols.py`, `measured_values.py`, `energy_efficiency.py` — eliminated triplicated BB84/E91/MDI setup blocks
- `bb84_qber.py` — collapsed 6 manually-written experiments into a loop
- `cv_vs_dv.py` — extracted DSP energy calculation into loop
- `cvqkd.py` — collapsed 4+4 manually-written experiments into loops

#### `dist[:len(energy)]` safety

All plot calls now slice `dist` to match `energy` array length, since `time_skr()` now filters R>0 and may return fewer elements than `dist`.

---

### Round 3: Test Suite & Build

#### New test suite (`tests/`)

3 test modules, 46 test cases, all passing:

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_components.py` | 25 | Component energy, Fiber parameters, laser/detector values, meas_power=None handling |
| `test_experiments.py` | 5 | Experiment energy/power aggregation, empty experiment edge case |
| `test_skr.py` | 16 | G() function, mutual information, all 5 SKR formulae, BB84 end-to-end, mutable-default isolation |

#### Makefile updates

- `make test` — runs `python3 -m unittest discover -s tests -v`
- `make check` — runs tests + syntax check on all .py files

---

### Files Changed (23 total)

| File | Change |
|------|--------|
| `Makefile` | Added `test` and `check` targets |
| `qenergy/components/__init__.py` | Explicit imports instead of leaky `__all__` |
| `qenergy/components/base.py` | `total_energy_measured` handles `None` meas_power |
| `qenergy/components/others.py` | Fiber: dict-based wavelength lookup, 532nm support, `_attenuation_distance` init, `isinstance()` check. Cryostat: fixed `fixed_energy` |
| `qenergy/experiments.py` | Delegate to component methods, rename `power()`→`total_power()`, add `total_fixed_energy()` |
| `qenergy/experiments_cv.py` | Mutable defaults fixed, CKA `time_skr` now filters R>0 |
| `qenergy/experiments_dv.py` | Mutable defaults fixed, all `time_skr`/`raw_time` filter R>0, GHZ defensive copy, docstring fixes |
| `qenergy/skr_cv.py` | Remove duplicate `g` lambda, dead code, type annotation fix |
| `studies/__init__.py` | Shared constants + factory functions for DV/CV hardware |
| `studies/all_to_all.py` | Fixed accumulation bug, use shared constants |
| `studies/bb84_detector.py` | Use shared constants |
| `studies/bb84_qber.py` | Rewritten with loop, use shared configs |
| `studies/bb84_wavelength.py` | Use shared constants |
| `studies/cka.py` | Fixed energy calculation, use shared constants |
| `studies/cka_dist.py` | Use shared constants |
| `studies/cv_vs_dv.py` | Rewritten with shared configs, DSP loop |
| `studies/cvcka.py` | Use shared constants |
| `studies/cvqkd.py` | Rewritten with loops, use shared configs |
| `studies/energy_efficiency.py` | Rewritten with shared configs |
| `studies/measured_values.py` | Rewritten with shared configs |
| `studies/piecharts.py` | Fixed typo + show/save order |
| `studies/qkd_protocols.py` | Rewritten with shared configs |
| `studies/timevspolar.py` | Use shared constants |
| `tests/__init__.py` | New (empty) |
| `tests/test_components.py` | New — 25 tests |
| `tests/test_experiments.py` | New — 5 tests |
| `tests/test_skr.py` | New — 16 tests |
