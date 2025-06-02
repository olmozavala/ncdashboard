import cmocean
import numpy as np

def select_colormap(field_name):
    '''
    Based on the name if the field it chooses a colormap from cmocean
    Args:
        field_name:

    Returns:

    '''
    field_name = field_name.lower()
    cmap = getattr(cmocean.cm, 'gray_r')
    if any(field_name.find(x) != -1 for x in ('ssh', 'srfhgt', 'adt','surf_el')):
        cmap = getattr(cmocean.cm, 'curl')
    elif any(field_name.find(x) != -1 for x in ('temp', 'sst', 'temperature','t2m')):
        cmap = getattr(cmocean.cm, 'thermal')
    elif any(field_name.find(x) != -1 for x in ('vorticity', 'vort')):
        cmap = getattr(cmocean.cm, 'curl')
    elif any(field_name.find(x) != -1 for x in ('salin', 'sss', 'sal')):
        cmap = getattr(cmocean.cm, 'haline')
    elif any(field_name.find(x) != -1 for x in ('chlor-a', 'chlora', 'dchl', 'nchl')):
        cmap = getattr(cmocean.cm, 'algae')
    elif 'error' in field_name:
        cmap = getattr(cmocean.cm, 'diff')
    elif 'binary' in field_name:
        cmap = getattr(cmocean.cm, 'oxy')
    elif any(field_name.find(x) != -1 for x in ('u10', 'v10', 'u_', 'v_', 'u-vel.', 'v-vel.','velocity')):
        cmap = getattr(cmocean.cm, 'speed')

    return cmocean_to_plotly(cmap, 256)

def cmocean_to_plotly(cmap, pl_entries):
    '''
    This function converts a cmocean colormap to a plotly compatible colormap
    '''
    h = 1.0/(pl_entries-1)
    pl_colorscale = []
    
    for k in range(pl_entries):
        rgb_tuple = tuple(int(x) for x in np.array(cmap(k*h)[:3])*255)
        pl_colorscale.append([k*h, f'rgb{rgb_tuple}'])
        
    return pl_colorscale
