# analyze_schedules.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -----------------------------
# Configuration
# -----------------------------
scenarios = ["low_crew", "baseline", "high_crew"]
results_folder = "results"
plots_folder = os.path.join(results_folder, "plots")
os.makedirs(plots_folder, exist_ok=True)

vessel_capacity = 20
crew_capacity_dict = {"low_crew": 10, "baseline": 15, "high_crew": 25}
component_crew = {"gearbox": 3, "generator": 2, "blade": 2}
component_duration = {"gearbox": 12, "generator": 8, "blade": 6}

summary_rows = []

# -----------------------------
# Loop through scenarios
# -----------------------------
for scenario in scenarios:
    schedule_file = f"{results_folder}/schedule_{scenario}.csv"
    schedule = pd.read_csv(schedule_file)

    if schedule.empty:
        print(f"⚠ Scenario {scenario} has no scheduled tasks!")
        continue

    # Metrics
    num_tasks = len(schedule)
    total_downtime = schedule['downtime_cost'].sum()
    avg_urgency = schedule['urgency'].mean()
    tasks_per_component = schedule['component'].value_counts()

    # Time horizon and number of vessels
    time_horizon = schedule['time'].max() + 1
    num_vessels = schedule['vessel'].max() + 1

    # Vessel utilization per time slot
    vessel_util = np.zeros((time_horizon, num_vessels))
    for _, row in schedule.iterrows():
        t = int(row['time'])
        v = int(row['vessel'])
        duration = component_duration[row['component']]
        vessel_util[t, v] += duration

    vessel_util_percent = vessel_util.sum(axis=1) / (num_vessels * vessel_capacity) * 100

    # Crew utilization per time slot
    crew_util = np.zeros(time_horizon)
    for _, row in schedule.iterrows():
        t = int(row['time'])
        crew_util[t] += component_crew[row['component']]
    crew_util_percent = crew_util / crew_capacity_dict[scenario] * 100

    # -----------------------------
    # Save metrics summary
    # -----------------------------
    summary_rows.append({
        "scenario": scenario,
        "num_tasks": num_tasks,
        "total_downtime_cost": total_downtime,
        "avg_urgency": avg_urgency
    })

    # -----------------------------
    # Generate plots
    # -----------------------------

    # Vessel utilization plot
    plt.figure(figsize=(10,4))
    plt.plot(range(time_horizon), vessel_util_percent, marker='o')
    plt.xlabel("Time slot")
    plt.ylabel("Vessel utilization (%)")
    plt.title(f"Vessel Utilization Over Time ({scenario})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/vessel_util_{scenario}.png")
    plt.close()

    # Crew utilization plot
    plt.figure(figsize=(10,4))
    plt.plot(range(time_horizon), crew_util_percent, marker='o', color='orange')
    plt.xlabel("Time slot")
    plt.ylabel("Crew utilization (%)")
    plt.title(f"Crew Utilization Over Time ({scenario})")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/crew_util_{scenario}.png")
    plt.close()

    # Task urgency scatter plot
    plt.figure(figsize=(10,4))
    plt.scatter(schedule['time'], schedule['urgency'], c=schedule['urgency'], cmap='Reds', alpha=0.7)
    plt.colorbar(label='Urgency')
    plt.xlabel("Time slot")
    plt.ylabel("Task urgency")
    plt.title(f"Task Urgency Over Time ({scenario})")
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/urgency_{scenario}.png")
    plt.close()

    # Component distribution plot
    plt.figure(figsize=(6,4))
    sns.countplot(x='component', data=schedule)
    plt.title(f"Tasks per Component ({scenario})")
    plt.ylabel("Number of tasks")
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/component_dist_{scenario}.png")
    plt.close()

# -----------------------------
# Save summary CSV
# -----------------------------
summary_df = pd.DataFrame(summary_rows)
summary_file = f"{results_folder}/metrics_summary.csv"
summary_df.to_csv(summary_file, index=False)
print(f"✔ Metrics summary saved: {summary_file}")
print(f"✔ All plots saved in: {plots_folder}")
