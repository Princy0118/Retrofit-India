# pid_sim.py 
# Run: python pid_sim.py  ->  report + pid_response_python.png

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# 1. THE DATA BASE OF VARIABLES AND CONSTANTS
DT, T_END = 0.02, 12.0
V_MAX     = 60.0   # km/h at 100% motor power
TAU       = 0.6    # s, motor lag
TARGET    = 50.0
PEDAL_AT  = 1.0

# 2. THE TWO ALTERNATIVES IN PROCESSING
# FIXED: must discover the right pedal by trial & error (integral wind-up).
FIXED_GAINS = (2.0, 1.5, 0.0)
# ADAPTIVE: knows the physics and its concepts aplication (feedforward) + trims error with switchable PID.
FAST_GAINS   = (2.0, 0.5, 0.6)   # far from target: firm correction
SMOOTH_GAINS = (1.2, 0.8, 0.5)   # near target: gentle correction
SWITCH_GAP   = 15.0

class PID:
    def __init__(self, kp, ki, kd, lo=0.0, hi=100.0):
        self.kp, self.ki, self.kd, self.lo, self.hi = kp, ki, kd, lo, hi
        self.integral, self.prev_error = 0.0, 0.0

    def set_gains(self, kp, ki, kd): self.kp, self.ki, self.kd = kp, ki, kd

    def update(self, e, dt):
        self.integral = max(self.lo, min(self.hi, self.integral + e * dt))
        p, i = self.kp * e, self.ki * self.integral
        d = self.kd * (e - self.prev_error) / dt
        self.prev_error = e
        return max(self.lo, min(self.hi, p + i + d)), p, i, d

@dataclass
class Run:
    name: str; t: np.ndarray; v: np.ndarray
    rise: float; overshoot: float; settle: float; sse: float; wobble: float

def compute_metrics(t, v):
    peak = v.max()
    hit = np.where(v >= 0.9 * TARGET)[0]
    inside = np.abs(v - TARGET) <= 1.0
    settle = np.nan
    if inside[-1]:
        i = len(v) - 1
        while i > 0 and inside[i - 1]: i -= 1
        if t[i] > PEDAL_AT: settle = float(t[i])
    return dict(rise=float(t[hit[0]]) if hit.size else np.nan,
                overshoot=max(0.0, (peak - TARGET) / TARGET * 100),
                settle=settle, sse=float(TARGET - v[-1]),
                wobble=float(np.sum(np.abs(np.diff(v)))))  # km/h of unnecessary speed changes

def simulate(gains, adaptive=False, log=False):
    pid = PID(*gains, lo=(-40 if adaptive else 0), hi=(40 if adaptive else 100))
    n = int(T_END / DT); t = np.arange(n) * DT; v = np.zeros(n); speed = 0.0
    if log:
        print("\nLive math of the FIXED brain (it has to *guess* the pedal):")
        print(f"{'t':>5} {'wish':>5} {'speed':>6} {'gap':>5} | {'P':>6} {'I':>7} {'D':>6} | {'motor%':>6}")
    for k in range(n):
        wish = TARGET if t[k] >= PEDAL_AT else 0.0
        e = wish - speed
        if adaptive:
            # Example of EDGE AI: it knows the car. 50 km/h needs ~83% pedal.
            ff = wish / V_MAX * 100.0
            pid.set_gains(*(FAST_GAINS if abs(e) > SWITCH_GAP else SMOOTH_GAINS))
            corr, p, i, d = pid.update(e, DT)
            u = max(0.0, min(100.0, ff + corr))
        else:
            ff = 0.0
            u, p, i, d = pid.update(e, DT)
        speed += DT * ((u / 100.0 * V_MAX) - speed) / TAU
        v[k] = speed
        if log and 1.0 <= t[k] <= 1.6 and k % 5 == 0:
            print(f"{t[k]:5.2f} {wish:5.1f} {speed:6.1f} {e:5.1f} | {p:6.1f} {i:7.1f} {d:6.1f} | {u:6.1f}")
    return Run("adaptive" if adaptive else "fixed", t, v, **compute_metrics(t, v))

