from datetime import date, time, datetime
from typing import Optional
import numpy as np



###############################################################################
# E1
###############################################################################

nmea_formats = ["GGA", "GLL", "GSA", "GSV", "RMC", "VTG", "ZDA"]

def safe_int(s: str) -> Optional[int]:
    """Convert string to int, return None if conversion fails"""
    try:
        return int(s)
    except Exception:
        return None


def safe_float(s: str) -> Optional[float]:
    """Convert string to float, return None if conversion fails"""
    try:
        return float(s)
    except Exception:
        return None


def dm_to_deg(dm: str) -> Optional[float]:
    """Convert NMEA lat/lon in ddmm.mmmm (or dddmm.mmmm) to decimal degrees"""
    if not dm or dm == "":
        return None
    try:
        if '.' in dm:
            parts = dm.split('.')
            whole = parts[0]
        else:
            whole = dm
        # latitude: 2 deg digits, longitude: 3 deg digits - detect by length
        if len(whole) <= 4:  # e.g. 3844 -> lat
            deg_len = 2
        else:
            deg_len = len(whole) - 2
        degrees = int(dm[:deg_len])
        minutes = float(dm[deg_len:])
        return degrees + minutes / 60.0
    except Exception:
        return None

def nmea_str_to_datetime(s: str) -> Optional[datetime]:
    """Convert NMEA date/time string to datetime object, return None if conversion fails"""
    # Format: hhmmss.sss,dd,mm,yyyy for date and time
    try:
        if len(s) == 6:  # time only, e.g. 110259
            return datetime.strptime(s, "%H%M%S")
        elif len(s) == 12:  # date and time, e.g. 250913110259
            return datetime.strptime(s, "%d%m%y%H%M%S")
        else:
            return None
    except Exception:
        return None

def nmea_str_to_date(s: str) -> Optional[date]:
    """Convert NMEA date string to date object, return None if conversion fails"""
    # Format: ddmm yy, e.g. 250913
    try:
        return datetime.strptime(s, "%d%m%y").date()
    except Exception:
        return None

def nmea_str_to_time(s: str) -> Optional[time]:
    """Convert NMEA time string to time object, return None if conversion fails"""
    # Format: hhmmss.sss, e.g. 110259.600
    try:
        return datetime.strptime(s, "%H%M%S.%f").time()
    except Exception:
        return None

def knots_to_kmh(knots: Optional[float]) -> Optional[float]:
    """Convert speed from knots to km/h, return None if input is None"""
    if knots is None:
        return None
    return knots * 1.852


###############################################################################
# E2
###############################################################################

# ---------------------------------------------------------------------
# WGS-84 constants
# ---------------------------------------------------------------------

WGS84_A = 6378137.0                      # semi-major axis [m]
WGS84_F = 1 / 298.257223563              # flattening
WGS84_B = WGS84_A * (1 - WGS84_F)        # semi-minor axis
WGS84_E2 = WGS84_F * (2 - WGS84_F)       # first eccentricity squared
WGS84_EP2 = WGS84_E2 / (1 - WGS84_E2)    # second eccentricity squared

#---------------------------------------------------------------------
# WGS-84 non-constants
#---------------------------------------------------------------------

def wgs84_radius_of_curvature(lat_rad):
    """Calculate the radius of curvature in the prime vertical (RN) at given latitude"""
    sin_lat = np.sin(lat_rad)
    return WGS84_A / np.sqrt(1 - WGS84_E2 * sin_lat**2)

def wgs84_circumference_at_lat(lat_rad):
    """Calculate the circumference of the Earth at given latitude"""
    RN = wgs84_radius_of_curvature(lat_rad)
    return 2 * np.pi * RN * np.cos(lat_rad)


# ---------------------------------------------------------------------
# Distance
# ---------------------------------------------------------------------

def euclidean_distance(x1, y1, z1, x2, y2, z2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)


# ---------------------------------------------------------------------
# Angle utilities
# ---------------------------------------------------------------------

def deg2rad(deg):
    return np.deg2rad(deg)


def rad2deg(rad):
    return np.rad2deg(rad)


