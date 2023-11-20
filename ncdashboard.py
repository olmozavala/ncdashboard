"""NcDashboard Options

Usage:
  ncdashboard.py  <path>
  ncdashboard.py  <path> --regex <regex>
  ncdashboard.py (-h | --help)
  ncdashboard.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  <path>  NetCDF file or regular expression to explore. 
"""
import logging
import glob
from docopt import docopt
import dash_bootstrap_components as dbc

from controller import NcDashboard

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# %%

if __name__ == "__main__":
    args = docopt(__doc__, version='NcDashboard 0.0.1')
    print(args)
    path = args['<path>']
    regex = args['<regex>']

    # https://dash.plotly.com/sharing-data-between-callbacks
    if regex:
        ncdashboard = NcDashboard(path, regex)
    else:
        ncdashboard = NcDashboard(path, '')

    ncdashboard.start()