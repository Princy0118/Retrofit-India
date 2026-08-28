#battery wasted with respect to money wasted per 1000 cars per city
import matplotlib.pyplot as plt
import numpy as np

CITIES = ["Delhi\n(high frquency high sensitivity)", "Mumbai\n(Potholes & mechanical jerks)", "Bangalore\n(very exhaustive traffic Jams)"]
DATA = {"Delhi":     dict(commute_h=2.0, stops_h=55, potholes_h=8,  idle_frac=0.35, avg_kmh=22),
        "Mumbai":    dict(commute_h=1.8, stops_h=40, potholes_h=25, idle_frac=0.30, avg_kmh=19),
        "Bangalore": dict(commute_h=2.2, stops_h=45, potholes_h=12, idle_frac=0.45, avg_kmh=16),}

# Constants
PETROL_PRICE = 110  # ₹ per Liter average of all three cities as of 26/08/2026
EVB_PRICE    = 15  # ₹ per kWh (Commercial/Public charging rate in India)
BASE_WH_KM    = 110 # Wh/km to move car
AUX_W         = 800 # Watts for AC/Electronic requirements while car = idling
STOP_WH       = 6   # Watt hour lost per stop (Normal EV regenerative braking is only 65% efficient) as per average of open sourced web available information
POTH_WH       = 6   # Watt hour lost per pothole dodge - especially core to mumbai

petrol_waste_rs = []
normal_ev_waste_rs = []
ai_ev_waste_rs = []

# --- 2. CALCULATING BATTERY WASTAGE AT EACH CITY ---
for c, d in DATA.items():
    # A. PETROL WASTE (Liters to Rupees)
    idle_h = d["commute_h"] * d["idle_frac"]
    p_idle = idle_h * 0.6                                         # 600 mL/hr idling
    p_stop = d["commute_h"] * d["stops_h"] * 0.008                # 8 mL per stop
    p_poth = d["commute_h"] * d["potholes_h"] * 0.012             # 12 mL per pothole
    petrol_rs = (p_idle + p_stop + p_poth) * PETROL_PRICE * 1000  # Scaling to 1000 cars
    petrol_waste_rs.append(petrol_rs)                             # Averages according to information available on web

    # B. ELECTRIC BATTERY WASTE (kWh to Rupees)
    # EVs waste energy on inefficient regenerative braking, pothole dodging at non-ideal urban roads, and working electric motor with working AC
    ev_regen_loss = d["commute_h"] * d["stops_h"] * STOP_WH       # Wh
    ev_poth_loss  = d["commute_h"] * d["potholes_h"] * POTH_WH    # Wh
    ev_aux_loss   = idle_h * AUX_W                                # Wh (AC running in jams, and electric motor still on)
    ev_total_wh   = ev_regen_loss + ev_poth_loss + ev_aux_loss
    normal_rs = (ev_total_wh / 1000) * EVB_PRICE * 1000          # Scaling to 1000 cars
    normal_ev_waste_rs.append(normal_rs)

    # C. AI *optimized* RETROFITTED EV WASTE (Theoretical Application of AI Optimized torque delivery with driver and road: sensing + labelling + adaptation)
    # AI powered Microcontroller smooths braking (regen efficiency 65% becomes 90% which is = 70% reduction in loss)
    # AI mechanism predicts potholes and adjusts torque appropriately (60% reduction in loss)
    # Theoretical application of AI, optimizes thermal cabin management (40% reduction in standing AC drain)
    ai_regen_loss = ev_regen_loss * 0.30
    ai_poth_loss  = ev_poth_loss * 0.40
    ai_aux_loss   = ev_aux_loss * 0.60
    ai_total_wh   = ai_regen_loss + ai_poth_loss + ai_aux_loss
    ai_rs = (ai_total_wh / 1000) * EVB_PRICE * 1000              # Scaled to 1000 cars
    ai_ev_waste_rs.append(ai_rs)

# --- 3. PLOTTING THE GROUPED BAR CHART ---
fig, ax = plt.subplots(figsize=(12, 7))
x = np.arange(len(CITIES))
width = 0.25
bars1 = ax.bar(x - width, petrol_waste_rs, width, label='Petrol Car (Fixed Engine)', color='#ff0000', edgecolor='black')
bars2 = ax.bar(x, normal_ev_waste_rs, width, label='Normal EV (Fixed Control)', color='#00ff00', edgecolor='black')
bars3 = ax.bar(x + width, ai_ev_waste_rs, width, label='AI powered Retrofit EV (Adaptive Torque)', color='#00ffff', edgecolor='black', linewidth=2)

for i in range(len(CITIES)):
    normal_val = normal_ev_waste_rs[i]
    ai_val = ai_ev_waste_rs[i]
    saved = normal_val - ai_val
    pct = (saved / normal_val) * 100

    ax.annotate(f"AI SAVES\n₹{saved/1000:.0f}k\n({pct:.0f}%)",
                xy=(x[i], normal_val), xycoords='data',
                xytext=(x[i] + width, ai_val + 15000), textcoords='data',
                arrowprops=dict(facecolor='#333', shrink=0.05, width=2, headwidth=8),   # Arrow
                fontsize=11, fontweight='bold', color='#006400',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#2ECC71", lw=2))

# --- 4. FORMATTING FOR MAXIMUM IMPACT ---
ax.set_ylabel("Rupees (₹) Wasted Per Day (per 1000 cars)", fontsize=13, fontweight='bold')
ax.set_title("The Hidden Cost of Indian Traffic:\nWhy Normal EVs and Petrol Cars Bleed Money, and How Retrofitted Adaptive AI based (Petrol Car) EV Fixes It",
             fontsize=16, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(CITIES, fontsize=13)
ax.set_ylim(0, max(normal_ev_waste_rs) * 1.25)
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: f"₹{val/1000:.0f}k"))
ax.legend(fontsize=12, loc='lower right', framealpha=0.9)
fig.text(0.5, 0.01,"Normal EVs waste massive energy on inefficient regenerative braking and standing AC, and obviously so do Petrol Cars. This theory of AI controlled retrofitted petrol Cars, recovers up to 70% of that lost gap.", ha="center", fontsize=11, style="italic", color="#555")

plt.tight_layout()
plt.subplots_adjust(bottom=0.12)
plt.savefig("ai_ev_savings_comparison.png", dpi=300)
plt.show()

print("Graph saved as 'ai_retro_ev_savings_comparison.png'")
