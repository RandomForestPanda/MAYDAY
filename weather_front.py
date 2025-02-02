# Importing Necessary Modules
import requests
import datetime
import streamlit as st
import pandas as pd
from datetime import timedelta
import base64


def get_image_base64(file):
    with open(file,"rb") as f:
        data=f.read()
    return base64.b64encode(data).decode()
img=get_image_base64("image.jpg")
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]
    {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
    }}
    h1, p,h3{{
        color: white;  /* Make the text white */
    }}
    button[data-testid="stBaseButton-secondary"] {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
    }}

    button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: darkorange !important; /* Darker orange on hover */
    }}
    .st-emotion-cache-1wivap2.e1i5pmia3 {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        color: white; /* Text color to ensure readability on top of the image */
        padding: 10px; /* Add some padding for better text visibility */
        border-radius: 5px; /* Optional: add rounded corners */
    }}
    header {{
    background-color: rgba(0, 0, 0, 0) !important; /* Transparent */
    color: white;
    }}


    </style>
    """, unsafe_allow_html=True)
# This method will return us our actual coordinates using our IP address
def locationCoordinates():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        loc = data['loc'].split(',')
        lat, lon = float(loc[0]), float(loc[1])
        city = data.get('city', 'Unknown')
        state = data.get('region', 'Unknown')
        return lat, lon, city, state
    except:
        # Displaying the error message
        print("Internet Not available")
        # Closing the program
        exit()
        return False

def get_weather_data(lat, lon, hours):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&forecast_days=2"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve weather data.")
        return None

st.title("Real-Time Weather Dashboard 🌤️")
st.write("Get live weather updates and forecasts.")

forecast_duration = st.slider("Select forecast duration (hours)", min_value=12, max_value=48, value=24, step=12)
parameter_options = st.multiselect(
    "Choose weather parameters to display:",
    options=["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)"],
    default=["Temperature (°C)", "Humidity (%)"]
)

if st.button("Get Weather Data"):
    lat, lon, city, state = locationCoordinates()
    if lat and lon:
        data = get_weather_data(lat, lon, forecast_duration)
        if data:
            # Calculate the forecast times
            times = [datetime.datetime.now() + timedelta(hours=i) for i in range(forecast_duration)]
            df = pd.DataFrame({"Time": times})

            # Display forecast data
            if "Temperature (°C)" in parameter_options:
                df["Temperature (°C)"] = data['hourly']['temperature_2m'][:forecast_duration]
                st.subheader(f"Temperature Forecast")
                st.line_chart(df.set_index("Time")["Temperature (°C)"])

            if "Humidity (%)" in parameter_options:
                df["Humidity (%)"] = data['hourly']['relative_humidity_2m'][:forecast_duration]
                st.subheader(f"Humidity Forecast")
                st.line_chart(df.set_index("Time")["Humidity (%)"])

            if "Wind Speed (m/s)" in parameter_options:
                df["Wind Speed (m/s)"] = data['hourly']['wind_speed_10m'][:forecast_duration]
                st.subheader(f"Wind Speed Forecast")
                st.line_chart(df.set_index("Time")["Wind Speed (m/s)"])

        # Display current weather data
        if data:
            st.subheader("Current Weather Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ Temperature", f"{data['hourly']['temperature_2m'][0]}°C")
            col2.metric("💧 Humidity", f"{data['hourly']['relative_humidity_2m'][0]}%")
            col3.metric("🌬️ Wind Speed", f"{data['hourly']['wind_speed_10m'][0]} m/s")

# Main method (for console execution, but no longer needed in Streamlit)
if __name__ == "__main__":
    print("---------------GPS Using Python---------------\n")

    # Fetching coordinates
    lat, lon, city, state = locationCoordinates()
    print("You are in {},{}".format(city, state))
    print("Your latitude = {} and longitude = {}".format(lat, lon))
    get_weather_data(lat, lon, forecast_duration)
