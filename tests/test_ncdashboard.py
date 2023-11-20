import pytest
from controller import NcDashboard
from ncdashboard import load_data, create_dashboard

def test_load_data():
    path = "../test_data/"

    ncdashboard = NcDashboard(path, '')
    # assert that no exceptions are raised