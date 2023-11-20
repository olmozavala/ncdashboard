import dash_bootstrap_components as dbc
from dash import Patch, html, dcc

def get_animation_controls(node_id, all_anim_coords):
    anim_options = [
        dbc.Row(
            [
                dbc.Col(html.Div("Resolution:"), width=3),
                dbc.Col(
                    dbc.RadioItems(
                        id={"type": "resolution", "index": node_id},
                        options=[
                            {"label": "High", "value": f"{node_id}:high"},
                            {"label": "Medium", "value": f"{node_id}:medium"},
                            {"label": "Low", "value": f"{node_id}:low"},
                        ],
                        value=f"{node_id}:low",
                        inline=True,
                    ),
                    width=9,
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Button(
                        f"Animate {cur_coord}",
                        id={
                            "type": "animation",
                            "index": f"{node_id}:{cur_coord}",
                        },
                        size="sm",
                        className="me-1",
                        color="light",
                    )
                    for cur_coord in all_anim_coords
                ],
                width={"size": 8, "offset": 2},
            )
        ),
    ]

    return anim_options

def get_frame_controls(node_id, all_anim_coords):
    frame_controls = [
                # Add a div with the name of the field
                html.Div([f"{cur_coord}", 
                    dbc.ButtonGroup(
                    [
                        dbc.Button(html.I(className="bi bi-skip-backward"), color="light", id={"type":"first_frame", "index":f'{cur_coord}:{node_id}'}),
                        dbc.Button(html.I(className="bi bi-skip-start"),    color="light", id={"type":"prev_frame",  "index":f'{cur_coord}:{node_id}'}),
                        dbc.Button(html.I(className="bi bi-skip-end"),      color="light", id={"type":"next_frame",  "index":f'{cur_coord}:{node_id}'}),
                        dbc.Button(html.I(className="bi bi-skip-forward"),  color="light", id={"type":"last_frame",  "index":f'{cur_coord}:{node_id}'}),
                        ], size="sm",
                        ),
                ]) for cur_coord in all_anim_coords
            ]

    return frame_controls
