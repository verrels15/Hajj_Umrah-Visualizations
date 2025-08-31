import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from branca.element import Template, MacroElement
from folium.plugins import HeatMap



# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data_aggregations import load_and_clean_data

# === Load data using my data_aggregation functions ===
df = load_and_clean_data("data/hajj_umrah_crowd_management_dataset.csv")

# === Page Title ===
st.title("🕋 HajjSense Interactive Map & Incident Monitor 🕋")
st.markdown("""
**Welcome to HajjSense!**
This dashboard aims to support the health, safety, and movement experience of all pilgrims. I was inspired to make this dashboard to help improve the experience of Hajj and Umrah pilgrims
after seeing the challenges faced by many during the pilgrimage when I went with my family.
All data is aggregated and anonymized to respect individual privacy.
""")



# === Sidebar: How to Use ===
with st.sidebar:
    st.title("🕋 HajjSense Guide")

    st.markdown("""

    1. **Interactive Map:** 
    This map helps to showcase the crowd
    density of the areas of Hajj and Umrah.

    2. **Stress & Fatigue Trends:**  
    This graph helps how scores change over different hours
    between fatigure and stress.

    3. **Incident Frequency by Density:**  
    See incidents by crowd levels and by hour.

    4. **Animated Movement Heatmap:**  
    Watch crowd speed patterns across the day.

    5. **Nationality Insights:**  
    Explore the top nationality attendees.

    6. **Average Transport Waiting Time Across Zones**  
    Look at the average waiting time for different transport modes in
    different zones.
    
    7. **Satisfaction vs Perceived Safety:**
    This graph helps to compare the perceived safety and satisfaction
    levels of different nationalities.
    8. **Incident Frequency Over Time:**
    This graph helps to see the frequency of incidents
    over different hours.
    
    9. **Stress Level by Pilgrim Experience:**
    This graph helps to compare the stress levels
    of first-time and experienced pilgrims.
    
    10. **Movement Speed by Pilgrim Experience:**
    This graph helps to compare the movement speed
    of first-time and experienced pilgrims.
    
    11. **Health Condition Frequency:**
    This graph helps to see the frequency of health
    conditions reported by pilgrims.

    
    ---
    *Data anonymized and partially simulated for demonstration purposes.*
    """)



# === Quick Metrics ===
col1, col2, col3 = st.columns(3)
col1.metric("Total Incidents", f"{df['Incident_Type'].count()}")
col2.metric("Avg Movement Speed", f"{df['Movement_Speed'].mean():.2f} m/s")
col3.metric("Top Risk Area", df["Zone"].mode()[0] if "Zone" in df.columns else "Mina")

st.divider()





