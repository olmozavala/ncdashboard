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

# Initialize Panel extension
pn.extension(notifications=True)
hv.extension('bokeh')
gv.extension('bokeh')
# Remove logos from plots
hv.plotting.bokeh.ElementPlot.toolbar_logo = None
hv.config.logo = False
# Suppress "not evenly sampled" warning
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
        
        # Custom Analysis modal components
        self.analysis_modal = None
        self.analysis_status = None
        
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
        
        button_style = """
        :host(.bk-btn) {
            font-size: 12px;
            padding: 4px 8px;
            min-height: 32px;
        }
        """
        
        var_widgets = []
        for var_type in ["4D", "3D", "2D", "1D"]:
            fields = self.ncdash.get_field_names(var_type)
            if not fields:
                continue
            
            var_column = pn.Column(pn.pane.Markdown(f"### {var_type} Vars"))
            for name, field, dims in fields:
                # Create a button for each variable for one-click plotting
                btn = pn.widgets.Button(
                    name=f"{name} {dims}", 
                    sizing_mode='stretch_width',
                    stylesheets=[button_style]
                )
                
                # Use a factory function to capture the scope correctly
                def make_plot_callback(f, vt):
                    return lambda e: self.plot_field(f, vt)
                
                btn.on_click(make_plot_callback(field, var_type))
                var_column.append(btn)
            var_widgets.append(var_column)

        close_all_btn = pn.widgets.Button(
            name="Close all", 
            button_type='danger',
            sizing_mode='stretch_width',
            stylesheets=[button_style]
        )
        close_all_btn.on_click(lambda e: self.main_area.clear())

        # Custom Analysis button (LLM-powered)
        custom_analysis_btn = pn.widgets.Button(
            name="🤖 Custom Analysis",
            button_type='success', 
            sizing_mode='stretch_width',
            stylesheets=[button_style]
        )
        custom_analysis_btn.on_click(lambda e: self.open_custom_analysis_dialog())

        # Save State: download current dashboard state as JSON
        def state_download_callback():
            state = self.ncdash.get_state()
            return io.BytesIO(json.dumps(state, indent=2).encode("utf-8"))

        save_state_btn = pn.widgets.FileDownload(
            label="Save State",
            filename="ncdashboard_state.json",
            callback=state_download_callback,
            button_type="primary",
            sizing_mode='stretch_width',
            stylesheets=[button_style]
        )

        # Load State: upload a JSON/YAML file to restore dashboard
        load_state_input = pn.widgets.FileInput(
            accept='.json,.yml,.yaml', 
            name="", 
            sizing_mode='stretch_width'
        )
        
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
        # Actions at the top: Custom Analysis, Save, Close All, Load
        self.sidebar_area.append(custom_analysis_btn)
        self.sidebar_area.append(save_state_btn)
        self.sidebar_area.append(close_all_btn)
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

    def open_custom_analysis_dialog(self):
        """Open dialog for LLM-based custom analysis."""
        
        # Close any existing dialog first
        if self.analysis_modal is not None:
            if self.analysis_modal in self.main_area.objects:
                self.main_area.remove(self.analysis_modal)
            self.analysis_modal = None
        
        # Get available source nodes (root + open figures)
        source_options = self._get_source_node_options()
        
        # Get LLM config for defaults
        from llm.llm_client import load_llm_config
        llm_config = load_llm_config()
        default_provider = llm_config.get("default_provider", "ollama")
        available_providers = list(llm_config.get("providers", {}).keys())
        if not available_providers:
            available_providers = ["ollama", "openai", "gemini", "anthropic"]
        
        # LLM Provider selector
        provider_select = pn.widgets.Select(
            name="LLM Provider",
            options=available_providers,
            value=default_provider,
            width=180
        )
        
        # Source node selector  
        source_select = pn.widgets.Select(
            name="Source Data",
            options=source_options,
            value="root",
            width=280
        )
        
        # Request text input
        request_input = pn.widgets.TextAreaInput(
            name="Analysis Request",
            placeholder="e.g., 'Calculate the mean along the time dimension' or 'Convert temperature to Celsius'",
            height=80,
            sizing_mode='stretch_width'
        )
        
        # Status display
        status_pane = pn.pane.Markdown("", sizing_mode='stretch_width')
        self.analysis_status = status_pane
        
        # Generate button
        generate_btn = pn.widgets.Button(name="🚀 Generate", button_type="primary", width=120)
        cancel_btn = pn.widgets.Button(name="✕ Close", button_type="light", width=100)
        
        def on_cancel(event=None):
            if self.analysis_modal is not None and self.analysis_modal in self.main_area.objects:
                self.main_area.remove(self.analysis_modal)
            self.analysis_modal = None
        
        def on_generate(event):
            provider = provider_select.value
            source_id = source_select.value
            request = request_input.value.strip()
            
            if not request:
                self.analysis_status.object = "⚠️ **Please enter an analysis request.**"
                return
            
            # Disable button and show progress
            generate_btn.disabled = True
            generate_btn.name = "⏳ Generating..."
            self.analysis_status.object = "🔄 Generating code with LLM..."
            
            # Run analysis (this will update status)
            try:
                self.run_custom_analysis(provider, source_id, request)
                # Close modal on success
                on_cancel()
            except Exception as e:
                self.analysis_status.object = f"❌ **Error:** {str(e)}"
                generate_btn.disabled = False
                generate_btn.name = "🚀 Generate"
        
        cancel_btn.on_click(on_cancel)
        generate_btn.on_click(on_generate)
        
        # Create dialog as a Card widget
        dialog_card = pn.Card(
            pn.pane.Markdown(
                "Use AI to generate new datasets from natural language. "
                "The LLM generates Python code to transform your xarray data.",
                styles={'color': '#666', 'margin-bottom': '10px'}
            ),
            pn.Row(provider_select, source_select),
            request_input,
            status_pane,
            pn.Row(generate_btn, cancel_btn),
            title="🤖 Custom Analysis",
            sizing_mode='stretch_width',
            max_width=550,
            margin=10,
            styles={
                'background': '#f8f9fa',
                'border': '2px solid #4CAF50'
            }
        )
        
        self.analysis_modal = dialog_card
        
        # Insert at the beginning of main_area
        self.main_area.insert(0, dialog_card)
    
    def _get_source_node_options(self) -> dict:
        """Get available source nodes for analysis."""
        options = {"Root Dataset": "root"}
        
        # Add open figures
        for child in self.ncdash.tree_root.get_children():
            node_id = child.get_id()
            field_name = child.get_field_name() or node_id
            options[f"{field_name} ({node_id})"] = node_id
        
        return options
    
    def run_custom_analysis(self, provider: str, source_id: str, request: str):
        """
        Run LLM-based custom analysis.
        
        Args:
            provider: LLM provider name ("ollama", "openai", "gemini")
            source_id: ID of source node ("root" or figure ID)
            request: Natural language analysis request
        """
        from llm import get_llm_client, run_with_retry
        from model.model_utils import PlotType
        
        logger.info(f"Running custom analysis: provider={provider}, source={source_id}, request='{request}'")
        
        # Get source data
        if source_id == "root":
            data = self.ncdash.data
            parent_node = self.ncdash.tree_root
        else:
            node = self.ncdash.tree_root.locate(source_id)
            if node is None:
                raise ValueError(f"Source node '{source_id}' not found")
            data = node.get_data()
            parent_node = node
        
        # Update status
        if self.analysis_status:
            self.analysis_status.object = f"🔌 Connecting to {provider}..."
        
        # Get LLM client
        try:
            llm_client = get_llm_client(provider)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize {provider}: {e}")
        
        # Check availability
        if not llm_client.is_available():
            raise ConnectionError(f"{provider} is not available. Check your configuration.")
        
        if self.analysis_status:
            self.analysis_status.object = "🧠 Generating and executing code..."
        
        # Run with retry (up to 3 attempts)
        result = run_with_retry(llm_client, data, request, max_attempts=3)
        
        if not result.success:
            raise RuntimeError(f"Analysis failed after 3 attempts: {result.error_message}")
        
        # Success! Create figure from output
        output_data = result.output
        logger.info(f"Analysis successful! Output shape: {output_data.shape}")
        
        # Determine plot type based on dimensions
        ndims = len(output_data.shape)
        if ndims == 1:
            plot_type = PlotType.OneD
        elif ndims == 2:
            plot_type = PlotType.TwoD
        elif ndims == 3:
            plot_type = PlotType.ThreeD
        else:
            plot_type = PlotType.FourD
        
        # Create figure
        new_fig_node = self.ncdash.create_figure_from_dataarray(
            output_data,
            parent_node=parent_node,
            title=f"LLM: {request[:50]}...",
            layout_container=self.main_area
        )
        
        # Show summary in a nice notification or small pane
        if result.summary:
            summary_md = pn.pane.Markdown(f"""
            ### 🤖 Analysis Summary
            {result.summary}
            
            *Code generated for: "{request}"*
            """, margin=(0, 10, 0, 0), sizing_mode='stretch_width')
            
            close_summary_btn = pn.widgets.Button(
                name="✕", 
                width=30, height=30, 
                align='start',
                stylesheets=[""":host .bk-btn { 
                    background-color: #cbd5e0 !important; 
                    color: #4a5568 !important; 
                    border-radius: 50%; 
                    font-weight: bold; 
                    border: none;
                }
                :host .bk-btn:hover {
                    background-color: #a0aec0 !important;
                }"""]
            )
            
            summary_container = pn.Row(
                summary_md,
                close_summary_btn,
                styles={
                    'background': '#e8f5e9', 
                    'padding': '15px', 
                    'border-left': '5px solid #4caf50',
                    'margin': '10px',
                    'border-radius': '4px'
                },
                sizing_mode='stretch_width'
            )
            
            def on_close_summary(event):
                try:
                    self.main_area.remove(summary_container)
                except ValueError:
                    pass
            
            close_summary_btn.on_click(on_close_summary)
            
            # Add to main area at the top
            self.main_area.insert(0, summary_container)
            
            # Also show as notification
            pn.state.notifications.success("Analysis complete!", duration=3000)
            
        logger.info("Custom analysis figure created successfully")


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
