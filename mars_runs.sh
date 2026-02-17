# Classic
python ncdashboard_panel.py  test_data --regex "gom*.nc" --port 8053

# GOMb0.01
python ncdashboard_panel.py  /hycom/ftp/datasets/GOMb0.01/reanalysis/data/2024/027_archv.2024_245_18_3z.nc --port 8053

# GOMb0.04
python ncdashboard_panel.py  /hycom/ftp/datasets/GOMb0.04/reanalysis/data/2024/038_archv.2024_173_21_3z.nc --port 8053
python ncdashboard_panel.py  /hycom/ftp/datasets/GOMb0.04/reanalysis/data/2024/ --regex "038_archv.2024_173_21_*.nc" --port 8053
python ncdashboard_panel.py  /hycom/ftp/datasets/GOMb0.04/reanalysis/data/2024/ --regex "*_12_*.nc" --port 8053

nohup python ncdashboard_panel.py /hycom/ftp/datasets/GOMb0.04/reanalysis/data/2024/ --regex "*_12_*.nc" --port 8053 > ncdashboard.log 2>&1 &