# === MAP SECTION ===
with st.expander("View Interactive Map", expanded=False):
    st.subheader("Interactive Map of Zones + Incidents")

    try:
        # === Filters ===
        map_day = st.selectbox("Map View: Select Day", sorted(df["DayOfWeek"].unique()), key="map_day_filter")
        map_df = df[df["DayOfWeek"] == map_day].copy()

        activity_options = ["All"] + sorted(map_df["Activity_Type"].dropna().unique())
        activity_filter = st.selectbox("Filter Activity", activity_options, key="activity_filter_map")
        if activity_filter != "All":
            map_df = map_df[map_df["Activity_Type"] == activity_filter]

        incident_options = sorted(map_df["Incident_Type"].dropna().unique())
        incident_filter = st.multiselect("Incident Types to Show", incident_options, default=incident_options)
        map_df = map_df[map_df["Incident_Type"].isin(incident_filter)]

        color_mode = st.radio("Color Markers By:", ["Crowd Density", "Activity Type"], horizontal=True)

        # Color logic
        crowd_color_map = {"Low": "green", "Medium": "orange", "High": "red"}
        activity_color_map = {
            "Tawaf": "blue", "Prayer": "purple", "Resting": "gray",
            "Sa’i": "cadetblue", "Transport": "lightgreen", "Other": "black"
        }

        def get_color(row):
            try:
                if color_mode == "Crowd Density":
                    return crowd_color_map.get(row["Crowd_Density"], "gray")
                else:
                    return activity_color_map.get(row["Activity_Type"], "gray")
            except KeyError:
                return "gray"

        # === Create Map ===
        m = folium.Map(location=[21.4225, 39.8262], zoom_start=13)
        incident_layer = folium.FeatureGroup(name="Incidents")
        heatmap_layer = folium.FeatureGroup(name="Heatmap")

        # Zone markers based on the areas
        zones = {
            "Tawaf (Masjid al-Haram)": (21.4225, 39.8262),
            "Sa’i": (21.4185, 39.8295),
            "Mina": (21.4290, 39.8897),
            "Arafat": (21.3541, 39.9832),
            "Muzdalifah": (21.3865, 39.8930)
        }

        # Add zone markers to the map (start with blue)
        for name, (lat, lon) in zones.items():
            folium.Marker(
                location=[lat, lon],
                popup=name,
                tooltip=name,
                icon=folium.Icon(color="blue", icon="star")
            ).add_to(incident_layer)

        # Incident markers
        # credit: https://stackoverflow.com/questions/62517929/python-folium-map-developement 
        for _, row in map_df.iterrows():
            try:
                folium.CircleMarker(
                    location=[row["Location_Lat"], row["Location_Long"]],
                    color=get_color(row),
                    fill=True,
                    fill_opacity=0.6,
                    popup=(
                        f"<b>Incident:</b> {row.get('Incident_Type', 'N/A')}<br>"
                        f"<b>Activity:</b> {row.get('Activity_Type', 'N/A')}<br>"
                        f"<b>Crowd:</b> {row.get('Crowd_Density', 'N/A')}<br>"
                        f"<b>Stress:</b> {row.get('Stress_Level', 'N/A')}<br>"
                        f"<b>Fatigue:</b> {row.get('Fatigue_Level', 'N/A')}"
                    ),
                    tooltip=f"{row.get('Incident_Type', 'Incident')} | {row.get('Activity_Type', 'Activity')}"
                ).add_to(incident_layer)
            except Exception as e:
                st.warning(f"Could not plot marker: {e}")

        # Heatmap layer
        try:
            heat_data = map_df[["Location_Lat", "Location_Long"]].dropna().values.tolist()
            HeatMap(
                heat_data,
                radius=25,
                blur=20,
                min_opacity=0.3,
                gradient={
                    0.2: 'blue',
                    0.4: 'lime',
                    0.6: 'yellow',
                    0.8: 'orange',
                    1.0: 'red'
                }
            ).add_to(heatmap_layer)
        except Exception as e:
            st.error(f"Failed to load heatmap data: {e}")

        # Add layers
        incident_layer.add_to(m)
        heatmap_layer.add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)

        # Show the map
        folium_static(m, height=600)

        # Map legend
        st.markdown("""
        ### Map Legend

        #### Incidents by Crowd Level
        - 🟢 Low Crowd
        - 🟠 Medium Crowd
        - 🔴 High Crowd

        #### Heatmap (Density Color)
        - 🔵 Low
        - 🟩 Medium
        - 🟨 High
        - 🔴 Very High
        """)
    
    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except Exception as e:
        st.error(f"Unexpected error generating map: {e}")







# === FATIGUE & STRESS TRENDS ===
# credit to: https://discuss.streamlit.io/t/expander-expanded-false-not-working/20786 
with st.expander("View Stress vs Fatigue", expanded=False):
    try:
        # Filter by day
        day_selected = st.selectbox("Choose a Day of the Week", sorted(df["DayOfWeek"].dropna().unique()))

        df_filtered = df[df["DayOfWeek"] == day_selected]

        # Group & aggregate by hour
        fatigue_stress_by_hour = df_filtered.groupby("Hour")[["Fatigue_Score", "Stress_Score"]].mean().reset_index()

        if fatigue_stress_by_hour.empty:
            st.warning(f"No data available for {day_selected}.")
        else:
            # Melt the DataFrame for Plotly
            melted = fatigue_stress_by_hour.melt(id_vars="Hour", var_name="Metric", value_name="Avg Score")

            # --- Visualization ---
            st.header(f"Fatigue & Stress by Hour on {day_selected}")
            fig = px.line(
                melted,
                x="Hour",
                y="Avg Score",
                color="Metric",
                markers=True,
                title=f"Average Fatigue and Stress Scores by Hour ({day_selected})",
                color_discrete_map={
                    "Fatigue_Score": "orange",
                    "Stress_Score": "red"
                }
            )

            # allows for to see a range of hours
            fig.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    tick0=0,
                    dtick=1,
                    tickvals=list(range(0, 24)),
                    ticktext=[
                        "12AM", "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", "8AM", "9AM", "10AM", "11AM",
                        "12PM", "1PM", "2PM", "3PM", "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM", "11PM"
                    ]
                )
            )

            st.plotly_chart(fig)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred while generating the chart: {e}")








