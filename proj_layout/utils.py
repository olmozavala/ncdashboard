import cmocean
import numpy as np

def select_colormap(field_name):
    '''
    Based on the name if the field it chooses a colormap from cmocean.
    Returns the colormap object directly, compatible with HoloViews/Matplotlib.
    '''
    field_name = field_name.lower()
    cmap = cmocean.cm.gray_r
    if np.any([field_name.find(x) != -1 for x in ('ssh', 'srfhgt', 'adt','surf_el')]):
        cmap = cmocean.cm.curl
    elif np.any([field_name.find(x) != -1 for x in ('temp', 'sst', 'temperature','t2m')]):
        cmap = cmocean.cm.thermal
    elif np.any([field_name.find(x) != -1 for x in ('vorticity', 'vort')]):
        cmap = cmocean.cm.curl
    elif np.any([field_name.find(x) != -1 for x in ('salin', 'sss', 'sal')]):
        cmap = cmocean.cm.haline
    elif np.any([field_name.find(x) != -1 for x in ('chlor-a', 'chlora', 'dchl', 'nchl')]):
        cmap = cmocean.cm.algae
    elif field_name.find('error') != -1:
        cmap = cmocean.cm.diff
    elif field_name.find('binary') != -1:
        cmap = cmocean.cm.oxy
    elif np.any([field_name.find(x) != -1 for x in ('u10', 'v10', 'u_', 'v_', 'u-vel.', 'v-vel.','velocity')]):
        cmap = cmocean.cm.speed

    return cmap