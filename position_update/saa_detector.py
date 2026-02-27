"""
SAA (South Atlantic Anomaly) detector for satellite emulator.
ephem returns lat/lon in radians; SAA region is defined in degrees.
"""
import math
from datetime import datetime, timedelta

from satellite_emulator.position_update import const_var as cv

try:
    import ephem
except ImportError:
    ephem = None


def _rad_to_deg(rad: float) -> float:
    return math.degrees(rad)


def is_in_saa(lat: float, lon: float) -> bool:
    """
    Check if (lat, lon) is inside SAA rectangular region.
    :param lat: latitude in radians (from ephem) or degrees
    :param lon: longitude in radians (from ephem) or degrees
    :return: True if inside SAA region
    """
    lat_deg = _rad_to_deg(lat) if abs(lat) <= math.pi else lat
    lon_deg = _rad_to_deg(lon) if abs(lon) <= math.pi else lon

    lat_min, lat_max = cv.SAA_LAT_RANGE
    lon_min, lon_max = cv.SAA_LON_RANGE

    return lat_min <= lat_deg <= lat_max and lon_min <= lon_deg <= lon_max


def get_time_to_saa(node, now: datetime, window_sec: float = 10) -> int:
    """
    Predict seconds until node enters SAA within window_sec.
    :param node: SatelliteNode with get_next_position(time_now)
    :param now: current time
    :param window_sec: lookahead window in seconds
    :return: -1 if not entering within window (or orbit never passes SAA),
             0 if already in SAA,
             else seconds until entering SAA
    """
    if not hasattr(node, 'get_next_position'):
        return -1

    step_sec = 1.0
    t = now
    end_t = now + timedelta(seconds=window_sec)

    while t <= end_t:
        try:
            sublat, sublong, _ = node.get_next_position(t)
            if is_in_saa(sublat, sublong):
                elapsed = (t - now).total_seconds()
                return 0 if elapsed < 0.5 else int(elapsed)
        except Exception:
            pass
        t = t + timedelta(seconds=step_sec)

    return -1
