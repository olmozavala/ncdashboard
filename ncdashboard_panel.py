"""NcDashboard Panel Options

Usage:
  ncdashboard_panel.py  <path> [--regex <regex>] [--state <state_file>] [--port=<port>] [--host=<host>]
  ncdashboard_panel.py  --state <state_file> [--port=<port>] [--host=<host>]
  ncdashboard_panel.py (-h | --help)
  ncdashboard_panel.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  <path>        Directory or path for NetCDF files.
  --regex <regex>  File pattern (e.g. "*.nc") when path is a directory.
  --state <state_file>  Load dashboard from saved state file (path/regex from file if path not given).
  --port=<port>  Port [default: 8050].
  --host=<host>  Host [default: 127.0.0.1].
"""
import io
import json
import panel as pn
from loguru import logger
from docopt import docopt
from model.dashboard import Dashboard
from model.state import load_state_file

import holoviews as hv
import geoviews as gv

# Initialize Panel extension using Bootstrap
pn.extension(design='bootstrap', browser_info=True)
hv.extension('bokeh')
gv.extension('bokeh')
# Suppress "not evenly sampled" warning for Image with irregular lat/lon
hv.config.image_rtol = 0.1

class NcDashboard:
    def __init__(self, file_paths, regex, initial_state=None):
        """
        file_paths: path to directory or file list.
        regex: file pattern when path is a directory.
        initial_state: optional state dict to restore (from --state file).
        """
        logger.info('Initializing new NcDashboard session...')
        
        # --- UI Components ---
        self.main_area = pn.FlexBox(align_content='start', justify_content='start')
        self.sidebar_area = pn.Column(sizing_mode='stretch_width')
        
        # Initialize the template
        self.template = pn.template.BootstrapTemplate(
            title='NcDashboard',
            sidebar=[self.sidebar_area],
            main=[self.main_area],
            header_background='#354869'
        )
        
        try:
            self.ncdash = Dashboard(file_paths, regex)
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            # Create a simple nice text saying that the files can't be found
            error_message = pn.Column(
                pn.pane.Markdown(f"""
                # 📂 Files Not Found
                
                We were unable to open the specified NetCDF files.
                
                **Location:** `{file_paths}`  
                **Pattern:** `{regex or '(None)'}`
                
                ### Tips:
                * Ensure the path is correct.
                * If pointing to a directory, use a pattern like `--regex "*.nc"`.
                * Verify that the files are valid NetCDF datasets.
                
                ---
                **Error Details:**  
                `{str(e)}`
                """, styles={
                    'padding': '30px', 
                    'background-color': '#fffafa', 
                    'border-radius': '15px', 
                    'border': '1px solid #ffcccc',
                    'box-shadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'color': '#721c24'
                }, sizing_mode='stretch_width'),
                max_width=800,
                align='center',
                margin=50
            )
            self.main_area.append(error_message)
            return

        # Build the initial menu
        self.init_menu()

        # Restore figures from saved state if provided
        if initial_state is not None:
            try:
                self.ncdash.apply_state(initial_state, self.main_area)
            except Exception as e:
                logger.exception(f"Failed to apply state: {e}")
                self.main_area.append(pn.pane.Markdown(f"**State restore error:** {e}", styles={'color': 'red'}))

    def init_menu(self):
        self.sidebar_area.clear()
        
        var_widgets = []
        for var_type in ["4D", "3D", "2D", "1D"]:
            fields = self.ncdash.get_field_names(var_type)
            if not fields:
                continue
            
            var_column = pn.Column(pn.pane.Markdown(f"### {var_type} Vars"))
            for name, field, dims in fields:
                # Create a button for each variable for one-click plotting
                # Using 'default' or 'light' for a clean look
                btn = pn.widgets.Button(name=f"{name} {dims}", sizing_mode='stretch_width')
                
                # Use a factory function to capture the scope correctly
                def make_plot_callback(f, vt):
                    return lambda e: self.plot_field(f, vt)
                
                btn.on_click(make_plot_callback(field, var_type))
                var_column.append(btn)
            var_widgets.append(var_column)

        close_all_btn = pn.widgets.Button(name="Close all", button_type='danger')
        close_all_btn.on_click(lambda e: self.main_area.clear())

        # Save State: download current dashboard state as JSON
        def state_download_callback():
            state = self.ncdash.get_state()
            return io.BytesIO(json.dumps(state, indent=2).encode("utf-8"))

        save_state_btn = pn.widgets.FileDownload(
            label="Save State",
            filename="ncdashboard_state.json",
            callback=state_download_callback,
            button_type="primary",
            sizing_mode='stretch_width'
        )

        # Load State: upload a JSON/YAML file to restore dashboard
        load_state_input = pn.widgets.FileInput(accept='.json,.yml,.yaml', name="")
        
        def on_load_state(event):
            if load_state_input.value:
                try:
                    content = load_state_input.value.decode('utf-8')
                    if load_state_input.filename.endswith('.json'):
                        state = json.loads(content)
                    else:
                        import yaml
                        state = yaml.safe_load(content)
                    
                    self.main_area.clear()
                    self.ncdash.apply_state(state, self.main_area)
                    logger.info(f"State loaded from {load_state_input.filename}")
                except Exception as e:
                    logger.exception(f"Failed to load state: {e}")
                    self.main_area.append(pn.pane.Markdown(f"**Load State Error:** {e}", styles={'color': 'red'}))

        load_state_input.param.watch(on_load_state, 'value')

        # Add items to sidebar in desired order
        # Options/Actions at the top
        self.sidebar_area.append(close_all_btn)
        self.sidebar_area.append(pn.pane.Markdown("### Save State"))
        self.sidebar_area.append(save_state_btn)
        self.sidebar_area.append(pn.pane.Markdown("### Load State"))
        self.sidebar_area.append(load_state_input)
        
        # Add variable buttons below
        for widget in var_widgets:
            self.sidebar_area.append(widget)

    def plot_field(self, field, var_type):
        from model.model_utils import PlotType 
        
        ptype = PlotType.TwoD
        if var_type == "3D": ptype = PlotType.ThreeD
        elif var_type == "4D": ptype = PlotType.FourD
        elif var_type == "1D": ptype = PlotType.OneD
        
        # create_default_figure appends to self.main_area automatically via layout_container
        self.ncdash.create_default_figure(field, ptype, layout_container=self.main_area)

