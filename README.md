# HajjSense: Human-Centered Crowd Insights by Verrels Eugeneo

Welcome to **HajjSense**, which is my interactive dashboard that visualizes crowd behavior, safety incidents, and human experiences during the Hajj and Umrah pilgrimage.

This project combines **interactive maps**, **animated heatmaps**, **stress and fatigue patterns**, **incident analytics**, and **health condition insights**.
---


## Acknowledgements

I would like to acknowledge the following resources and tools that helped me complete this project:

- **Folium Documentation**: For teaching me how to create interactive maps, heatmaps, and layered controls: https://python-visualization.github.io/folium/latest/ 
- **Plotly Express Documentation**: For helping me design clean and customizable graphs for my visualizations: https://plotly.com/python/line-and-scatter/ 
- **ChatGPT**: For helping brainstorm ideas, debug issues, and explain how to improve my dashboard step-by-step.
- **StackOverflow**: For providing helpful answers and code snippets whenever I got stuck during development.
- **Microsoft Copilot**: For assisting with some basic code completions and helping streamline repetitive tasks.
- **Streamlit Community and Docs**: For making it easy to build a full interactive dashboard quickly and effectively: https://docs.streamlit.io/develop/tutorials 

I learned a lot from experimenting, making mistakes, and finding solutions through these tools and resources.  



## Features

- **Interactive Map**: Visualize incidents, zones, and crowd density in Mecca during Hajj.
- **Animated Heatmap**: Watch real-time movement speed densities across different hours of the day.
- **Stress vs Fatigue**: Understand physical and psychological strain across hours.
- **Incident Frequency Analysis**: Compare incidents across crowd densities and over time.
- **Nationality Diversity**: Explore where pilgrims are traveling from.
- **Transport Wait Times**: Analyze waiting time patterns by zone and transport type.
- **Health Condition Trends**: View most common health-related incidents (heatstroke, dehydration, injuries).
- **Satisfaction vs Safety**: Analyze the perception of safety vs. satisfaction among pilgrims.
- **Pilgrim Experience**: Compare stress levels, movement speeds, and experiences between first-time and experienced pilgrims.
- **Sidebar Directions**: Easy-to-follow guide on how to use the dashboard.

---



## Lessons Learned and Tools Used

### Tools and Technologies
- **Streamlit**: Built the interactive dashboard interface with collapsible panels, metrics, expander views, and clean UI components.
- **Pandas**: Processed and cleaned CSV data, aggregated metrics, and handled missing values, which was easier to do since we had plenty of assignments doing this.
- **Plotly Express**: Created responsive graphs (bar charts, line plots, animated density maps) with interactive features.
- **Folium + Streamlit-Folium**: Developed layered maps showing zones, incidents, and real-time heatmaps over Makkah areas.
- **Branca Templates**: Added custom legends for incident levels and heatmap densities on Folium maps.
- **Python**: Used core Python data manipulation techniques for dynamic grouping, filtering, sorting.

---

## What I Learned

Through this project, I learned how to build a full dashboard from start to finish — starting with cleaning up messy data and ending with creating cool interactive graphs that tell a real story. I worked a lot with mapping things using latitude and longitude, which let me show where incidents happened on a real map. I also created filters, toggles, dropdowns, and animations, which made the dashboard feel a lot more dynamic and fun to use. Most of these were not too difficult since we had some experience working with them throughout the semester.

One thing I made sure of was being careful about how I presented sensitive topics like health issues and crowd safety. I didn't want the graphs to scare people or show anything unfair, so I learned to think about ethics while visualizing the data. This was something that was discussed in our last lecture as a class. I also got a lot of practice cleaning up the dataset — like removing useless categories (such as "Normal" in the health conditions) and fixing missing values so the graphs would make more sense.

Another big thing I improved on was thinking about the user's experience. I tried to make everything clear and simple to follow by adding map legends, sidebar instructions, and easy toggles. Overall, one lesson this class taught me is that I realized that making graphs isn't just about showing numbers.  it's about telling a story that people can understand quickly and safely.

---
 This project helped me grow as both a technical builder and a data storyteller while doing something that is meaningful to me.

ALSO: Some location data, especially for the animated movement heatmaps, was slightly randomized and manipulated for visualization purposes. The original dataset had inaccurate or widely spread latitude/longitude values that did not properly map to the Hajj zones (like Masjid al-Haram, Mina, Arafat, etc.). To make the heatmaps more realistic and focused, I generated simulated coordinates centered around actual Hajj zones while preserving the overall patterns of the data.

All adjustments were made purely for educational and demonstration reasons, and **do not represent real-world crowd behavior or exact incident locations**.


## Challenges and What I Would Do Differently

### Challenges I Faced
- **Messy and Inaccurate Data**:  
  Some latitude and longitude values were unrealistic or missing, which made it hard to plot incidents correctly. I had to simulate more realistic coordinates for the heatmaps.
  
- **Streamlit Design Limitations**:  
  Streamlit was simple to use, but customizing detailed layouts, themes, and interactions (like light/dark mode toggles or multi-page routing) had some restrictions compared to full web frameworks.

- **Ethical Visualization**:  
  I had to think carefully about how to display sensitive topics like health issues and crowd risks without making it feel exaggerated or alarming.

---

### What I Would Do Differently Next Time

- **Organize Code into Modules**:  
  If I did it again, I would split the app.py file even more into separate files for graphs, maps, filters, etc. This would make the code cleaner and easier to update.

- **Test Mobile Responsiveness**:  
  I would check earlier how the dashboard looks on tablets and phones, and make better design choices (like larger fonts or mobile-friendly maps). My main focus was mainly on websites.

---

##  Future Features I Would Add
- **Real-Time Updates**:  
  Allow live data updates instead of using a static CSV file, so incidents and crowd movements could refresh automatically, though I am not sure where to find a real-time data for this.

- **Story Mode for First-Time Users**:  
  Add a simple guided tour that walks users through how to use each part of the dashboard the first time they open it. Also would like to add StreetView instead of Mapview.

- **Accessibility Improvements**:  
  Make sure the dashboard fully supports screen readers, keyboard navigation, and high-contrast modes for better inclusivity. Perhaps create an actual app people can use in real-time while
  they are doing their pilgrims.

---



## How to Run Locally

1. **Install required libraries**:

```bash
pip install streamlit pandas plotly folium streamlit-folium
streamlit run app.py
