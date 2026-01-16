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
pn.extension(design='bootstrap')
hv.extension('bokeh')
gv.extension('bokeh')

class NcDashboard:
    def __init__(self, file_paths, regex, host='127.0.0.1', port=8050):
        self.host = host
        self.port = port
        
        logger.info('Starting NcDashboard (Panel)...')
        self.ncdash = Dashboard(file_paths, regex)
        
        # --- UI Components ---
        # Use FlexBox for wrapping content (approx 2 columns)
        self.main_area = pn.FlexBox(align_content='start', justify_content='start')
        self.sidebar_area = pn.Column(sizing_mode='stretch_width')
        
        # Initialize the template
        self.template = pn.template.BootstrapTemplate(
            title='NcDashboard',
            sidebar=[self.sidebar_area],
            main=[self.main_area],
            header_background='#354869' # Example color
        )
        
        # Build the initial menu
        self.init_menu()

    def start(self):
        # Serve the app
        # Allow websocket origin for both localhost and 127.0.0.1 to avoid 403 errors
        ws_origin = [f"{self.host}:{self.port}", f"localhost:{self.port}", f"127.0.0.1:{self.port}"]
        pn.serve(self.template, port=self.port, address=self.host, show=False, websocket_origin=ws_origin)

    def init_menu(self):
        """
        Creates the selection menu for 1D, 2D, 3D, 4D variables.
        """
        self.sidebar_area.clear()
        
        controls = []
        
        for var_type in ["4D", "3D", "2D", "1D"]:
            fields = self.ncdash.get_field_names(var_type)
            if not fields:
                continue
                
            # fields is list of (name, field, dims)
            options = {f"{name} {dims}": field for name, field, dims in fields}
            
            # Using CheckBoxGroup as requested
            selector = pn.widgets.CheckBoxGroup(
                name=f"{var_type} Vars",
                options=options,
                inline=False # Vertical list
            )
            # Store the selector
            controls.append((var_type, selector))
            
            # wrap in a card or column with title
            self.sidebar_area.append(pn.Column(pn.pane.Markdown(f"### {var_type} Vars"), selector))

        # Plot Button
        plot_btn = pn.widgets.Button(name="Plot selected fields", button_type='success')
        
        def on_plot_click(event):
            try:
                # Aggregate all selected fields
                for v_type, sel_widget in controls:
                    selected_vals = sel_widget.value
                    if selected_vals:
                        for field in selected_vals:
                            # Create figure for each selected field
                            self.plot_field(field, v_type)
                
                # Uncheck all boxes after plotting
                for _, sel_widget in controls:
                    sel_widget.value = []
            except Exception as e:
                logger.exception(f"Error acting on plot click: {e}")
                # Show error in UI
                self.main_area.append(pn.pane.Markdown(f"**Error**: {e}", styles={'color': 'red'}))

        plot_btn.on_click(on_plot_click)
        
        close_all_btn = pn.widgets.Button(name="Close all", button_type='danger')
        close_all_btn.on_click(lambda e: self.main_area.clear())

        self.sidebar_area.append(pn.Row(plot_btn, close_all_btn))

    def plot_field(self, field, var_type):
        """
        Calls the model to create a figure/pane for the field and adds it to the main area.
        """
        from model.model_utils import PlotType 
        
        ptype = PlotType.TwoD
        if var_type == "3D": ptype = PlotType.ThreeD
        elif var_type == "4D": ptype = PlotType.FourD
        elif var_type == "1D": ptype = PlotType.OneD
        
        # Create default figure returns a Panel object (Row/Col/Card)
        # Pass self.main_area so the figure knows where to add drill-down plots or remove itself
        fig_pane = self.ncdash.create_default_figure(field, ptype, layout_container=self.main_area)
        self.main_area.append(fig_pane)

if __name__ == "__main__":
    args = docopt(__doc__, version='NcDashboard Panel 0.0.1')
    path = args['<path>']
    regex = args['<regex>']
    port = args['<port>']
    host = args['<host>']
    
    if port:
        port = int(port)
    else:
        port = 8050

    if not host:
        host = '127.0.0.1'

    ncdashboard = NcDashboard(path, regex or '', host=host, port=port)
    ncdashboard.start()
