# comparison_parametric.py
import matplotlib.pyplot as plt
import numpy as np

# --- 1. SYSTEMS & SCORE CALCULATION ---
class System:
    def __init__(self, name, color, overshoot_pct, waste_rs_day, co2_kg_day, cost_5yr_lakh):
        self.name = name; self.color = color
        self.overshoot_pct = overshoot_pct; self.waste_rs_day = waste_rs_day
        self.co2_kg_day = co2_kg_day; self.cost_5yr_lakh = cost_5yr_lakh

def cl(v): return max(0.0, min(100.0, v))

systems = [
    System("Petrol car (today)",    "#ff0000", 10, 150000, 6200, 6.0),
    System("Normal EV (fixed PID)", "#31f5ff", 15,  10600, 3100, 15.0),
    System("AI-optimized retrofitted EV","#39ff14",  4,   6300, 2700, 2.0),
]
param_s = ["Torque delivery", "Less wastage", "Eco-friendliness", "Affordability"]

scores = []
for s in systems:
    scores.append([
        cl(100 - s.overshoot_pct * 5),
        cl(100 - s.waste_rs_day / 1600.0),
        cl(100 - s.co2_kg_day / 70.0),
        cl(100 - s.cost_5yr_lakh * 6.0)
    ])

print(f"{'SYSTEM':<26}", end="")
for p in param_s: print(f"{p:<18}", end="")
print("\n" + "-"*98)
for i, s in enumerate(systems):
    print(f"{s.name:<26}", end="")
    for j in range(4): print(f"{int(scores[i][j]):<18}", end="")
    print()

# --- 2. COVERAGE AREA METRICS ---
def radar_area(vals):
    n = len(vals)
    return 0.5 * np.sin(2*np.pi/n) * sum(vals[j]*vals[(j+1) % n] for j in range(n))

ideal_area = radar_area([100]*len(param_s))
coverage = [radar_area(sc)/ideal_area*100 for sc in scores]
print("\nOVERALL PERFORMANCE COVERAGE (% of a perfect 100/100/100/100 technology):")
for s, c in zip(systems, coverage):
    print(f"  {s.name:<26}: {c:5.1f}%")

angles = np.linspace(0, 2*np.pi, len(params), endpoint=False).tolist()
angles += angles[:1]

fig = plt.figure(figsize=(16, 9.5))
ax1 = fig.add_axes([0.08, 0.27, 0.36, 0.58], polar=True)
ax2 = fig.add_axes([0.72, 0.30, 0.25, 0.55])   

ax1.set_theta_offset(np.pi/2)
ax1.set_theta_direction(-1)

ax1.plot(angles, [100]*(len(param_s)+1), color='gray', linestyle='--',
         linewidth=1.5, label='Optimized technology (theoretical)')

ang_off = [-0.18, 0.0, 0.18]
for i, s in enumerate(systems):
    vals = scores[i] + scores[i][:1]
    ax1.plot(angles, vals, color=s.color, linewidth=3, label=s.name)
    ax1.fill(angles, vals, color=s.color, alpha=0.18)
    for j in range(len(param_s)):
        ax1.text(angles[j] + ang_off[i], scores[i][j] + 6, str(int(scores[i][j])),
                 ha='center', va='center', fontsize=10, fontweight='bold', color=s.color,
                 bbox=dict(boxstyle='round,pad=0.18', fc='white', ec=s.color, alpha=0.9))

ax1.set_xticks(angles[:-1])
ax1.set_xticklabels(["Torque delivery", "", "Eco-friendliness", "Affordability"],
                    fontsize=12, fontweight='bold')
ax1.text(angles[1], 116, "Less wastage", ha='left', va='center',
         fontsize=12, fontweight='bold', clip_on=False)

ax1.tick_params(axis='x', pad=22)
ax1.set_ylim(0, 110)
ax1.set_yticks([25, 50, 75, 100])
ax1.set_yticklabels([])
ax1.set_title("Graphical representation of Performance", fontsize=18, fontweight='bold', pad=52)

# Right panel — FIX: short y-labels (full names stay in the legend)
y = np.arange(len(systems))
bars = ax2.barh(y, coverage, color=[s.color for s in systems], edgecolor='black', linewidth=1.2)
for bar, c in zip(bars, coverage):
    ax2.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
             f"{c:.0f}%", va='center', fontsize=13, fontweight='bold')
ax2.set_yticks(y)
ax2.set_yticklabels(["Petrol", "Normal EV", "AI retro EV"], fontsize=12)
ax2.set_xlim(0, 100)
ax2.set_xlabel("Overall coverage of the ideal technologys solution (%)", fontsize=12, fontweight='bold')
ax2.set_title("One-number summary", fontsize=18, fontweight='bold', pad=15)
ax2.grid(axis='x', linestyle='--', alpha=0.5)
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

fig.suptitle("Which solution must win for India?", fontsize=24, fontweight='bold', y=0.98)
fig.text(0.26, 0.205, "Grey rings (inner → outer) = score 25 · 50 · 75 · 100",
         ha='center', fontsize=10, style='italic', color='gray')
# --- LEGEND ---
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc='lower left', bbox_to_anchor=(0.04, 0.02),
           ncol=2, fontsize=11, framealpha=0.95,
           title="Technologies compared (dashed = theoretical ideal)")

plt.savefig("comparison_radar.png", dpi=300, bbox_inches='tight')
plt.show()