# === INCIDENT FREQUENCY BY DENSITY GRAPH ===
with st.expander("Incident Frequency by Crowd Density", expanded=False):
    try:
        # === FILTERS ===
        incident_day = st.selectbox("Filter by Day", sorted(df["DayOfWeek"].dropna().unique()), key="incident_day_filter")
        df_day_filtered = df[df["DayOfWeek"] == incident_day].copy()

        # Filter by Activity Type
        activity_options = sorted(df_day_filtered["Activity_Type"].dropna().unique())
        selected_activity = st.selectbox("Filter by Activity Type", ["All"] + activity_options, key="activity_filter")

        if selected_activity != "All":
            df_day_filtered = df_day_filtered[df_day_filtered["Activity_Type"] == selected_activity]

        if df_day_filtered.empty:
            st.warning("No data available for the selected filters.")
        else:
            # Add Hour column
            df_day_filtered["Hour"] = df_day_filtered["Timestamp"].dt.hour

            # === VIEW TOGGLE ===
            view_mode = st.radio("Choose View Mode", ["Summary View", "Detailed View"], horizontal=True)

            # === TOGGLE FOR COUNT VS PERCENT ===
            show_pct = st.toggle("Show as Percentages")
            y_col = "Count"
            y_title = "Number of Incidents"

            # === AGGREGATE DATA ===
            if view_mode == "Summary View":
                incidents = df_day_filtered.groupby(["Incident_Type", "Crowd_Density"]).size().reset_index(name="Count")
            else:
                incidents = df_day_filtered.groupby(["Hour", "Incident_Type", "Crowd_Density"]).size().reset_index(name="Count")

            # Sort crowd levels logically
            incidents["Crowd_Density"] = pd.Categorical(incidents["Crowd_Density"], categories=["Low", "Medium", "High"], ordered=True)

            # Sort incident types logically
            custom_incident_order = ["Security Breach", "Theft", "Unruly Behavior", "Medical Emergency", "Lost Pilgrim"]
            incidents["Incident_Type"] = pd.Categorical(incidents["Incident_Type"], categories=custom_incident_order, ordered=True)

            # Convert to percentage if toggled
            if show_pct:
                if view_mode == "Summary View":
                    total_by_type = incidents.groupby("Incident_Type")["Count"].transform("sum")
                else:
                    total_by_type = incidents.groupby(["Hour", "Incident_Type"])["Count"].transform("sum")
                incidents["Percent"] = (incidents["Count"] / total_by_type) * 100
                y_col = "Percent"
                y_title = "Percent of Incidents"

            # === HANDLE TOOLTIP COLUMNS DYNAMICALLY ===
            hover_data_cols = ["Incident_Type", "Crowd_Density", y_col]
            if view_mode == "Detailed View":
                hover_data_cols.append("Hour")

            # === PLOT ===
            fig2 = px.bar(
                incidents,
                x="Incident_Type",
                y=y_col,
                color="Crowd_Density",
                animation_frame="Hour" if view_mode == "Detailed View" else None,
                barmode="group",
                title=f"Incident Frequency by Crowd Density ({incident_day}) - {view_mode}",
                color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"},
                category_orders={
                    "Incident_Type": custom_incident_order,
                    "Crowd_Density": ["Low", "Medium", "High"]
                },
                hover_data=hover_data_cols
            )

            fig2.update_layout(xaxis_title="Incident Type", yaxis_title=y_title)
            st.plotly_chart(fig2)

            # === DOWNLOAD BUTTON ===
            st.download_button(
                label="Download Incident Data (Filtered)",
                data=incidents.to_csv(index=False),
                file_name=f"incident_data_{incident_day}_{selected_activity}.csv",
                mime="text/csv"
            )

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error: {e}")
    except Exception as e:
        st.error(f"Unexpected error generating incident chart: {e}")

    
    
    
    
    
    
