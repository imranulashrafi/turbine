# run_experiments_greedy.py
import pandas as pd
import os
from run_scheduler import run_scheduler_greedy

# Load alerts
alerts = pd.read_csv("data/alerts.csv")
alerts = alerts[alerts["p_fail_14d"] > 0.0]

# Base configuration
base_config = {
    "time_horizon": 14,   # 2 weeks
    "num_vessels": 5,
    "vessel_capacity": 20,
    "vessel_cost": 2000,
    "downtime_scale": 1000
}

# Scenarios with different crew capacities
scenarios = [
    ("low_crew", 10),
    ("baseline", 15),
    ("high_crew", 25)
]

os.makedirs("results", exist_ok=True)

summary_rows = []

for name, crew_cap in scenarios:
    config = base_config.copy()
    config["crew_capacity"] = crew_cap

    print(f"\nRunning scenario '{name}' with crew_capacity={crew_cap}")
    total_cost, schedule = run_scheduler_greedy(alerts, config)

    schedule_file = f"results/schedule_{name}.csv"
    schedule.to_csv(schedule_file, index=False)
    print(f"✔ Schedule saved: {schedule_file} ({len(schedule)} tasks)")

    summary_rows.append({
        "scenario": name,
        "crew_capacity": crew_cap,
        "total_cost": total_cost,
        "num_tasks": len(schedule)
    })

# Save summary
summary_file = "results/summary.csv"
pd.DataFrame(summary_rows).to_csv(summary_file, index=False)
print(f"✔ Summary saved: {summary_file}")
