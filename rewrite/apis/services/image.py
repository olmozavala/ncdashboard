import os
import xarray as xr
import plotly.graph_objects as go
from utils.constants import DATA_DIR

# TODO: remove the variable parameter default value
def generate_image(dataset, time_index, depth_index, variable = "water_u", data = None):
    print(dataset, time_index, depth_index, variable)
    data = xr.open_dataset(os.path.join(DATA_DIR, dataset), decode_times=False) if data is None else data
    z_data = data[variable][time_index, depth_index, :, :]
    
    lats = data["lat"]
    lons = data["lon"]

    fig = go.Figure(
        data=[go.Heatmap(
            z=z_data, 
            x=lons.values,  # Longitude on x-axis
            y=lats.values,  # Latitude on y-axis
            colorscale='Viridis',
            showscale=True,
        )],
        layout=go.Layout(
            title="Hycom GOM",
            xaxis_title="Longitude",
            yaxis_title="Latitude",
        )
    )
    
    

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )

    fig.update_traces(showscale=False)

    image_data = fig.to_image(format="jpeg")

    return image_data