# === ANIMATED MOVEMENT SPEED HEATMAP ===    
with st.expander("Animated Movement Speed Heatmap by Hour", expanded=False):
    try:
        st.subheader("Movement Density Over Time")

        # === FILTERS ===
        heatmap_day = st.selectbox(
            "Select Day for Heatmap", 
            sorted(df["DayOfWeek"].dropna().unique()), 
            key="heatmap_day_filter"
        )
        df_day = df[df["DayOfWeek"] == heatmap_day].copy()

        if df_day.empty:
            st.warning(f"No movement data available for {heatmap_day}.")
        else:
            # Toggle: Simulated or Real Coordinates
            use_sim = st.toggle("Use Simulated Coordinates?", value=True, key="heatmap_use_sim_toggle")
            lat_col = "Sim_Lat" if use_sim else "Real_Lat"
            lon_col = "Sim_Lon" if use_sim else "Real_Lon"

            # Assign lat/lon and handle missing values
            if lat_col not in df_day.columns or lon_col not in df_day.columns:
                st.error(f"Missing columns: {lat_col} or {lon_col}")
            else:
                df_day["Latitude"] = df_day[lat_col]
                df_day["Longitude"] = df_day[lon_col]

                # Create AM/PM time labels for sorting/animation
                hour_labels = {i: f"{i%12 or 12}{'AM' if i < 12 else 'PM'}" for i in range(24)}

                # Ensure 'Hour' column exists and is numeric
                if "Hour" not in df_day.columns:
                    st.error("Missing 'Hour' column in dataset.")
                else:
                    df_day = df_day.dropna(subset=["Hour", "Latitude", "Longitude", "Movement_Speed"])
                    df_day["Hour"] = df_day["Hour"].astype(int)
                    df_day = df_day.sort_values("Hour")
                    df_day["Time_Label"] = df_day["Hour"].map(hour_labels)

                    # === Animated Heatmap ===
                    fig_heatmap = px.density_mapbox(
                        df_day,
                        lat="Latitude",
                        lon="Longitude",
                        z="Movement_Speed",   # Color intensity by speed
                        radius=25,            # Bigger = more smoothing
                        animation_frame="Time_Label",  # Animate across hours
                        center={"lat": 21.4225, "lon": 39.8262},
                        zoom=13,
                        height=600,
                        mapbox_style="carto-positron",
                        color_continuous_scale="Turbo",
                        range_color=[0, 2],  # Adjust depending on speed range
                        title="Crowd Movement Speed Density by Hour"
                    )

                    fig_heatmap.update_layout(
                        coloraxis_colorbar=dict(title="Speed (m/s)"),
                        margin=dict(l=0, r=0, t=40, b=0)
                    )

                    st.plotly_chart(fig_heatmap)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Data formatting issue: {e}")
    except Exception as e:
        st.error(f"Unexpected error rendering the heatmap: {e}")







