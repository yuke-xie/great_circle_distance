from flask import Flask, render_template, request, send_file, jsonify
from geopy.distance import geodesic
import folium
import os
import plotly.graph_objects as go
import numpy as np

app = Flask(__name__)

# Read airport data from the file and store it in a dictionary
def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal_degrees = float(degrees) + (float(minutes) / 60) + (float(seconds) / 3600)
    if direction in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    return decimal_degrees

airport_data = {}
with open('GlobalAirportDatabase.txt', 'r') as file:
    for line in file:
        parts = line.strip().split(':')
        if parts[2] == 'N/A':
            continue
        name = parts[2] + ' (' + parts[0] + ' | ' + parts[1] + ')'
        lat = dms_to_decimal(parts[5], parts[6], parts[7], parts[8])
        lon = dms_to_decimal(parts[9], parts[10], parts[11], parts[12])
        airport_data[name] = {'name': name, 'lat': lat, 'lon': lon}

@app.route('/')
def index():
    return render_template('index.html', airports=list(airport_data.values()))

@app.route('/autocomplete_data')
def autocomplete_data():
    return jsonify(list(airport_data.values()))

@app.route('/calculate', methods=['POST'])
def calculate():
    if request.method == 'POST':
        code1 = request.form['location1']
        code2 = request.form['location2']

        airport1 = airport_data.get(code1)
        airport2 = airport_data.get(code2)

        if not airport1 or not airport2:
            return render_template('index.html', airports=list(airport_data.values()), error='Invalid airport codes.')

        coords_1 = (airport1['lat'], airport1['lon'])
        coords_2 = (airport2['lat'], airport2['lon'])

        print(coords_1, coords_2)

        distance = int(geodesic(coords_1, coords_2).kilometers)
        data=go.Scattergeo(
            lat = [airport1['lat'], airport2['lat']],
            lon = [airport1['lon'], airport2['lon']],
            mode = 'lines',
            line = dict(width = 2.5, color = 'blue'),
        )

        fig = go.Figure(data)

        fig.add_trace(go.Scattergeo(
                    locationmode = 'USA-states',
                    lat = [airport1['lat'], airport2['lat']],
                    lon = [airport1['lon'], airport2['lon']],
                    text = [airport1['name'][-4:-1], airport2['name'][-4:-1]],
                    textfont = {"color": 'black',
                                "family":'Times New Roman',
                                "size":16},
                    textposition="top center",
                    name = "Candidate Facility",
                    mode ="markers+text",
                    marker = dict(
                        size = 10,
                        color = "black",
                        line_color='black',
                        line_width=0.5,
                        sizemode = 'area')))

        # Calculate the midpoint coordinates
        midpoint_lat = (airport1['lat'] + airport2['lat']) / 2
        midpoint_lon = (airport1['lon'] + airport2['lon']) / 2

        # Set the layout to a 3D globe with the calculated midpoint as the center
        fig.update_geos(
            showsubunits=True, subunitcolor="Blue",
            showland=True,
            showcountries=True,
            showocean=True,
            countrywidth=1,
            landcolor='LightYellow',
            lakecolor='LightBlue',
            oceancolor="LightBlue",
            # bgcolor='white',
            # center_lat=midpoint_lat,
            # center_lon=midpoint_lon,
            projection=dict(
                type='orthographic',
                rotation=dict(
                    lon=-midpoint_lon,
                    lat=-midpoint_lat,
                    roll=0
                )
            ),
        )


        fig.update_layout(
            # paper_bgcolor='white',
            # plot_bgcolor='white',
            showlegend = False,
            margin=dict(l=0, r=0, t=200, b=200, pad=0),
        )

        # Save the map to a file (you can customize the filename)
        map_filename = 'great_circle_map.html'
        fig.write_html('templates/' + map_filename)

        return render_template('index.html', airports=list(airport_data.values()), distance=distance, map_filename=map_filename)

@app.route('/static/<filename>')
def serve_static(filename):
    return send_file(os.path.join('templates', filename))

if __name__ == '__main__':
    app.run(debug=True)