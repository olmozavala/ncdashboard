import cmocean
import numpy as np

def select_colormap(field_name):
    '''
    Based on the name if the field it chooses a colormap from cmocean
    Args:
        field_name:

    Returns:

    '''
    field_name = field_name.lower()
    cmap = cmocean.cm.gray_r
    if np.any([field_name.find(x) != -1 for x in ('ssh', 'srfhgt', 'adt','surf_el')]):
        # cmaps_fields.append(cmocean.cm.deep_r)
        cmap = cmocean.cm.curl
    elif np.any([field_name.find(x) != -1 for x in ('temp', 'sst', 'temperature')]):
        cmap = cmocean.cm.thermal
    elif np.any([field_name.find(x) != -1 for x in ('vorticity', 'vort')]):
        cmap = cmocean.cm.curl
    elif np.any([field_name.find(x) != -1 for x in ('salin', 'sss', 'sal')]):
        cmap = cmocean.cm.haline
    elif np.any([field_name.find(x) != -1 for x in ('chlor-a', 'chlora', 'dchl', 'nchl')]):
        cmap = cmocean.cm.algae
    elif field_name.find('error') != -1:
        cmap = cmocean.cm.diff
    elif field_name.find('binary') != -1:
        cmap = cmocean.cm.oxy
    elif np.any([field_name.find(x) != -1 for x in ('u_', 'v_', 'u-vel.', 'v-vel.','velocity')]):
        cmap = cmocean.cm.speed

    return cmocean_to_plotly(cmap, 256)

def cmocean_to_plotly(cmap, pl_entries):
    '''
    This function converts a cmocean colormap to a plotly compatible colormap
    '''
    h = 1.0/(pl_entries-1)
    pl_colorscale = []
    
    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])
        
    return pl_colorscale


def get_buttons_config():
    def_config = dict(
                modeBarButtonsToRemove=['zoom2d','zoomOut2d','zoomIn2d'],
                modeBarButtonsToAdd=['drawline', 'drawcircle', 'lasso2d', 'select2d'],
                scrollZoom=True,
                displayModeBar= True,
                displaylogo=False,
            )
    return def_config


def get_def_slider(prefix_name, suffix, n_steps):
    slider = {"active": 0,
                "yanchor": "top", # top --> bellow figure bottom --> bottom left corner (inside image)
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": f"{prefix_name.capitalize()}:",
                    "suffix": f" {suffix}",
                    "visible": True,
                    "xanchor": "left"
                },
                "transition": {"duration": 10, "easing": "cubic-in-out"},
                "len": 0.5, # (from 0 to 1) 0.5 --> slider is half the width of the figure
                "x": 0, # 1 moves one figure with to the righ
                "y": 0, # 1 moves one figure with to the top
                "steps":[ {'args':[ 
                                    [f'{prefix_name}_{c_time}'], 
                                    { 'frame':{"duration": 10, "redraw": True},
                                    'mode':"immediate"}
                                    ],
                        'label':str(c_time),
                        'method':"animate",
                        } for c_time in range(n_steps)],
                    }
    return slider

def get_update_buttons(dim_names, n_steps):
    buttons = dict(
                    type="buttons",
                    buttons=
                        [dict(label=f"Play {dim_name}", method="animate", 
                            args=[[f'{dim_name}_{c_time}' for c_time in range(n_steps[i])], {
                                    "frame": {"duration": 200, "redraw": True},
                                    "fromcurrent": True,
                                    }]) for i, dim_name in enumerate(dim_names)] +
                        [
                        dict(label="Pause", method="animate", 
                            args=[[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate"}]
                                ),
                        ]
                )
    return buttons