def report(a, b):
    print("\nWHAT ANY PASSENGER FEELS              FIXED PROCESSING   ADAPTIVE PROCESSING")
    print("-" * 68)
    print(f"JumpS past the driver's wish OR domain of control         {a.overshoot:8.1f} %    {b.overshoot:8.1f} %")
    print(f"Time taken until drive feels smooth          {a.settle:8.2f} s    {b.settle:8.2f} s")
    print(f"Unnecessary speed changes (wobble and mechanical jerks)  {a.wobble:8.0f}      {b.wobble:8.0f}")
    print(f"Speed error at the end              {a.sse:8.2f}       {b.sse:8.2f}")

def plot(a, b):
    fig, ax = plt.subplots(figsize=(11.5, 6.8))
    ax.fill_between(a.t, TARGET, a.v, where=a.v > TARGET, color="#d9534f", alpha=0.15,
                    label="energy utillized in the jump")
    ax.fill_between(a.t, a.v, TARGET, where=(a.v < TARGET) & (a.t > 2.5), color="#ff0000",
                    alpha=0.10, label="passengers jerked back while it recovers due to inertia")
    ax.fill_between(a.t, TARGET - 1, TARGET + 1, color="#4ee44e", alpha=0.10)
    ax.text(0.1, TARGET + 1.5, "comfort zone (±1 km/h)", fontsize=9, color="#00ff00")

    ax.plot(a.t, a.v, color="#ff0000", lw=3,
            label=f"Fixed Processing: guesses by trial & error (jump {a.overshoot:.0f}%)")
    ax.plot(b.t, b.v, color="#4ee44e", lw=3,
            label=f"Adaptive Processor: knows the car, trims the error (jump {b.overshoot:.0f}%)")
    ax.axhline(TARGET, color="gray", ls="--", lw=1.8, label="Driver's wish: 50 km/h")
    ax.axvline(PEDAL_AT, color="gray", ls=":", lw=1.2, alpha=0.7)
    ax.text(PEDAL_AT + 0.08, 2, "pedal pressed", color="gray", fontsize=10, rotation=90, va="bottom")

    i_pk = int(np.argmax(a.v))                       # measured peak
    i_tr = i_pk + int(np.argmin(a.v[i_pk:]))         # measured dip after the peak
    ax.annotate("Jumps past the control domain:\nfuel/battery burned for nothing.",
                xy=(a.t[i_pk], a.v[i_pk]), xytext=(4.2, 64.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="#a02020"),
                fontsize=10.5, fontweight="bold", color="#a02020", va="top")
    ax.annotate("Then wastes fuel:\nseasick oscillation for seconds.",
                xy=(a.t[i_tr], a.v[i_tr]), xytext=(6.5, 30),
                arrowprops=dict(arrowstyle="->", lw=2, color="#a02020"),
                fontsize=10.5, fontweight="bold", color="#a02020")
    i_g = int(np.argmax(b.v >= 0.98 * TARGET))
    ax.annotate(f"At the optimal zone in ~{b.t[i_g]:.1f} s.\nNo jump. No wobble. Stays there consistently.",
                xy=(b.t[i_g], b.v[i_g]), xytext=(2.2, 20),
                arrowprops=dict(arrowstyle="->", lw=2, color="#4ee44e"),
                fontsize=10.5, fontweight="bold", color="#4ee44e")

    ax.text(0.985, 0.98,
            "Why green performs better:\nit KNOWS 50 km/h needs ~83% pedal (vehicle model),\nso PID only trims the error.\nRed must discover it by trial & error -> wind-up -> jump.",
            transform=ax.transAxes, ha="right", va="top", fontsize=9.5,
            bbox=dict(boxstyle="round", fc="#fffbe6", ec="#c9b458", alpha=0.95))

    ax.set_xlabel("time (seconds)", fontsize=12)
    ax.set_ylabel("car speed (km/h)", fontsize=12)
    ax.set_title("Same pedal press: guessing (fixed) vs knowing (model-based + adaptive)",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_xlim(0, T_END); ax.set_ylim(0, 68)
    ax.legend(fontsize=9.5, loc="lower right", framealpha=0.95)
    ax.grid(alpha=0.3, ls="--")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout(); plt.savefig("pid_response_python.png", dpi=300); plt.show()