def dms_to_decimal(deg, minutes, seconds, sign=1):
    """
    Convert Degrees, Minutes, Seconds to decimal degrees.
    sign = +1 or -1
    """
    return sign * (abs(deg) + minutes / 60 + seconds / 3600)

def dm_to_decimal(deg, minutes, sign=1):
    """
    Convert Degrees and Decimal Minutes to decimal degrees.
    sign = +1 or -1
    """
    return sign * (abs(deg) + minutes / 60)


def decimal_to_dms(decimal_deg):
    """
    Convert decimal degrees to (deg, min, sec)
    """
    sign = np.sign(decimal_deg)
    decimal_deg = abs(decimal_deg)

    deg = int(decimal_deg)
    minutes_full = (decimal_deg - deg) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60

    return sign, deg, minutes, seconds


def decimal_to_dm(decimal_deg):
    """
    Convert decimal degrees to (deg, decimal_minutes)
    """
    sign = np.sign(decimal_deg)
    decimal_deg = abs(decimal_deg)

    deg = int(decimal_deg)
    minutes = (decimal_deg - deg) * 60

    return sign, deg, minutes


# ---------------------------------------------------------------------
# Geodetic <-> ECEF
# ---------------------------------------------------------------------

def ecef_to_long(x, y):
    """Calculate longitude in radians from ECEF x and y"""
    return np.arctan2(y, x)

def ecef_to_lat_bowring(x, y, z):
    """Calculate latitude in radians from ECEF x, y, z using Bowring (1976) method"""
    b = WGS84_B
    a = WGS84_A
    e2 = WGS84_E2
    ep2 = WGS84_EP2
    p = np.sqrt(x**2 + y**2)
    beta = np.arctan2(a * z, b * p)

    lat = np.arctan2(
        z + ep2 * b * np.sin(beta)**3,
        p - e2 * a * np.cos(beta)**3
    )

    return lat

def ecef_to_lat_heikkinen(x, y, z):
    """Calculate latitude in radians from ECEF x, y, z using Heikkinen (1982) method"""
    b = WGS84_B
    a = WGS84_A
    e2 = WGS84_E2
    ep2 = WGS84_EP2
    r = np.sqrt(x**2 + y**2)

    F = 54 * b**2 * z**2
    G = r**2 + (1 - e2) * z**2 - e2 * (a**2 - b**2)
    c = (e2**2 * F * r**2) / (G**3)
    s = np.cbrt(1 + c + np.sqrt(c**2 + 2*c))
    P = F / (3 * (s + 1/s + 1)**2 * G**2)
    Q = np.sqrt(1 + 2 * e2**2 * P)
    r0 = -(P * e2 * r) / (1 + Q) + np.sqrt(0.5 * a**2 * (1 + 1/Q) - P * (1 - e2) * z**2 / (Q * (1 + Q)) - 0.5 * P * r**2)
    U = np.sqrt((r - e2 * r0)**2 + z**2)
    V = np.sqrt((r - e2 * r0)**2 + (1 - e2) * z**2)
    z0 = (b**2 * z) / (a * V)
    h = U * (1 - b**2 / (a * V))

    lat = np.arctan2(z + ep2 * z0, r)

    return lat

def ecef_to_llh(x, y, z,
                a=WGS84_A, f=WGS84_F, method='bowring'):
    """
    Convert ECEF (x,y,z) to geodetic (lat, lon, h)
    using Bowring (1976) method.
    Returns (lat_rad, lon_rad, h)
    """

    b = a * (1 - f)
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)

    p = np.sqrt(x**2 + y**2)

    lon = ecef_to_long(x, y)

    if method == 'bowring':
        lat = ecef_to_lat_bowring(x, y, z)
    elif method == 'heikkinen':
        lat = ecef_to_lat_heikkinen(x, y, z)
    else:
        lat = ecef_to_lat_bowring(x, y, z)

    sin_lat = np.sin(lat)
    RN = a / np.sqrt(1 - e2 * sin_lat**2)

    h = p / np.cos(lat) - RN

    return lat, lon, h

