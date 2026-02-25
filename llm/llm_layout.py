import panel as pn
from loguru import logger
from .llm_client import get_llm_client
from .code_executor import run_with_retry
from model.model_utils import PlotType

class CustomAnalysisUI:
    """Handles the UI and execution for LLM-based custom analysis."""
    
    def __init__(self, ncdash, main_area):
        self.ncdash = ncdash
        self.main_area = main_area
        self.modal = None
        self.status = None

    def open_dialog(self):
        """Open dialog for LLM-based custom analysis."""
        
        # Close any existing dialog first
        if self.modal is not None:
            if self.modal in self.main_area.objects:
                self.main_area.remove(self.modal)
            self.modal = None
        
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
            height=70,
            sizing_mode='stretch_width'
        )
        
        # Status display
        self.status = pn.pane.Markdown("", sizing_mode='stretch_width', margin=0)
        
        # Generate button
        generate_btn = pn.widgets.Button(name="🚀 Generate", button_type="success", width=120)
        cancel_btn = pn.widgets.Button(name="✕ Close", button_type="danger", width=100)
        
        def on_cancel(event=None):
            if self.modal is not None and self.modal in self.main_area.objects:
                self.main_area.remove(self.modal)
            self.modal = None
        
        def on_generate(event):
            provider = provider_select.value
            source_id = source_select.value
            request = request_input.value.strip()
            
            if not request:
                self.status.object = "⚠️ **Please enter an analysis request.**"
                return
            
            # Disable button and show progress
            generate_btn.disabled = True
            generate_btn.name = "⏳ Generating..."
            self.status.object = "🔄 Generating code with LLM..."
            
            # Run analysis (this will update status)
            try:
                self.run_analysis(provider, source_id, request)
                # Close modal on success
                on_cancel()
            except Exception as e:
                self.status.object = f"❌ **Error:** {str(e)}"
                generate_btn.disabled = False
                generate_btn.name = "🚀 Generate"
        
        cancel_btn.on_click(on_cancel)
        generate_btn.on_click(on_generate)
        
        # Create dialog as a Card widget
        self.modal = pn.Card(
            pn.Column(
                pn.pane.Markdown(
                    "Use AI to generate new datasets from natural language. "
                    "The LLM generates Python code to transform your xarray data.",
                    styles={'color': '#666'},
                    margin=(5, 10, 0, 10)
                ),
                pn.Row(provider_select, source_select, margin=(0, 10, 0, 10)),
                pn.Column(request_input, margin=(0, 10, 0, 10), sizing_mode='stretch_width'),
                self.status,
                pn.Row(generate_btn, cancel_btn, margin=(0, 10, 10, 10)),
                sizing_mode='stretch_width'
            ),
            title="🤖 Custom Analysis",
            sizing_mode='stretch_width',
            max_width=550,
            margin=10,
            styles={
                'background': '#f8f9fa',
                'border': '2px solid #4CAF50',
                'flex': '1 1 100%'
            }
        )
        
        # Insert at the beginning of main_area
        self.main_area.insert(0, self.modal)

    def _get_source_node_options(self) -> dict:
        """Get available source nodes for analysis."""
        options = {"Root Dataset": "root"}
        
        # Add open figures
        for child in self.ncdash.tree_root.get_children():
            node_id = child.get_id()
            field_name = child.get_field_name() or node_id
            options[f"{field_name} ({node_id})"] = node_id
        
        return options

    def run_analysis(self, provider: str, source_id: str, request: str):
        """Run LLM-based custom analysis."""
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
        if self.status:
            self.status.object = f"🔌 Connecting to {provider}..."
        
        # Get LLM client
        try:
            llm_client = get_llm_client(provider)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize {provider}: {e}")
        
        # Check availability
        if not llm_client.is_available():
            raise ConnectionError(f"{provider} is not available. Check your configuration.")
        
        if self.status:
            self.status.object = "🧠 Generating and executing code..."
        
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
        self.ncdash.create_figure_from_dataarray(
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
                    'border-radius': '4px',
                    'flex': '1 1 100%'
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
