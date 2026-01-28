"""NcDashboard Panel Options

Usage:
  ncdashboard_panel.py  <path>
  ncdashboard_panel.py  <path> --regex <regex>
  ncdashboard_panel.py  <path> --regex <regex> --port <port> --host <host>
  ncdashboard_panel.py (-h | --help)
  ncdashboard_panel.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  <path>  NetCDF file or regular expression to explore. 
"""
import panel as pn
from loguru import logger
from docopt import docopt
from model.dashboard import Dashboard

import holoviews as hv
import geoviews as gv

# Initialize Panel extension using Bootstrap
pn.extension(design='bootstrap', browser_info=True)
hv.extension('bokeh')
gv.extension('bokeh')

class NcDashboard:
    def __init__(self, file_paths, regex):
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

    def init_menu(self):
        # ... (Method logic remains the same)
        self.sidebar_area.clear()
        
        controls = []
        
        for var_type in ["4D", "3D", "2D", "1D"]:
            fields = self.ncdash.get_field_names(var_type)
            if not fields:
                continue
                
            options = {f"{name} {dims}": field for name, field, dims in fields}
            
            selector = pn.widgets.CheckBoxGroup(
                name=f"{var_type} Vars",
                options=options,
                inline=False 
            )
            controls.append((var_type, selector))
            self.sidebar_area.append(pn.Column(pn.pane.Markdown(f"### {var_type} Vars"), selector))

        plot_btn = pn.widgets.Button(name="Plot selected fields", button_type='success')
        
        def on_plot_click(event):
            try:
                for v_type, sel_widget in controls:
                    selected_vals = sel_widget.value
                    if selected_vals:
                        for field in selected_vals:
                            self.plot_field(field, v_type)
                for _, sel_widget in controls:
                    sel_widget.value = []
            except Exception as e:
                logger.exception(f"Error acting on plot click: {e}")
                self.main_area.append(pn.pane.Markdown(f"**Error**: {e}", styles={'color': 'red'}))

        plot_btn.on_click(on_plot_click)
        
        close_all_btn = pn.widgets.Button(name="Close all", button_type='danger')
        close_all_btn.on_click(lambda e: self.main_area.clear())

        self.sidebar_area.append(pn.Row(plot_btn, close_all_btn))

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
    path = args['<path>']
    regex = args['<regex>']
    port = int(args['<port>']) if args['<port>'] else 8050
    host = args['<host>'] or '127.0.0.1'
    
    # Pre-check if files exist to warn the user early
    import glob
    import os
    search_pattern = os.path.join(path, regex or '')
    if not glob.glob(search_pattern):
        logger.warning(f"No files found matching: {search_pattern}")
        logger.warning("The dashboard will show an error message when accessed in the browser.")

    # We pass a function to pn.serve to create a new NcDashboard per session
    def make_app():
        return NcDashboard(path, regex or '').template

    ws_origin = [f"{host}:{port}", f"localhost:{port}", f"127.0.0.1:{port}"]
    
    logger.info(f"Starting NcDashboard server on http://{host}:{port}")
    pn.serve(make_app, port=port, address=host, show=False, 
             websocket_origin=ws_origin, autoreload=True)
