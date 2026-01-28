# ncdashboard
An Open Source project to generate dynamic visualizations of ocean and atmospheric data. 

## Installation

Ensure you have access to the pre-configured `uv` environment.

1. Use the python executable from the `uv` environment to run the dashboard:
    ```bash
    /home/olmozavala/uv/envs/eoasweb/bin/python ncdashboard_panel.py path_to_file
    ```

## Running
To run the `ncdashboard.py` script, you will need to provide the path 
to the netCDF file or files you wish to visualize. For example, if you have 
a file called `test.nc` in the same directory as the `ncdashboard.py` script, you would run the following command:

```bash
python ncdashboard.py test.nc
```

If you have multiple files you can use regular expressions to select them. For example, if you have a directory with multiple files, you can select all the files with the `.nc` extension using the following command:

```bash
python ncdashboard.py path --regex "*.nc"
```

## Examples
This section contains examples of the visualizations that can be generated using the `ncdashboard.py` script with the example data provided in the `test_data` directory.

### Single netcdf file
To test using a single netcdf file in `test_data`, run the following command:

```bash
python ncdashboard.py test_data/gom_t007.nc
```

### Multiple netcdf files with regex
To test using multiple netcdf files in `test_data`, run the following command:

```bash
python ncdashboard.py test_data --regex "*.nc"
```

![Alt Text](figs/example.gif)

# Links
This is a list of important links for the project.


- [Plotly](https://dash.plot.ly/)
- [Core components](https://dash.plot.ly/dash-core-components)
- [HTML Components](https://dash.plot.ly/dash-html-components)