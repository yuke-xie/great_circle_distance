from flask import Flask, render_template, request, send_file, jsonify
from geopy.distance import geodesic
import folium
import os

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
        if parts[2]=='N/A': continue
        name = parts[2]+' ('+parts[0]+' | '+parts[1]+')'
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

        distance = geodesic(coords_1, coords_2).kilometers

        # Create a folium map centered on the average coordinates
        map_center = [(coords_1[0] + coords_2[0]) / 2, (coords_1[1] + coords_2[1]) / 2]
        my_map = folium.Map(location=map_center, zoom_start=5)

        # Plot great circle line on the map
        folium.PolyLine([coords_1, coords_2], color='blue', weight=2.5, opacity=1).add_to(my_map)

        # Save the map to a file (you can customize the filename)
        map_filename = 'great_circle_map.html'
        my_map.save('templates/' + map_filename)

        return render_template('result.html', distance=distance, map_filename=map_filename)

@app.route('/static/<filename>')
def serve_static(filename):
    return send_file(os.path.join('templates', filename))

if __name__ == '__main__':
    app.run(debug=True)
