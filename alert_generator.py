# generate_alerts.py
import pandas as pd
import random
import os

# -----------------------------
# Configuration
# -----------------------------
NUM_ALERTS = 3000  # number of alerts to generate
COMPONENTS = ["gearbox", "generator", "blade"]
MAX_RUL = 60  # max remaining useful life in days

# -----------------------------
# Linear P-F curve function
# -----------------------------
def ramp_probability(rul, horizon=MAX_RUL):
    """
    Calculates failure probability based on remaining useful life (RUL).
    Linear P-F curve: probability increases as RUL decreases.
    """
    return max(0.0, 1.0 - rul / horizon)

# -----------------------------
# Generate alerts
# -----------------------------
rows = []
for i in range(NUM_ALERTS):
    turbine_id = f"T{i+1:04d}"
    component = random.choice(COMPONENTS)
    rul = random.randint(5, MAX_RUL)
    rows.append({
        "turbine_id": turbine_id,
        "component": component,
        "RUL_days": rul,
        "p_fail_14d": round(ramp_probability(rul), 2)
    })

# -----------------------------
# Save to CSV
# -----------------------------
os.makedirs("data", exist_ok=True)
df = pd.DataFrame(rows)
df.to_csv("data/alerts.csv", index=False)

print(f"✔ {NUM_ALERTS} alerts written to data/alerts.csv")
