# Coords.py

from dataclasses import dataclass
import numpy as np
from .utilities import *
from .Orbit import *


@dataclass
class WGS84Coords:
    """
    Geodetic (latitude, longitude, altitude) coordinates
    on the WGS-84 ellipsoid.

    lat, lon stored in decimal degrees.
    alt in meters.
    """

    lat: float
    lon: float
    alt: float = 0.0

    # ---------------------------------------------------------
    # Constructors
    # ---------------------------------------------------------

    @classmethod
    def from_dms(cls, lat_dms, lon_dms, alt=0.0):
        """
        lat_dms = (deg, min, sec, 'N'/'S')
        lon_dms = (deg, min, sec, 'E'/'W')
        """

        lat_sign = 1 if lat_dms[3].upper() == 'N' else -1
        lon_sign = 1 if lon_dms[3].upper() == 'E' else -1

        lat = dms_to_decimal(lat_dms[0], lat_dms[1],
                                lat_dms[2], lat_sign)

        lon = dms_to_decimal(lon_dms[0], lon_dms[1],
                                lon_dms[2], lon_sign)

        return cls(lat, lon, alt)
    
    @classmethod
    def from_dm(cls, lat_dm, lon_dm, alt=0.0):
        """
        lat_dm = (deg, min, 'N'/'S')
        lon_dm = (deg, min, 'E'/'W')
        """

        lat_sign = 1 if lat_dm[2].upper() == 'N' else -1
        lon_sign = 1 if lon_dm[2].upper() == 'E' else -1

        lat = dm_to_decimal(lat_dm[0], lat_dm[1], lat_sign)
        lon = dm_to_decimal(lon_dm[0], lon_dm[1], lon_sign)

        return cls(lat, lon, alt)

    @classmethod
    def from_ecef(cls, x, y, z, method='bowring'):
        lat_rad, lon_rad, h = ecef_to_llh(x, y, z, method=method)
        return cls(rad2deg(lat_rad),
                   rad2deg(lon_rad),
                   h)
    
    @classmethod
    def from_orbit(cls, orbit: Orbit, wn: int = 0, tow: int = 0):
        """Construct WGS84Coords from given Orbit at given time (wn, tow)."""
        x, y, z = orbit.wgs84_ecef_position(wn, tow)
        return cls.from_ecef(x, y, z)
    

    # ---------------------------------------------------------
    # Representations
    # ---------------------------------------------------------

    def to_radians(self):
        return (deg2rad(self.lat),
                deg2rad(self.lon),
                self.alt)

    def to_dms(self):
        lat = decimal_to_dms(self.lat)
        lon = decimal_to_dms(self.lon)
        return lat, lon, self.alt

    def to_dm(self):
        lat = decimal_to_dm(self.lat)
        lon = decimal_to_dm(self.lon)
        return lat, lon, self.alt

    # ---------------------------------------------------------
    # Conversion
    # ---------------------------------------------------------

    def to_ecef(self):
        lat_rad, lon_rad, h = self.to_radians()
        return llh_to_ecef(lat_rad, lon_rad, h)
    
    def molodensky_transform(self, da, df, dx, dy, dz):
        """Returns new WGS84Coords transformed by Molodensky transformation with given parameters."""
        lat_rad, lon_rad, h = self.to_radians()
        new_lat_rad, new_lon_rad, new_h, d_lat, d_lon, d_h = molodensky_transform(lat_rad, lon_rad, h,
                                                              da, df, dx, dy, dz)
        
        print(f"d_lat: {rad2deg(d_lat)} deg, d_lon: {rad2deg(d_lon)} deg, d_h: {d_h} m")

        return WGS84Coords(rad2deg(new_lat_rad),
                           rad2deg(new_lon_rad),
                           new_h)

    def translate_ecef(self, dx, dy, dz):
        """Returns tuple with ECEF coords translated by given dx, dy, dz in ECEF coordinates."""
        x, y, z = self.to_ecef()
        x2 = x + dx
        y2 = y + dy
        z2 = z + dz
        return (x2, y2, z2)
    

    # ---------------------------------------------------------
    # Distance
    # ---------------------------------------------------------

    def distance_to(self, other):
        x1, y1, z1 = self.to_ecef()
        x2, y2, z2 = other.to_ecef()
        return euclidean_distance(x1, y1, z1,
                                     x2, y2, z2)

    def arc_length_to_ew(self, other):
        """Returns arc length in east-west direction in meters along the WGS84 ellipsoid between self and other."""
        lat1_rad, lon1_rad, _ = self.to_radians()
        lat2_rad, lon2_rad, _ = other.to_radians()
        delta_lon_rad = lon2_rad - lon1_rad
        circumference = wgs84_circumference_at_lat(lat1_rad)
        return circumference * (delta_lon_rad / (2 * np.pi))

    def orthodrome_to(self, other, radius=6371000):
        """Return distance, initial bearing and final bearing in degrees along the orthodrome (great circle) between self and other."""
        lat1_rad, lon1_rad, _ = self.to_radians()
        lat2_rad, lon2_rad, _ = other.to_radians()

        return orthodrome(lat1_rad, lon1_rad, lat2_rad, lon2_rad, radius=radius)

    def loxodrome_to(self, other, radius=6371000):
        """Return distance and bearing in degrees along the loxodrome (rhumb line) between self and other."""
        lat1_rad, lon1_rad, _ = self.to_radians()
        lat2_rad, lon2_rad, _ = other.to_radians()
        
        return loxodrome(lat1_rad, lon1_rad, lat2_rad, lon2_rad, radius=radius)

    # ---------------------------------------------------------
    # Azimuth & Elevation
    # ---------------------------------------------------------

    def enu_to(self, other):
        """Returns ENU vector from self to other, with self as origin."""
        x1, y1, z1 = self.to_ecef()
        x2, y2, z2 = other.to_ecef()
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        lat_rad, lon_rad, _ = self.to_radians()
        return ecef_to_enu(dx, dy, dz, lat_rad, lon_rad)

    def az_el_to(self, other):
        """Returns azimuth and elevation in degrees from self to other."""
        e, n, u = self.enu_to(other)
        print(f"e: {e}, n: {n}, u: {u}")
        return enu_to_az_el(e, n, u)
    
    def az_el_range_to(self, other):
        """Returns azimuth, elevation in degrees and range in meters from self to other."""
        e, n, u = self.enu_to(other)
        return enu_to_az_el_range(e, n, u)
    
    def coords_from_az_el_range(self, az_deg, el_deg, range_m):
        """Returns new WGS84Coords of point at given azimuth, elevation and range from self."""
        e, n, u = az_el_range_to_enu(az_deg, el_deg, range_m)
        lat_rad, lon_rad, _ = self.to_radians()
        dx, dy, dz = enu_to_ecef(e, n, u, lat_rad, lon_rad)
        x1, y1, z1 = self.to_ecef()
        x2 = x1 + dx
        y2 = y1 + dy
        z2 = z1 + dz
        return WGS84Coords.from_ecef(x2, y2, z2)

    # ---------------------------------------------------------
    # Pretty printing
    # ---------------------------------------------------------

    def __str__(self, decimals=2):
        return f"{self.lat:.6f}°, {self.lon:.6f}°, h={self.alt:.{decimals}f} m"

    def to_dms_string(self, decimals=2):
        """Returns formatted string: DDº MM´ SS.ss´´ N/S, DDº MM´ SS.ss´´ E/W"""
        lat_dms, lon_dms, _ = self.to_dms()
        # lat_dms and lon_dms are (sign, deg, min, sec)
        lat_dir = 'N' if lat_dms[0] >= 0 else 'S'
        lon_dir = 'E' if lon_dms[0] >= 0 else 'W'
        lat_str = f"{int(lat_dms[1])}º {int(lat_dms[2])}´ {lat_dms[3]:.{decimals}f}´´ {lat_dir}"
        lon_str = f"{int(lon_dms[1])}º {int(lon_dms[2])}´ {lon_dms[3]:.{decimals}f}´´ {lon_dir}"
        return f"{lat_str}, {lon_str}, h={self.alt:.{decimals}f} m"

    def to_dm_string(self, decimals=2):
        """Returns formatted string: DDº MM.mmm´ N/S, DDº MM.mmm´ E/W"""
        lat_dm, lon_dm, _ = self.to_dm()
        # lat_dm and lon_dm are (sign, deg, min)
        lat_dir = 'N' if lat_dm[0] >= 0 else 'S'
        lon_dir = 'E' if lon_dm[0] >= 0 else 'W'
        lat_str = f"{int(lat_dm[1])}º {lat_dm[2]:.{decimals}f}´ {lat_dir}"
        lon_str = f"{int(lon_dm[1])}º {lon_dm[2]:.{decimals}f}´ {lon_dir}"
        return f"{lat_str}, {lon_str}, h={self.alt:.{decimals}f} m"

    def to_decimal_string(self, decimals=2):
        """Returns formatted string: DD.ddd° N/S, DD.ddd° E/W"""
        lat_dir = 'N' if self.lat >= 0 else 'S'
        lon_dir = 'E' if self.lon >= 0 else 'W'
        lat_str = f"{abs(self.lat):.{decimals}f}° {lat_dir}"
        lon_str = f"{abs(self.lon):.{decimals}f}° {lon_dir}"
        return f"{lat_str}, {lon_str}, h={self.alt:.{decimals}f} m"

    def to_ecef_string(self, decimals=2):
        """Returns formatted string: x, y, z in meters (WGS84 cartesian)"""
        x, y, z = self.to_ecef()
        return f"x={x:.{decimals}f} m, y={y:.{decimals}f} m, z={z:.{decimals}f} m"