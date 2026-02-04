# LLM Workflow: From Request to Figure

This document describes the sequence of events and the code path taken when a user performs a **Custom Analysis** using the LLM-powered feature in NcDashboard.

## 1. UI Layer: The User Trigger
- **File**: `ncdashboard_panel.py`
- **Class**: `NcDashboard`
- **Sequence**:
    1. User clicks the **"🤖 Custom Analysis"** button in the sidebar.
    2. `open_custom_analysis_dialog()` creates a Panel `Card` modal.
    3. User selects a provider (Ollama, OpenAI, Gemini), source data, and enters a request.
    4. User clicks **"🚀 Generate"**, which triggers the `on_generate` callback.
    5. `on_generate` calls `self.run_custom_analysis(provider, source_id, request)`.

## 2. Orchestration Layer: run_custom_analysis
- **File**: `ncdashboard_panel.py`
- **Method**: `NcDashboard.run_custom_analysis`
- **Sequence**:
    1. Locates the source data (either the `root` dataset or a specific node's data).
    2. Initializes the LLM client using `get_llm_client(provider)` from the `llm` module.
    3. Calls `run_with_retry(llm_client, data, request, max_attempts=3)`.

## 3. LLM Logic: Generating and Executing Code
- **File**: `llm/code_executor.py`
- **Function**: `run_with_retry`
- **Sequence**:
    1. **Prompt Building**: `PromptBuilder` (`llm/prompt_builder.py`) extracts metadata from the `xarray` object (variables, coordinates, shapes) and formats it into a prompt using templates in `llm/prompts/base.py`.
    2. **LLM Generation**: The `llm_client` sends the prompt to the selected provider and returns a raw Python code string.
    3. **Execution**: `CodeExecutor.execute()` runs the code in a "sandbox":
        - It uses `exec()` with a restricted dictionary of globals (only `np`, `xr`, and the `data` object are allowed).
        - It strips imports and checks that the code defines an `output` variable of type `xr.DataArray`.
    4. **Error Correction**: If execution fails (e.g., SyntaxError, ValueError), a new prompt is built containing the error message and the failed code. This is sent back to the LLM for a fix (up to 3 attempts).

## 4. Model Layer: Creating the Figure
- **File**: `model/dashboard.py`
- **Method**: `Dashboard.create_figure_from_dataarray`
- **Sequence**:
    1. Receives the `xr.DataArray` named `output` from the LLM execution.
    2. Determines the dimensionality of the data (1D, 2D, 3D, or 4D).
    3. Creates the appropriate node type (e.g., `TwoDNode`, `ThreeDNode`).
    4. Wraps the node in a `FigureLayout` object.
    5. Appends the layout to the `main_area` (Panel FlexBox).

## 5. View Layer: Rendering
- **File**: `ncdashboard_panel.py` / `model/dashboard.py`
- **Sequence**:
    1. Because the `main_area` is a Panel component already displayed in the browser, adding the new figure layout to it causes a reactive update.
    2. The browser renders the new Bokeh/HoloViews plot immediately.

---

### Key Classes & Files Summary

| Component | File | Responsibility |
| :--- | :--- | :--- |
| **UI** | `ncdashboard_panel.py` | Dialog management and status updates. |
| **Orchestrator** | `llm/code_executor.py` | Implementation of the `run_with_retry` loop. |
| **Logic** | `llm/prompt_builder.py` | Metadata extraction and prompt formatting. |
| **Sandbox** | `llm/code_executor.py` | Secure execution of LLM-generated Python code. |
| **Client** | `llm/llm_client.py` | Communication with OpenAI, Gemini, or Ollama. |
| **Model** | `model/dashboard.py` | Turning the resulting `xarray` object into a dashboard figure. |
