# traffic_fuel_waste.py
import matplotlib.pyplot as plt

# ---- CITY TRAFFIC DATA (averages from published traffic studies) ----
# NOTE: constants are model assumptions.
CITIES = ["Delhi\n(high frequency + sensitive stop-go)", "Mumbai\n(potholes as jerks and fuel wasters)", "Bangalore\n(very long traffic jams)"]
DATA = {
 "Delhi":     dict(commute_h=2.0, stops_h=55, potholes_h=8,  idle_frac=0.35),
 "Mumbai":    dict(commute_h=1.8, stops_h=40, potholes_h=25, idle_frac=0.30),
 "Bangalore": dict(commute_h=2.2, stops_h=45, potholes_h=12, idle_frac=0.45),
}
IDLE_LPH = 0.6    # litres burned per hour of idling (engine on, car not moving)
STOP_L   = 0.008  # extra litres per stop-start (brake, then re-accelerate)
POTH_L   = 0.012  # litres per pothole/construction dodge (slow down then accelerating positively again)

wastage = {}
for c, d in DATA.items():
    idle_h = d["commute_h"] * d["idle_frac"]
    wastage[c] = (idle_h * IDLE_LPH,                        # idling waste
                d["commute_h"] * d["stops_h"] * STOP_L,     # red light wastage
                d["commute_h"] * d["potholes_h"] * POTH_L)  # pothole-acceleration and retardation waste

print("PETROL WASTED PER CAR PER DAY (litres)")
for c, (i, s, p) in wastage.items():
    print(f"{c.replace(chr(10),' ')}: idling={i:.2f}  stop-go={s:.2f}  potholes={p:.2f}  TOTAL={i+s+p:.2f}")

# ---- GRAPH (scaled per 1000 cars) ----
idle  = [wastage[c][0]*1000 for c in DATA]
stops = [wastage[c][1]*1000 for c in DATA]
poth  = [wastage[c][2]*1000 for c in DATA]

fig, ax = plt.subplots(figsize=(10, 7))
x = range(len(CITIES))
ax.bar(x, idle, label="1. Engine idling in jams (car stopped, petrol burning)")
ax.bar(x, stops, bottom=idle, label="2. Stop-start cycles (brake, then accelerate again)")
ax.bar(x, poth, bottom=[i+s for i, s in zip(idle, stops)], label="3. Pothole/construction dodging (slow down + speed up)")

for g in range(len(CITIES)):
    total = idle[g] + stops[g] + poth[g]
    ax.text(g, total + 25, f"{total:.0f} L/day", ha="center", fontsize=13, fontweight="bold")
ax.set_ylabel("Litres of petrol *WASTED* per day by 1000 cars", fontsize=12)
ax.set_title("Analysis of petrol wastage in 3 metropolitan cities of India per 1000 cars", fontsize=14)
ax.set_xticks(list(x)); ax.set_xticklabels(CITIES, fontsize=11)
ax.legend(fontsize=10, loc="lower right")
ax.grid(axis="y", alpha=0.3)
fig.text(0.5, 0.001, "Simulation graphed analysis based on published traffic averages (illustrative)",
         ha="center", fontsize=9, style="italic")
plt.tight_layout(); plt.savefig("traffic_fuel_waste.png", dpi=200); plt.show()