def llh_to_ecef(lat_rad, lon_rad, h,
                a=WGS84_A, f=WGS84_F):
    """
    Convert geodetic (lat, lon, h) to ECEF (x,y,z).
    All angles in radians.
    """
    e2 = f * (2 - f)

    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)

    RN = a / np.sqrt(1 - e2 * sin_lat**2)

    x = (RN + h) * cos_lat * np.cos(lon_rad)
    y = (RN + h) * cos_lat * np.sin(lon_rad)
    z = ((1 - f)**2 * RN + h) * sin_lat

    #print(f"RN: {RN}, f: {f}")

    return x, y, z


# ---------------------------------------------------------------------
# ENU frame
# ---------------------------------------------------------------------

def rot_x(angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s, c]])

def rot_y(angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    return np.array([[c, 0, s],
                     [0, 1, 0],
                     [-s, 0, c]])

def rot_z(angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    return np.array([[c, -s, 0],
                     [s, c, 0],
                     [0, 0, 1]])

def ecef_to_enu(dx, dy, dz, lat_rad, lon_rad):
    """
    Convert delta ECEF vector to ENU at reference (lat, lon) using rotation matrices.
    """

    R = rot_z(lon_rad + np.pi/2) @ rot_x(np.pi/2 - lat_rad)
    return np.array([dx, dy, dz]) @ R

def enu_to_ecef(e, n, u, lat_rad, lon_rad):
    """
    Convert ENU vector to delta ECEF at reference (lat, lon) using rotation matrices.
    """
    R = rot_x(lat_rad - np.pi/2) @ rot_z(-lon_rad - np.pi/2) 
    return np.array([e, n, u]) @ R

def az(e, n):
    """Calculate azimuth in degrees from ENU e and n components"""
    return rad2deg(np.arctan2(e, n))

def el(e, n, u):
    """Calculate elevation in degrees from ENU e, n, u components"""
    return rad2deg(np.arctan2(u, np.sqrt(e**2 + n**2)))

def enu_to_az_el(e, n, u):
    """Calculate azimuth and elevation in degrees from ENU e, n, u components"""
    return az(e, n), el(e, n, u)

def enu_to_az_el_range(e, n, u):
    """Calculate azimuth, elevation in degrees and range in meters from ENU e, n, u components"""
    azimuth = az(e, n)
    elevation = el(e, n, u)
    range_m = np.sqrt(e**2 + n**2 + u**2)
    return azimuth, elevation, range_m

def az_el_range_to_enu(az_deg, el_deg, range_m):
    """Convert azimuth, elevation in degrees and range in meters to ENU vector"""
    az_rad = deg2rad(az_deg)
    el_rad = deg2rad(el_deg)
    e = range_m * np.cos(el_rad) * np.sin(az_rad)
    n = range_m * np.cos(el_rad) * np.cos(az_rad)
    u = range_m * np.sin(el_rad)
    return e, n, u


###############################################################################
# E3
###############################################################################


# ---------------------------------------------------------------------
# Datum transformations
# ---------------------------------------------------------------------

def molodensky_transform(lat_rad, lon_rad, h, 
                        da, df, dX, dY, dZ, a=WGS84_A, b=WGS84_B, e2=WGS84_E2,):
    """
    Apply Molodensky transformation to convert coordinates between datums.
    lat_rad, lon_rad in radians, h in meters.
    da, df are the changes in the semi-major axis and flattening.
    dX, dY, dZ are the translation parameters in meters.
    Returns transformed (lat_rad, lon_rad, h, d_lat, d_lon, d_h).
    """

    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)
    sin_lon = np.sin(lon_rad)
    cos_lon = np.cos(lon_rad)

    RN = a / np.sqrt(1 - e2 * sin_lat**2)
    RM = a * (1 - e2) / (1 - e2 * sin_lat**2)**(3/2)

    d_lat = (-dX * sin_lat * cos_lon - dY * sin_lat * sin_lon + dZ * cos_lat + (da * ((RN * e2)/a) + df * (RM * (a/b) + RN * (b/a)) ) * sin_lat * cos_lat) / (RM + h)
    d_lon = (-dX * sin_lon + dY * cos_lon) / ((RN + h) * cos_lat)
    d_h = dX * cos_lat * cos_lon + dY * cos_lat * sin_lon + dZ * sin_lat - da * (a/RN) + df * (b/a) * RN * sin_lat**2
    
    return lat_rad + d_lat, lon_rad + d_lon, h + d_h, d_lat, d_lon, d_h

def ecef_datum_transform(lat_rad, lon_rad, h, dX, dY, dZ, a2, f2, a1=WGS84_A, f1=WGS84_F):
    """Convert to datum 2 with parameters a, f and translation dX, dY, dZ from datum 1,
        converting to ECEF, applying translation, and converting back to LLH.
        Default datum 1 is WGS-84."""
    x1, y1, z1 = llh_to_ecef(lat_rad, lon_rad, h, a=a1, f=f1)
    x2 = x1 + dX
    y2 = y1 + dY
    z2 = z1 + dZ
    return ecef_to_llh(x2, y2, z2, a=a2, f=f2)


# ---------------------------------------------------------------------
# Great circle navigation
# ---------------------------------------------------------------------

def orthodrome(lat1, lon1, lat2, lon2, radius=6371000):
    """Calculate orthodrome distance, departure heading and arrival heading between two points given in radians."""
    # Use spherical Earth model
    R = radius # m
    cos_theta = np.cos(lat2) * np.cos(lon1 - lon2) * np.cos(lat1) + np.sin(lat2) * np.sin(lat1)
    theta = np.arccos(cos_theta)
    distance = R * theta

    departure_heading = np.arctan2(np.cos(lat2) * np.sin(lon2 - lon1),
                                  -np.cos(lat2) * np.cos(lon1 - lon2) * np.sin(lat1) + np.sin(lat2) * np.cos(lat1))
    arrival_heading = np.arctan2(-np.sin(lon1 - lon2) * np.cos(lat1),
                                np.sin(lat2) * np.cos(lon1 - lon2) * np.cos(lat1) - np.cos(lat2) * np.sin(lat1))

    # Convert headings to degrees
    departure_heading = rad2deg(departure_heading)
    arrival_heading = rad2deg(arrival_heading)

    return distance, departure_heading, arrival_heading

def _sigma(lat):
    """Calculate the sigma parameter for loxodrome distance calculation."""
    return np.log(np.tan(lat/2 + np.pi/4))

def loxodrome(lat1, lon1, lat2, lon2, radius=6371000):
    """Calculate loxodrome distance and bearing between two points given in radians."""
    # Use spherical Earth model
    R = radius # m

    bearing = np.arctan2(lon2 - lon1, _sigma(lat2) - _sigma(lat1))
    distance = R * np.abs( (lat2 - lat1) / np.cos(bearing) )

    print(_sigma(lat1))
    print(_sigma(lat2))

    # Convert bearing to degrees
    bearing = rad2deg(bearing)

    return distance, bearing


###############################################################################
# E4
###############################################################################

# ---------------------------------------------------------------------
# Polar coordinates
# ---------------------------------------------------------------------

def r0(A, e, phi0):
    """Calculate r0 parameter for polar coordinates from eccentricity e and latitude of origin phi0 in radians."""
    return A * (1 - e**2) / (1 + e * np.cos(phi0))

def polar_to_cartesian(r, theta, r0):
    """Convert polar coordinates (r, theta) to Cartesian (x, y) using r0 parameter."""
    x = r * np.cos(theta) + r0
    y = r * np.sin(theta)
    return x, y


# ---------------------------------------------------------------------
# Orbital mechanics
# ---------------------------------------------------------------------


# Angular translation for Earth during 24 hours, in radians
EARTH_ALPHA = 2 * np.pi / (365.25)
EARTH_ROT_RATE_APPROX = (2 * np.pi + EARTH_ALPHA) / (24 * 60 * 60)  # rad/s, approximate
EARTH_ROT_RATE = 7.2921151467E-5 # rad/s, IS-GPS-200 standard value
RIGHT_ASCENSION_RATE = deg2rad(-0.04) / (24 * 60 * 60) # rad/s, rate of right ascension for GPS orbits

MU = 3.986005E14 # m^3/s^2, standard gravitational parameter for Earth

def orbital_period(A, mu=MU):
    """Calculate orbital period T in seconds for semi-major axis A in meters."""
    return 2.0 * np.pi * np.sqrt((A ** 3) / mu)

def semimajor_axis(T, mu=MU):
    """Calculate semi-major axis A in meters for orbital period T in seconds."""
    return ( (T / (2.0 * np.pi))**2 * mu )**(1/3)


def rarm(t, t0=0, initial_rarm=0, earth_rot_rate=EARTH_ROT_RATE):
    """Calculate Right Ascension of Reference Meridian in radians at time t (seconds) since epoch t0."""
    return initial_rarm + (earth_rot_rate * (t - t0))

def raan(t, t0=0, rate_deg_per_day=-0.04, initial_raan=0):
    """Calculate Right Ascension of Ascending Node in radians at time t (seconds) since epoch t0."""
    rate_rad_per_sec = np.deg2rad(rate_deg_per_day) / (24 * 60 * 60)
    return initial_raan + rate_rad_per_sec * (t - t0)

def lan(t, t0=0, initial_raan=0, rate_deg_per_day=-0.04, initial_rarm=0, earth_rot_rate=EARTH_ROT_RATE):
    """Calculate Longitude of Ascending Node in radians at time t (seconds) since epoch t0."""
    return raan(t, t0=t0, rate_deg_per_day=rate_deg_per_day, initial_raan=initial_raan) - rarm(t, t0=t0, initial_rarm=initial_rarm, earth_rot_rate=earth_rot_rate)

def mean_anomaly(t, t_p, n):
    """Calculate mean anomaly M (rad) from perigee time t_p and mean motion n (rad/s)."""
    return n * (t - t_p)

def mean_anomaly_M0(M0, d_t, eta):
    """Calculate mean anomaly M (rad) from reference epoch t_oe, M0 and mean motion n (rad/s)."""
    return M0 + eta * d_t

def mean_angular_velocity(a, d_eta=0.0, mu=MU):
    """Calculate mean angular velocity omega (eta) in rad/s from semi-major axis a in meters."""
    return np.sqrt(mu / (a ** 3)) + d_eta

def wrap_angle_2pi(angle_rad):
    """Wrap an angle in radians to [0, 2*pi)."""
    return angle_rad % (2.0 * np.pi)

def perigee_tow_from_toe(toe, M0, n):
    """Return perigee TOW (s) in the same cycle branch as toe from toe, M0 and mean motion n."""
    if n == 0:
        raise ValueError("mean motion n must be non-zero")
    return toe - (M0 / n)

def first_perigee_tow_in_week(toe, M0, n, week_seconds=604800.0):
    """Return the earliest perigee TOW (s) inside GPS week [0, week_seconds)."""
    t_ref = perigee_tow_from_toe(toe, M0, n)
    T = (2.0 * np.pi) / abs(n)

    if T >= week_seconds:
        return t_ref % week_seconds

    # Earliest non-negative perigee epoch among all t_ref + k*T in the week.
    return t_ref % T

def eccentric_anomaly(M, e, tol=1e-8, max_iter=100):
    """Calculate eccentric anomaly E from mean anomaly M and eccentricity e using Newton's method."""
    E = M  # initial guess
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M
        f_prime = 1 - e * np.cos(E)
        E_new = E - f / f_prime
        if abs(E_new - E) < tol:
            return E_new
        E = E_new
    return E  # return last estimate if max iterations reached

def true_anomaly(E, e):
    """Calculate true anomaly nu from eccentric anomaly E and eccentricity e."""
    return 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))

def orbital_radius(a, e, E):
    """Calculate orbital radius r from semi-major axis a, eccentricity e and eccentric anomaly E."""
    return a * (1 - e * np.cos(E))

def gps_delta_t(wn1, tow1, wn2, tow2):
    """Calculate time difference in seconds between two GPS epochs given by week number and TOW."""
    return (wn1 - wn2) * 604800.0 + (tow1 - tow2)

def calculate_start_time(wn_end, tow_end, dur_week, dur_sec):
    wn_start = wn_end - dur_week
    delta_s = tow_end - dur_sec
    if delta_s < 0:
        wn_start -= 1
        tow_start = 604800 + delta_s
    else:
        tow_start = delta_s
    return wn_start, tow_start