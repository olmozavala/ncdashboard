# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from openai import OpenAI
from netrc import netrc

def format_list(data):
    if len(var_names) > 1:
        formatted_string = ', '.join(var_names[:-1]) + ' and ' + var_names[-1]
    elif var_names:  # If there's only one item in the list
        formatted_string = var_names[0]
    else:
        formatted_string = ''  # Handle empty list case
    return formatted_string


# %% Read Netcdf
file_name = "/unity/f1/ozavala/CODE/ncdashboard/test_data/gom_t007.nc"
# validate the file exists
print(f'File exisits: {os.path.exists(file_name)}')

data = xr.open_dataset(file_name, engine='netcdf4', decode_times=False)
print(data)

# %% Plot in the same figure u and v
fig, axs = plt.subplots(1, 2)
axs[0].imshow(np.flipud(data['water_u'].values[0, 0, :, :]))
axs[1].imshow(np.flipud(data['water_v'].values[0, 0, :, :]))
plt.show()

# %% Prompt generation
# Simulate user prompt
user_prompt = "Please generate the vorticity field"
# user_prompt = "Make a vertical transect of temperature at the middle of the Gulf of Mexico"
# Get some information from the dataset
# Variable names
var_names = list(data.data_vars)
print(var_names)

# %% For each variable make a dictionary that contains the shape, units, name and the name of its coordinates
vars_info = {}
for var in var_names:
    vars_info[var] = {'shape': data[var].shape,
                      'units': data[var].attrs['units'],
                      'coords': list(data[var].coords)}
print(vars_info)

# %% Make text from the dictionary of the form "Variable 'name' has shape (shape) and units (units) and coordinates (coords)"
vars_info_text = []
for var, info in vars_info.items():
    vars_info_text.append(f"Variable '{var}' has shape {info['shape']} and units '{info['units']}', coordinates '{info['coords']}'")
# Join the text by '.' and add a '.' at the end
vars_info_text = '. '.join(vars_info_text) + '.'
print(vars_info_text)

# %% Information that may come from ncdashboard
ncdashboard_info = ""

# %% Generate automatic prompt
final_prompt = f"""
You are an expert python software engineer. You have an xarray dataset with an object named ‘data’, it contains the
fields {format_list(var_names)}. {vars_info_text}. Please {user_prompt}. {ncdashboard_info} The answer must be in
python, the output must be stored in an object called output. Please restrict the solution to use only xarray and
numpy, libraries. Please provide ONLY the Python code as an answer, no import lines and no commented code.
If possible generate a variable for each intermediate computation."""
print(final_prompt)

# %% Synthetic LLM anwer
# Synthetic I get for this prompt from ChatGPT
use_chatgpt = False
# %% ======================================= Using real code from openAI ===========================
if use_chatgpt:
    netrc_obj = netrc()
    api_key = netrc_obj.authenticators("OPENAI")[2]
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": final_prompt 
            }
        ]
    )

    answers = completion.choices[0]
    code = answers.message.content.replace("python","").replace("```","")
else:
    code = """
dx = data['lon'].diff(dim='lon') * (np.pi/180) * 6371000 * np.cos(np.deg2rad(data['lat']))
dy = data['lat'].diff(dim='lat') * (np.pi/180) * 6371000

dudx = (data['water_u'].isel(time=0, depth=0).diff(dim='lon') / dx).fillna(0)
dvdy = (data['water_v'].isel(time=0, depth=0).diff(dim='lat') / dy).fillna(0)

vorticity = dvdy - dudx
output = vorticity
"""
print(code)

# %% Evaluate code (Here we need to do the agent part and reiterate until it works)
print(f"Code to be executed: \n {code}")
exec(code)
# Validate that 'output' object is defined and is of type xarray. Throw an error if it's not
assert 'output' in locals(), "output object is not defined"
assert isinstance(output, xr.DataArray), "output object is not of type xarray"
print(f"Shape of output: {output.shape}")

# %%  From here after some validation on the output object NcDashboard should be able to handle the rest
plt.imshow(np.flipud(output.values[:, :]))
plt.show()