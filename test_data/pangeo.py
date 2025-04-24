# %% Visualize data from gom*.nc files
# %% Import libraries
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# %% Load data
df = ds = xr.open_mfdataset('gom*.nc', decode_times=False)
# %% Plot salinity water_temp, water_u and water_v in a 2x2 grid
fig, axs = plt.subplots(2, 2, figsize=(12, 12), subplot_kw={'projection': ccrs.PlateCarree()})
axs[0][0].set_title('Salinity')
axs[0][1].set_title('Water Temperature')
axs[1][0].set_title('Water U')
axs[1][1].set_title('Water V')
for i, var in enumerate(['salinity', 'water_temp', 'water_u', 'water_v']):
    df[var].isel(time=0, depth=0).plot(ax=axs.flatten()[i], transform=ccrs.PlateCarree(), cmap='viridis')
    axs.flatten()[i].add_feature(cfeature.LAND, color='k')
    axs.flatten()[i].coastlines()
plt.show()
