# run_scheduler_greedy.py
import pandas as pd
from component_rules import COMPONENT_RULES
import numpy as np

def run_scheduler_greedy(alerts, config):
    """
    Greedy heuristic scheduler:
    - Sort tasks by urgency descending
    - Assign earliest feasible time and vessel
    - Respect crew and vessel capacity
    """
    if alerts.empty:
        return 0.0, pd.DataFrame()

    # Sort tasks by urgency
    alerts = alerts.sort_values("p_fail_14d", ascending=False).reset_index(drop=True)

    time_horizon = config["time_horizon"]
    num_vessels = config["num_vessels"]
    vessel_capacity = config["vessel_capacity"]
    crew_capacity = config["crew_capacity"]
    vessel_cost = config["vessel_cost"]
    downtime_scale = config["downtime_scale"]

    # Track available crew and vessel capacity per time slot
    crew_available = np.full(time_horizon, crew_capacity, dtype=int)
    vessel_available = np.full((time_horizon, num_vessels), vessel_capacity, dtype=int)

    schedule_rows = []
    total_downtime_cost = 0.0

    for idx, task in alerts.iterrows():
        component = task["component"]
        duration = COMPONENT_RULES[component]["duration_hours"]
        crew_needed = COMPONENT_RULES[component]["crew_required"]
        urgency = task["p_fail_14d"]
        downtime_cost = downtime_scale * urgency

        # Try to assign earliest feasible slot and vessel
        assigned = False
        for t in range(time_horizon):
            for v in range(num_vessels):
                if vessel_available[t, v] >= duration and crew_available[t] >= crew_needed:
                    # Assign task
                    vessel_available[t, v] -= duration
                    crew_available[t] -= crew_needed

                    schedule_rows.append({
                        "task": idx,
                        "turbine_id": task["turbine_id"],
                        "component": component,
                        "time": t,
                        "vessel": v,
                        "urgency": urgency,
                        "downtime_cost": downtime_cost
                    })
                    total_downtime_cost += downtime_cost
                    assigned = True
                    break
            if assigned:
                break

    schedule_df = pd.DataFrame(schedule_rows)
    # Total cost = downtime + vessels used (1 per vessel per day)
    vessel_usage_cost = vessel_cost * np.sum(vessel_available < vessel_capacity)
    total_cost = total_downtime_cost + vessel_usage_cost

    return total_cost, schedule_df
