# ncdashboard
An Open Source project to generate dynamic visualizations of ocean and atmospheric data. 

# Install
```bash

conda install -c conda-forge dash
pip install dash-bootstrap-components
```

# Links
This is a list of important links for the project.


- [Plotly](https://dash.plot.ly/)
- [Core components](https://dash.plot.ly/dash-core-components)
- [HTML Components](https://dash.plot.ly/dash-html-components)

# Maps 
Difference between GeoMaps and MapboxMaps: https://plotly.com/python/mapbox-layers/

# Default `launch.json` for vscode 
```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Dash",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": ["run", "--no-debugger", "--no-reload", "--no-use-reloader"]
        }
    ]
}
```

# dashboard.py
This class will represent the main model of the dashboard. 
It will be responsible for holding the current configuration of the dashboard. 

Some of the information it will hold will be:
* Path and regex of the files loaded into the dashboard
* The tree object that represents the layout of the dashboard
* Data: the main xarray dataset that will be used to generate the plots and derived fields

Each node in the tree represent a specific visualization or plot. Each node will have the following attributes:
We are assuming all type of plots may be animated. We call this animation axis the 'time' axis. 

* Name of the plot/field
* ID (unique identifier used to create composite and derived fields)
* Childrens (we will have a )
* Type of plot/field (1D, 2D, 3D, 4D). 
     * 1D (Profiles): Line plot, bar plot, histogram, etc.
     * 2D (Transect): Raster, contour plot, streamline, vector (points, lines, polygons)
     * 3D (Classic 2D Map + Vertical Axes): Raster, contour plot, streamline, vector (points, lines, polygons)
     * Not for now 4D (Same as 3D but visualized in 3D): isosurface, volume rendering, etc.

* The data that will be used to generate the plot/field
     * type: (direct field (U), derived field (sqrt(U^2 + V^2)), composite field (U raster + SSH contour))
           * Direct field:
                * name of the field
           * derived field:
                * expression to calculate the derived field
           * composite field:
     * data: This is a self contained xarray dataset that will be used to generate the plot/field. 
             We should be able to generate this data from information of the other nodes in the tree (siblings and parent)


* The layout of the plot/field (e.g. size, position, etc.)
     * All types of plot
          * Bootstrap row and number of columns for the plot
          * Size of the plot
          * Speed, Number of frames, current frame
          * Title, subtitle, xaxis title, yaxis title, etc. 
     * 1D plot
     * 2D&3D plot
          * Colormap for the plot
     * 2D plot
     * 3D plot
          * Size of 'vertical' axes 
          * Current location of the 'vertical' axes
          * Will be good to be able to animate the 'vertical' axes + the 'time' axis
