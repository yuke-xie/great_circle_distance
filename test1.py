import plotly.graph_objects as go
import numpy as np

data=go.Scattergeo(
    lat = [40.7127, 51.5072],
    lon = [-74.0059, 0.1275],
    mode = 'lines',
    line = dict(width = 2, color = 'blue'),
)

fig = go.Figure(data)

# Set the layout to a 3D globe
fig.update_geos(
  showland = True,
  showcountries = True,
  showocean = True,
  countrywidth = 0.5,
  landcolor = 'rgb(230, 145, 56)',
  lakecolor = 'rgb(0, 255, 255)',
  oceancolor = 'rgb(0, 255, 255)',
  projection = dict(
      type = 'orthographic',
      rotation = dict(
          lon = -100,
          lat = 40,
          roll = 0
      )
  ),
)

fig.update_layout(margin ={'l':0,'t':0,'b':0,'r':0},
                  mapbox = {
                      'center': {'lon': 139, 'lat': 36.5},
                      'style': "stamen-terrain",
                      'zoom': 4.5},
                  width=1600,
                  height=900,)

# Save the plot to test.html
fig.write_html("test.html")
