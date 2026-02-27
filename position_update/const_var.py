# 维度
LATITUDE_KEY = 'lat'
# 经度
LONGITUDE_KEY = 'lon'
HEIGHT_KEY = 'hei'
# 卫星位置更新的时间间隔
UPDATE_INTERVAL = 10
# LIGHT_SPEED
LIGHT_SPEED = 300000
R_EARTH = 6371000

# DELAY BANDWIDTH LOSS
NETWORK_DELAY = 15  # unit ms, 150 means 150ms
NETWORK_BANDWIDTH = "2Mbps"   # unis kbytes/s must integer, 100 means 100kB/s
NETWORK_LOSS = "0%"  # percent 0 means 0%

# SAA (South Atlantic Anomaly) region
SAA_ENABLED = True
SAA_LAT_RANGE = (-50, 0)   # latitude range in degrees
SAA_LON_RANGE = (-80, 20)  # longitude range in degrees
SAA_NETWORK_LOSS = "2%"
SAA_NETWORK_BANDWIDTH = "1Mbps"