if __name__ == "__main__":
    args = docopt(__doc__, version='NcDashboard Panel 0.0.1')
    state_file = args.get('--state')
    port = int(args['--port']) if args.get('--port') else 8050
    host = args.get('--host') or '127.0.0.1'

    if state_file:
        state = load_state_file(state_file)
        path = state.get('path', '')
        regex = state.get('regex', '')
        if not path:
            logger.error("State file has no 'path'; cannot start dashboard.")
            raise SystemExit(1)
        initial_state = state
    else:
        raw_path = args.get('<path>')
        path = raw_path if isinstance(raw_path, str) else ''
        if not path:
            logger.error("Provide <path> or use --state <state_file>.")
            raise SystemExit(1)
        regex = args.get('--regex') or ''
        initial_state = None

    # Pre-check if files exist to warn the user early
    import glob
    import os
    search_pattern = os.path.join(str(path), regex) if (path and regex) else path
    if search_pattern and not glob.glob(search_pattern):
        logger.warning(f"No files found matching: {search_pattern}")
        logger.warning("The dashboard will show an error message when accessed in the browser.")

    def make_app():
        return NcDashboard(path, regex or '', initial_state=initial_state).template

    ws_origin = [f"{host}:{port}", f"localhost:{port}", f"127.0.0.1:{port}"]
    logger.info(f"Starting NcDashboard server on http://{host}:{port}")
    pn.serve(make_app, port=port, address=host, show=False,
             websocket_origin=ws_origin, autoreload=True)
