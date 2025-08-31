import pandas as pd
import numpy as np

import pandas as pd
import numpy as np

def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {csv_path}")
    except pd.errors.EmptyDataError:
        raise ValueError("The CSV file is empty.")
    except pd.errors.ParserError:
        raise ValueError("Error parsing the CSV file.")
    
    try:
        # clean and preprocess the data
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        df.dropna(subset=["Timestamp"], inplace=True)
        df["Hour"] = df["Timestamp"].dt.hour
        df["DayOfWeek"] = df["Timestamp"].dt.day_name()
        
        df["Crowd_Density"] = df["Crowd_Density"].str.title()
        df["Fatigue_Level"] = df["Fatigue_Level"].str.title()
        df["Stress_Level"] = df["Stress_Level"].str.title()

        df["AR_Navigation_Success"] = df["AR_Navigation_Success"].map({"Yes": 1, "No": 0})
        
        # convert fatigue/stress levels to numeric just in case they are not
        level_map = {"Low": 1, "Medium": 2, "High": 3}
        df["Fatigue_Score"] = df["Fatigue_Level"].map(level_map)
        df["Stress_Score"] = df["Stress_Level"].map(level_map)
    except KeyError as e:
        raise KeyError(f"Missing expected column: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during preprocessing: {e}")

    # === SIMULATED ZONE DISTRIBUTION ===
    try:
        np.random.seed(42)

        # Define zones and weights
        zone_centers = {
            "Tawaf": (21.4225, 39.8262),
            "Sa’i": (21.4215, 39.8280),
            "Mina": (21.4300, 39.8900),
            "Arafat": (21.3550, 39.9850),
            "Muzdalifah": (21.3850, 39.8920),
            "Other": (21.4190, 39.8200)
        }

        # Define weights for each zone to simulate a realistic distribution
        # These weights are arbitrary and should be adjusted based on real-world data because the original data
        # set does not provide a clear distribution of zones.
        zone_weights = {
            "Tawaf": 0.25,
            "Sa’i": 0.20,
            "Mina": 0.30,
            "Arafat": 0.10,
            "Muzdalifah": 0.10,
            "Other": 0.05
        }

        # Sample zones based on weights
        zone_choices = np.random.choice(
            list(zone_centers.keys()),
            size=len(df),
            p=list(zone_weights.values())
        )
        df["Zone"] = zone_choices

        # Apply random lat/lon around each zone's center (this is a simulation because the orginal data of the area did not align with the zones)
        jitter = lambda c: np.random.uniform(-0.0015, 0.0015)  # ≈150m variation
        df["Sim_Lat"] = df["Zone"].apply(lambda z: zone_centers[z][0] + jitter(0))
        df["Sim_Lon"] = df["Zone"].apply(lambda z: zone_centers[z][1] + jitter(0))

        df["Location_Lat"] = df["Sim_Lat"]
        df["Location_Long"] = df["Sim_Lon"]

        # Fallback "Real" columns (just duplicates here)
        df["Real_Lat"] = df["Sim_Lat"]
        df["Real_Lon"] = df["Sim_Lon"]

    except Exception as e:
        raise RuntimeError(f"Error during simulated zone distribution: {e}")

    return df





# NOTE: I DID NOT NEED DO THE FOLLOWING FUNCTIONS BELOW 
# BECAUSE I AM USING PLOTLY EXPRESS FOR THE GRAPHS AND I MANUALLY 
# LOADED THE DATA AS I WAS MAKING THE GRAPHS ON app.py

# === AGGREGATE DATA FOR DASHBOARD ===
# This function aggregates the data for various metrics to be displayed on the dashboard.
def aggregate_metrics(df: pd.DataFrame) -> dict:
    aggregations = {}

    # 1. Most common fatigue and stress levels by hour (for trends)
    # Average numeric fatigue/stress score by hour
    aggregations['fatigue_stress_by_hour'] = df.groupby("Hour")[["Fatigue_Score", "Stress_Score"]].mean().reset_index()

    # 2. Incident counts by type and crowd level
    aggregations['incidents_by_type_and_density'] = (
        df.groupby(["Incident_Type", "Crowd_Density"])
        .size()
        .reset_index(name="Count")
    )

    # 3. Satisfaction vs perceived safety by nationality
    aggregations['safety_vs_satisfaction'] = df.groupby("Nationality")[["Satisfaction_Rating", "Perceived_Safety_Rating"]].mean().reset_index()

    # 4. Movement speed by location (for heatmap)
    aggregations['movement_speed_by_location'] = (
        df.groupby(["Location_Lat", "Location_Long"])["Movement_Speed"]
        .mean()
        .reset_index()
    )

    # 5. Wait time by transport mode
    aggregations['wait_time_by_transport'] = df.groupby("Transport_Mode")["Waiting_Time_for_Transport"].mean().reset_index()

    return aggregations




# === AGGREGATE MOVEMENT SPEED FOR HEATMAP ===
# This function prepares the data for the movement speed heatmap.
def aggregate_movement_speed_for_heatmap(df: pd.DataFrame, use_simulated=True) -> pd.DataFrame:
    """
    Prepares data for movement speed heatmap.
    Groups lat/lon into a grid and averages movement speed.
    """
    lat_col = "Sim_Lat" if use_simulated else "Real_Lat"
    lon_col = "Sim_Lon" if use_simulated else "Real_Lon"

    # Safety check: Make sure those columns exist
    if lat_col not in df.columns or lon_col not in df.columns:
        raise KeyError(f"Missing expected column: {lat_col} or {lon_col}")

    df = df.copy()
    df["lat_rounded"] = df[lat_col].round(4)
    df["lon_rounded"] = df[lon_col].round(4)

    heatmap_df = df.groupby(["lat_rounded", "lon_rounded"])["Movement_Speed"].mean().reset_index()
    heatmap_df.rename(columns={
        "lat_rounded": "Latitude",
        "lon_rounded": "Longitude",
        "Movement_Speed": "Avg_Speed"
    }, inplace=True)

    return heatmap_df

