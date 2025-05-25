import pandas as pd
import folium
import streamlit as st
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import branca.colormap as cm

# dictionar culori pt evenimente
event_colors = {
    'Air/drone strike': 'red',
    'Shelling/artillery/missile attack': 'blue',
    'Armed clash': 'green',
    'Disrupted weapons use': 'purple',
    'Remote explosive/landmine/IED': 'orange',
    'Other': 'gray',
    'Non-state actor overtakes territory': 'yellow',
    'Agreement': 'cyan',
    'Peaceful protest': 'lime',
    'Grenade': 'pink',
    'Looting/property destruction': 'brown',
    'Attack': 'darkred',
    'Abduction/forced disappearance': 'darkblue',
    'Headquarters or base established': 'darkgreen',
    'Arrests': 'violet',
    'Mob violence': 'lightblue',
    'Government regains territory': 'darkviolet',
    'Change to group/activity': 'lightgreen',
    'Sexual violence': 'magenta',
    'Violent demonstration': 'lightpink',
    'Chemical weapon': 'olive',
    'Non-violent transfer of territory': 'lightcyan',
    'Protest with intervention': 'darkorange',
    'Suicide bomb': 'black',
    'Excessive force against protesters': 'gold',
}

# incarcare date
file_path = "Ukraine_Black_Sea_2020_2025_Mar07.csv"
df = pd.read_csv(file_path, parse_dates=['event_date'])
df['event_date'] = pd.to_datetime(df['event_date'])

# numarare inregistrari per event type
event_counts = df['sub_event_type'].value_counts()
# event_options = [f"<span style='color:{event_colors.get(event, 'black')}'>{event} ({count})</span>" for event, count in event_counts.items()]
event_options = [f"{event} ({count})" for event, count in event_counts.items()]

# Display colored legend
legend_html1 = """<div style='font-size:14px;'>"""
legend_html2 = """<div style='font-size:14px;'>"""
i=0
for event, color in event_colors.items():
    if event in event_counts:
        if i is 0:
            legend_html1 += f"<div style='display: flex; align-items: center;'><div style='width: 12px; height: 12px; background-color: {color}; margin-right: 5px;'></div>{event} ({event_counts[event]})</div>"
            i=1
        else:
            legend_html2 += f"<div style='display: flex; align-items: center;'><div style='width: 12px; height: 12px; background-color: {color}; margin-right: 5px;'></div>{event} ({event_counts[event]})</div>"
            i=0
legend_html1 += "</div>"
legend_html2 += "</div>"

# filtre
st.title("Hartă interactivă pentru evenimentele din războiul Rusia-Ucraina")
min_date, max_date = df['event_date'].min().date(), df['event_date'].max().date()
columns=st.columns([1,1])
with columns[0]:
    selected_min_date=st.date_input("Dată început",min_date,min_value=min_date,max_value=max_date)
with columns[1]:
    selected_max_date=st.date_input("Dată sfărșit",min_value=min_date,max_value=max_date)
min_fatalities,max_fatalities=df['fatalities'].min(),df['fatalities'].max()
selected_fatalities=st.slider("Interval număr de victime",min_value=min_fatalities,max_value=max_fatalities,value=(min_fatalities,max_fatalities))
selected_sub_event = st.multiselect("Selectare tip eveniment", options=event_options, default=["Air/drone strike (28307)","Armed clash (58480)","Non-state actor overtakes territory (575)"])
selected_events = [event.split(" (")[0] for event in selected_sub_event]
#selected_source = st.multiselect("Select Source", df['source'].unique(), default=df['source'].unique())
max_events = st.slider("Limitare număr evenimente", min_value=1000, max_value=len(df.index), value=5000, step=1000)

# filtrare date
filtered_df = df[(df['event_date'] >= pd.to_datetime(selected_min_date)) & (df['event_date'] <= pd.to_datetime(selected_max_date))]
filtered_df = filtered_df[filtered_df['sub_event_type'].isin(selected_events)]
filtered_df=filtered_df[(filtered_df['fatalities'] >= selected_fatalities[0]) & (filtered_df['fatalities'] <= selected_fatalities[1])]
#filtered_df = filtered_df[filtered_df['source'].isin(selected_source)]
filtered_df = filtered_df.head(max_events)  

# creare harta
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5)
#colormap = cm.linear.YlOrRd.scale(min_fatalities, max_fatalities)  
marker_cluster = MarkerCluster().add_to(m)
for _, row in filtered_df.iterrows():
    color = event_colors.get(row['sub_event_type'])
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5 + (row['fatalities'] / max_fatalities) * 100,
        # color=colormap(row['fatalities'])
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        icon=folium.Icon(color=color),
        popup=f'<span style="color:#FF4B4B;">Eveniment: </span>{row['sub_event_type']}<br><span style="color:#FF4B4B;">Dată: </span>{row['event_date'].date()}<br><span style="color:#FF4B4B;">Descriere: </span>{row['notes']}<br><span style="color:#FF4B4B;">Țară: </span>{row['country']}<br><span style="color:#FF4B4B;">Localitate: </span>{row['location']}'
    ).add_to(marker_cluster)

# afisare harta
folium_static(m)  
st.write(f"Se afișează {len(filtered_df)} evenimente")

columns=st.columns([1,1])
with columns[0]:
    st.markdown(legend_html1, unsafe_allow_html=True)
with columns[1]:
    st.markdown(legend_html2, unsafe_allow_html=True)