# === NATIONAL DOVERSITY GRAPH ===
with st.expander("Nationality Diversity", expanded=False):
    try:
        st.subheader("Distribution of Participants by Nationality")

        if "Nationality" not in df.columns:
            st.error("The 'Nationality' column is missing from the dataset.")
            st.stop()

        # Count nationality occurrences
        nationality_counts = df["Nationality"].dropna().value_counts().reset_index()
        nationality_counts.columns = ["Nationality", "Count"]

        if nationality_counts.empty:
            st.warning("No nationality data available to display.")
            st.stop()

        # If too many, group smaller ones into "Other" to make it easier to read
        top_n = 10
        if len(nationality_counts) > top_n:
            top_nationalities = nationality_counts[:top_n]
            other_count = nationality_counts[top_n:]["Count"].sum()
            top_nationalities = pd.concat(
                [top_nationalities, pd.DataFrame([{"Nationality": "Other", "Count": other_count}])]
            )
        else:
            top_nationalities = nationality_counts

        # Choose chart type
        chart_type = st.radio("Choose View:", ["Pie Chart", "Bar Chart"], horizontal=True)

        # Plot
        if chart_type == "Pie Chart":
            fig_nat = px.pie(
                top_nationalities,
                names="Nationality",
                values="Count",
                title="Nationality Distribution",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
        else:  # Bar chart
            fig_nat = px.bar(
                top_nationalities,
                x="Nationality",
                y="Count",
                title="Nationality Distribution",
                text="Count",
                color="Nationality",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_nat.update_layout(
                xaxis_title="Nationality",
                yaxis_title="Number of Participants"
            )

        st.plotly_chart(fig_nat, use_container_width=True)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error in nationality data: {e}")
    except Exception as e:
        st.error(f"Unexpected error while rendering nationality chart: {e}")







# === TRANSPORT WAITING TIME GRAPH ===
with st.expander("Transport Waiting Time by Zone", expanded=False):
    try:
        st.subheader("Average Transport Waiting Time Across Zones")

        # === FILTERS ===
        if "DayOfWeek" not in df.columns:
            st.error("Missing 'DayOfWeek' column in the dataset.")
            st.stop()

        transport_day = st.selectbox(
            "Select Day for Transport Analysis",
            sorted(df["DayOfWeek"].dropna().unique()),
            key="transport_day_filter"
        )
        df_transport = df[df["DayOfWeek"] == transport_day].copy()

        # Ensure necessary columns exist
        required_columns = {"Transport_Mode", "Waiting_Time_for_Transport", "Zone"}
        if not required_columns.issubset(df_transport.columns):
            st.error(f"Missing one or more required columns: {required_columns}")
            st.stop()

        # Filter out missing or invalid transport entries
        df_transport = df_transport.dropna(subset=list(required_columns))
        if df_transport.empty:
            st.warning(f"No transport data available for {transport_day}.")
            st.stop()

        # Exclude "Walking" transport mode because it is not part of waiting
        df_transport = df_transport[df_transport["Transport_Mode"] != "Walking"]

        if df_transport.empty:
            st.warning(f"No non-walking transport data for {transport_day}.")
            st.stop()

        # Group by Zone and Transport Mode
        transport_wait = df_transport.groupby(
            ["Zone", "Transport_Mode"]
        )["Waiting_Time_for_Transport"].mean().reset_index()

        if transport_wait.empty:
            st.warning("No data available after grouping by Zone and Transport Mode.")
            st.stop()

        # === PLOT ===
        fig_transport = px.bar(
            transport_wait,
            x="Zone",
            y="Waiting_Time_for_Transport",
            color="Transport_Mode",
            barmode="group",
            text_auto=".2s",
            title=f"Average Waiting Time by Zone and Transport Mode ({transport_day})",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig_transport.update_layout(
            xaxis_title="Zone",
            yaxis_title="Average Waiting Time (minutes)",
            legend_title="Transport Mode",
            height=600,
            plot_bgcolor="#0e1117",  # match your dark theme
            paper_bgcolor="#0e1117",
            font_color="white"
        )

        st.plotly_chart(fig_transport, use_container_width=True)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error during transport waiting time analysis: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred while rendering the chart: {e}")








# === SATISFACTION VS PERCEIVED SAFETY GRAPH ===
with st.expander("Satisfaction vs Perceived Safety", expanded=False):
    try:
        st.subheader("Perceived Safety vs Participant Satisfaction")

        # === FILTER DATA ===
        required_columns = {"Satisfaction_Rating", "Perceived_Safety_Rating", "Nationality"}
        if not required_columns.issubset(df.columns):
            st.error(f"Missing one or more required columns: {required_columns}")
            st.stop()

        # Drop missing or invalid ratings
        df_safety = df.dropna(subset=list(required_columns)).copy()

        if df_safety.empty:
            st.warning("No data available after filtering for satisfaction and safety ratings.")
            st.stop()

        # Group by Nationality and average the scores
        safety_summary = df_safety.groupby("Nationality")[["Satisfaction_Rating", "Perceived_Safety_Rating"]].mean().reset_index()

        # Add count of participants per nationality
        safety_summary["Count"] = df_safety["Nationality"].value_counts().reindex(safety_summary["Nationality"]).fillna(0).astype(int).values

        # Filter: Only show nationalities with enough participants (optional)
        min_threshold = 5
        safety_summary = safety_summary[safety_summary["Count"] >= min_threshold]

        if safety_summary.empty:
            st.warning(f"No nationalities with at least {min_threshold} participants.")
            st.stop()

        # === PLOT ===
        fig_safety = px.scatter(
            safety_summary,
            x="Satisfaction_Rating",
            y="Perceived_Safety_Rating",
            size="Count",
            color="Satisfaction_Rating",
            hover_name="Nationality",
            color_continuous_scale="Viridis",
            title="Satisfaction vs Perceived Safety by Nationality",
            size_max=30
        )

        fig_safety.update_layout(
            xaxis_title="Average Satisfaction Rating",
            yaxis_title="Average Perceived Safety Rating",
            height=600,
            coloraxis_colorbar=dict(title="Satisfaction Score")
        )

        st.plotly_chart(fig_safety, use_container_width=True)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error during safety/satisfaction analysis: {e}")
    except Exception as e:
        st.error(f"Unexpected error rendering safety vs satisfaction chart: {e}")






# === INCIDENT FREQUENCY OVER TIME GRAPH ===
with st.expander("Incident Frequency Over Time", expanded=False):
    try:
        st.subheader("Incident Trends Throughout the Day")

        # === FILTERS ===
        if "DayOfWeek" not in df.columns:
            st.error("Missing 'DayOfWeek' column in the dataset.")
            st.stop()

        time_series_day = st.selectbox(
            "Select Day for Incident Timeline",
            sorted(df["DayOfWeek"].dropna().unique()),
            key="incident_time_series_day"
        )
        df_time_filtered = df[df["DayOfWeek"] == time_series_day].copy()

        # Ensure required columns exist
        required_columns = {"Timestamp", "Incident_Type"}
        if not required_columns.issubset(df_time_filtered.columns):
            st.error(f"Missing one or more required columns: {required_columns}")
            st.stop()

        # Prepare data
        df_time_filtered["Hour"] = pd.to_datetime(df_time_filtered["Timestamp"], errors='coerce').dt.hour
        df_time_filtered.dropna(subset=["Hour"], inplace=True)
        df_time_filtered["Hour"] = df_time_filtered["Hour"].astype(int)

        if df_time_filtered.empty:
            st.warning(f"No incident data found for {time_series_day}.")
            st.stop()

        incidents_time = df_time_filtered.groupby(["Hour", "Incident_Type"]).size().reset_index(name="Count")
        if incidents_time.empty:
            st.warning("No incident trends available for the selected day.")
            st.stop()

        # Optional custom sort for incident types
        custom_incident_order = ["Security Breach", "Theft", "Unruly Behavior", "Medical Emergency", "Lost Pilgrim"]
        incidents_time["Incident_Type"] = pd.Categorical(
            incidents_time["Incident_Type"],
            categories=custom_incident_order,
            ordered=True
        )

        # === PLOT ===
        fig_time = px.line(
            incidents_time,
            x="Hour",
            y="Count",
            color="Incident_Type",
            markers=True,
            title=f"Incident Frequency Throughout the Day ({time_series_day})",
            color_discrete_map={
                "Security Breach": "red",
                "Theft": "orange",
                "Unruly Behavior": "purple",
                "Medical Emergency": "green",
                "Lost Pilgrim": "blue"
            },
            labels={"Count": "Number of Incidents", "Hour": "Hour of Day"}
        )

        fig_time.update_layout(
            xaxis=dict(
                tickmode="linear",
                tick0=0,
                dtick=1,
                tickvals=list(range(0, 24)),
                ticktext=[
                    "12AM", "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", "8AM", "9AM", "10AM", "11AM",
                    "12PM", "1PM", "2PM", "3PM", "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM", "11PM"
                ]
            ),
            yaxis_title="Number of Incidents",
            height=600
        )

        st.plotly_chart(fig_time, use_container_width=True)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error during incident trend processing: {e}")
    except Exception as e:
        st.error(f"Unexpected error while generating incident frequency chart: {e}")






# === STRESS LEVEL BY EXPERIENCE GRAPH ===
with st.expander("Stress Level by Pilgrim Experience", expanded=False):
    try:
        st.subheader("Comparing Stress Between First-Time and Experienced Pilgrims")

        # === FILTER ===
        required_columns = {"Pilgrim_Experience", "Stress_Score"}
        if not required_columns.issubset(df.columns):
            st.error(f"Missing one or more required columns: {required_columns}")
            st.stop()

        df_stress = df.dropna(subset=["Pilgrim_Experience", "Stress_Score"]).copy()

        if df_stress.empty:
            st.warning("No data available to compare stress levels between pilgrim types.")
            st.stop()

        # Use Pilgrim_Experience directly
        df_stress["Experience"] = df_stress["Pilgrim_Experience"]

        # Group and calculate average stress score
        stress_summary = df_stress.groupby("Experience")["Stress_Score"].mean().reset_index()

        if stress_summary.empty:
            st.warning("Not enough data to compute average stress scores.")
            st.stop()

        # === PLOT ===
        fig_stress = px.bar(
            stress_summary,
            x="Experience",
            y="Stress_Score",
            color="Experience",
            text_auto=".2f",
            title="Average Stress Level: First-Time vs Experienced Pilgrims",
            color_discrete_map={"First-Time": "blue", "Experienced": "green"}
        )

        fig_stress.update_layout(
            xaxis_title="Pilgrim Type",
            yaxis_title="Average Stress Score",
            height=500,
            showlegend=False
        )

        st.plotly_chart(fig_stress, use_container_width=True)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error while processing stress levels: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")







# === MOVEMENT SPEED BY EXPERIENCE GRAPH ===
with st.expander("Movement Speed by Pilgrim Experience", expanded=False):
    try:
        st.subheader("Comparing Movement Speed Between First-Time and Experienced Pilgrims")

        # === FILTER ===
        required_columns = {"Pilgrim_Experience", "Movement_Speed"}
        if not required_columns.issubset(df.columns):
            st.error(f"Missing one or more required columns: {required_columns}")
            st.stop()

        df_move = df.dropna(subset=["Pilgrim_Experience", "Movement_Speed"]).copy()

        if df_move.empty:
            st.warning("No data available to compare movement speed between pilgrim types.")
            st.stop()

        # Use Pilgrim_Experience directly
        df_move["Experience"] = df_move["Pilgrim_Experience"]

        # Group and calculate average Movement Speed
        speed_summary = df_move.groupby("Experience")["Movement_Speed"].mean().reset_index()

        if speed_summary.empty:
            st.warning("Not enough data to compute average movement speeds.")
            st.stop()

        # === PLOT ===
        fig_move = px.bar(
            speed_summary,
            x="Experience",
            y="Movement_Speed",
            color="Experience",
            text_auto=".2f",
            title="Average Movement Speed: First-Time vs Experienced Pilgrims",
            color_discrete_map={"First-Time": "blue", "Experienced": "green"}
        )

        fig_move.update_layout(
            xaxis_title="Pilgrim Type",
            yaxis_title="Average Speed (m/s)",
            height=500,
            showlegend=False
        )

        st.plotly_chart(fig_move, use_container_width=True)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error while processing movement speed: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")






# === HEALTH CONDITION FREQUENCY GRAPH ===
with st.expander("Health Condition Frequency", expanded=False):
    try:
        st.subheader("Most Common Health Incidents Reported")

        # Check required column
        if "Health_Condition" not in df.columns:
            st.error("Missing 'Health_Condition' column in the dataset.")
            st.stop()

        # Drop missing
        df_health = df.dropna(subset=["Health_Condition"]).copy()

        if df_health.empty:
            st.warning("No health condition data available.")
            st.stop()

        # Remove "Normal" rows because they are not incidents
        df_health = df_health[df_health["Health_Condition"] != "Normal"]

        if df_health.empty:
            st.warning("All health condition data is marked 'Normal'; no incidents to display.")
            st.stop()

        # Group and count
        health_counts = df_health["Health_Condition"].value_counts().reset_index()
        health_counts.columns = ["Health Condition", "Count"]

        if health_counts.empty:
            st.warning("No valid health condition incidents found.")
            st.stop()

        custom_color_map = {
            "Fainting": "#E63946",      # Muted Red
            "Heatstroke": "#F4A261",    # Soft Orange
            "Injured": "#A44CC9",       # Calm Purple
            "Dehydration": "#457B9D"    # Muted Blue
        }

        # Plot
        fig_health = px.bar(
            health_counts,
            x="Health Condition",
            y="Count",
            color="Health Condition",
            text_auto=True,
            color_discrete_map=custom_color_map,
            title="Health Condition Incident Counts"
        )

        fig_health.update_layout(
            xaxis_title="Health Condition",
            yaxis_title="Number of Cases",
            height=500,
            showlegend=False,
            plot_bgcolor="#0e1117",   # Dark background
            paper_bgcolor="#0e1117",
            font_color="white",
            title_font_size=24
        )

        fig_health.update_traces(
            textfont_size=14,
            textposition="outside"
        )

        st.plotly_chart(fig_health, use_container_width=True)

    except KeyError as e:
        st.error(f"Missing expected column: {e}")
    except ValueError as e:
        st.error(f"Value error while processing health incidents: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred while generating the chart: {e}")







st.markdown("""
---
*Disclaimer: The visualizations are based on simulated and sample data for academic purposes. 
Actual real-world conditions may vary.*
""")


