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

    def ecef_norm(self):
        """Returns distance from center of Earth to self in meters."""
        x, y, z = self.to_ecef()
        return np.sqrt(x**2 + y**2 + z**2)

    def pseudo_range_to(self, other, receiver_delta_t):
        """Returns pseudo-range in meters from self to other, accounting for clock offset."""
        c = 299792458  # speed of light in m/s
        geometric_range = self.distance_to(other)
        return geometric_range + c * receiver_delta_t

    def unit_vector_to(self, other):
        """Returns unit vector from self to other in ECEF coordinates."""
        x1, y1, z1 = self.to_ecef()
        x2, y2, z2 = other.to_ecef()
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        norm = np.sqrt(dx**2 + dy**2 + dz**2)
        if norm == 0:
            return (0.0, 0.0, 0.0)
        return (dx / norm, dy / norm, dz / norm)

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
    
    def direction_cosines_to(self, other):
        """Returns direction cosines from self to other in ECEF frame."""
        x1, y1, z1 = self.to_ecef()
        x2, y2, z2 = other.to_ecef()
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        norm = np.sqrt(dx**2 + dy**2 + dz**2)
        if norm == 0:
            return (0.0, 0.0, 0.0)
        return (dx / norm, dy / norm, dz / norm)

    def direction_cosines_to_enu(self, other):
        """Returns direction cosines from self to other in ENU frame."""
        e, n, u = self.enu_to(other)
        
        norm = np.sqrt(e**2 + n**2 + u**2)
        if norm == 0:
            return (0.0, 0.0, 0.0)
        return (e / norm, n / norm, u / norm)

    def compute_pseudoranges_for_epoch(
        self,
        orbits,
        wn: int,
        tow: float,
        clk_offset: float = 0.0,
        elevation_mask: float = 10.0,
        epsilon: float = 1e-4
    ) -> dict:
        """
        Computes pseudoranges from this receiver coordinate to a list of satellites for a specific epoch.
        
        Args:
            orbits: A list of Orbit objects or a dictionary mapping SV number to Orbit object.
            wn: Week Number at signal reception.
            tow: Time of Week (s) at signal reception.
            clk_offset: Receiver clock offset in seconds (dt_r). Default is 0.0.
            elevation_mask: Minimum elevation angle in degrees for a satellite to be included. Default is 10.0.
            epsilon: Convergence threshold for transmission time in meters.
            
        Returns:
            dict: A dictionary mapping sv_num to a result dict containing:
                - 'pseudorange': Computed pseudorange in meters
                - 'true_range': True geometric range in meters
                - 'elevation': Elevation angle in degrees
                - 'azimuth': Azimuth angle in degrees
                - 't_tx': Calculated transmission time
        """
        c = 299792458.0  # Speed of light in m/s
        results = {}
        
        orbit_dict = orbits
        if isinstance(orbits, list):
            orbit_dict = {}
            for i, ob in enumerate(orbits):
                if hasattr(ob, 'ephemeris') and ob.ephemeris is not None:
                    orbit_dict[ob.ephemeris.sv_num] = ob
                else:
                    orbit_dict[i] = ob

        rx_ecef = self.to_ecef()
        t_rx_total = tow + wn * 604800.0
        
        for sv_num, orbit in orbit_dict.items():
            # 1. Calculate precise transmission time iteratively
            t_tx_total = orbit.get_tx_time_from_ref_point(
                ref_wn=wn, 
                ref_tow=tow, 
                ref_pos_ecef=rx_ecef, 
                epsilon=epsilon
            )
            
            # 2. True geometric range based on signal transit time
            true_range = c * (t_rx_total - t_tx_total)
            
            # 3. Calculate elevation/azimuth using Sagnac-corrected satellite position
            sat_coords_rx_frame = orbit.get_pos_at_tx_time(
                t_tx=t_tx_total, 
                ref_wn=wn, 
                ref_tow=tow, 
                return_coords=True
            )
            
            azimuth, elevation = self.az_el_to(sat_coords_rx_frame)
            
            # 4. Check elevation mask and calculate pseudorange
            if elevation >= elevation_mask:
                pseudorange = true_range + c * clk_offset
                results[sv_num] = {
                    'pseudorange': float(pseudorange),
                    'true_range': float(true_range),
                    'elevation': float(elevation),
                    'azimuth': float(azimuth),
                    't_tx': float(t_tx_total)
                }
                
        return results
        

    # ---------------------------------------------------------
    # GNSS Positioning
    # ---------------------------------------------------------

    def get_orbits_from_elevation_mask(self, orbits, wn, tow, elevation_mask):
        """Returns list of Orbit objects that are above elevation mask at given time."""
        visible_orbits = []
        for ob in orbits:
            t_tx_total = ob.get_tx_time_from_ref_point(ref_wn=wn, ref_tow=tow, ref_pos_ecef=self.to_ecef(), epsilon=1e-4)
            sat_coords = ob.get_pos_at_tx_time(t_tx=t_tx_total, ref_wn=wn, ref_tow=tow, return_coords=True)
            _, elevation = self.az_el_to(sat_coords)
            if elevation >= elevation_mask:
                visible_orbits.append(ob)
                print(f"Satellite {ob.ephemeris.sv_num} is visible with elevation {elevation:.2f} deg")
        return visible_orbits
    
    def get_orbits_and_pseudoranges_from_elevation_mask(self, orbits, pseudoranges, wn, tow, elevation_mask):
        """Returns a list of Orbits and a list of pseudoranges for satellites above elevation mask at given time."""
        visible_orbits = []
        visible_pseudoranges = []
        for ob, pr in zip(orbits, pseudoranges):
            t_tx_total = ob.get_tx_time_from_ref_point(ref_wn=wn, ref_tow=tow, ref_pos_ecef=self.to_ecef(), epsilon=1e-4)
            sat_coords = ob.get_pos_at_tx_time(t_tx=t_tx_total, ref_wn=wn, ref_tow=tow, return_coords=True)
            _, elevation = self.az_el_to(sat_coords)
            if elevation >= elevation_mask:
                visible_orbits.append(ob)
                visible_pseudoranges.append(pr)
        return visible_orbits, visible_pseudoranges

    def get_H_matrix_from_orbits(self, orbits, wn, tow, elevation_mask, enu=False):        
        """Returns H matrix for given list of Orbit objects at given time and elevation mask."""
        visible_orbits = self.get_orbits_from_elevation_mask(orbits, wn, tow, elevation_mask)
        H = []
        for ob in visible_orbits:
            t_tx_total = ob.get_tx_time_from_ref_point(ref_wn=wn, ref_tow=tow, ref_pos_ecef=self.to_ecef(), epsilon=1e-4)
            sat_coords = ob.get_pos_at_tx_time(t_tx=t_tx_total, ref_wn=wn, ref_tow=tow, return_coords=True)
            if enu:
                unit_vec = self.direction_cosines_to_enu(sat_coords)
            else:
                unit_vec = self.direction_cosines_to(sat_coords)
            H.append((-unit_vec[0], -unit_vec[1], -unit_vec[2], 1.0))
        return np.array(H)
    
    def get_gdop_from_orbits(self, orbits, wn, tow, elevation_mask):
        """Returns GDOP value from given list of Orbit objects at given time and elevation mask."""
        visible_orbits = self.get_orbits_from_elevation_mask(orbits, wn, tow, elevation_mask)
        if len(visible_orbits) < 4:
            print("Not enough visible satellites to compute GDOP.")
            return float('inf')
        
        H = self.get_H_matrix_from_orbits(orbits, wn, tow, elevation_mask, enu=True)
        M = np.linalg.inv(H.T @ H)
        gdop_val = gdop(M=M)
        return gdop_val
    
    def get_pdop_from_orbits(self, orbits, wn, tow, elevation_mask):
        """Returns PDOP value from given list of Orbit objects at given time and elevation mask."""
        visible_orbits = self.get_orbits_from_elevation_mask(orbits, wn, tow, elevation_mask)
        if len(visible_orbits) < 4:
            print("Not enough visible satellites to compute PDOP.")
            return float('inf')
        
        H = self.get_H_matrix_from_orbits(orbits, wn, tow, elevation_mask, enu=True)
        M = np.linalg.inv(H.T @ H)
        pdop_val = pdop(M=M)
        return pdop_val
    
    def get_hdop_from_orbits(self, orbits, wn, tow, elevation_mask):
        """Returns HDOP value from given list of Orbit objects at given time and elevation mask."""
        visible_orbits = self.get_orbits_from_elevation_mask(orbits, wn, tow, elevation_mask)
        if len(visible_orbits) < 4:
            print("Not enough visible satellites to compute HDOP.")
            return float('inf')
        
        H = self.get_H_matrix_from_orbits(orbits, wn, tow, elevation_mask, enu=True)
        M = np.linalg.inv(H.T @ H)
        hdop_val = hdop(M=M)
        return hdop_val
    
    def get_vdop_from_orbits(self, orbits, wn, tow, elevation_mask):
        """Returns VDOP value from given list of Orbit objects at given time and elevation mask."""
        visible_orbits = self.get_orbits_from_elevation_mask(orbits, wn, tow, elevation_mask)
        if len(visible_orbits) < 4:
            print("Not enough visible satellites to compute VDOP.")
            return float('inf')
        
        H = self.get_H_matrix_from_orbits(orbits, wn, tow, elevation_mask, enu=True)
        M = np.linalg.inv(H.T @ H)
        vdop_val = vdop(M=M)
        return vdop_val
    
    def get_position_from_orbits_and_pseudoranges(
        self, orbits, pseudoranges, wn, tow, elevation_mask,
        num_iter=10, tol=1e-6, initial_guess=None
    ):
        import numpy as np
        c = 299792458.0

        visible_orbits, visible_pseudoranges = self.get_orbits_and_pseudoranges_from_elevation_mask(orbits, pseudoranges, wn, tow, elevation_mask)
        

        if len(visible_orbits) < 4:
            return None

        rx = np.array(self.to_ecef(), dtype=float) if initial_guess is None else np.array(initial_guess, dtype=float)
        bias = 0.0

        for iter_count in range(num_iter):
            H = []
            z_measurements = []

            for i, ob in enumerate(visible_orbits):
                pr = visible_pseudoranges[i]
                
                # t_rx = tow (according to local clock)
                # the true transmission time:
                t_tx_new = ob.get_tx_time_from_ref_point(ref_wn=wn, ref_tow=tow, ref_pos_ecef=tuple(rx), epsilon=1e-4) # wait, we need an even higher precision
                
                sat_coords = ob.get_pos_at_tx_time(t_tx=t_tx_new, ref_wn=wn, ref_tow=tow, return_coords=True)
                s_pos_eff = np.array(sat_coords.to_ecef(), dtype=float)
                
                geom_range = np.linalg.norm(s_pos_eff - rx)
                
                unit_vec = (rx - s_pos_eff) / geom_range
                H.append([unit_vec[0], unit_vec[1], unit_vec[2], 1.0])

                # Construct the absolute pseudo-measurement 'z' (Lecture formulation)
                z_k = pr - geom_range + (unit_vec[0] * rx[0] + unit_vec[1] * rx[1] + unit_vec[2] * rx[2])
                z_measurements.append(z_k)

            H = np.array(H)
            z = np.array(z_measurements)
            print(f"Iteration {iter_count+1}: H =\n{H}\nz = {z} \nrx = {rx}, bias = {bias}")

            x_new = np.linalg.inv(H.T @ H) @ H.T @ z
            
            if np.linalg.norm(x_new[0:3] - rx) < tol:
                rx = x_new[0:3]
                bias = x_new[3]
                print(f"Convergence achieved after {iter_count+1} iterations.")
                break

            rx = x_new[0:3]
            bias = x_new[3]

        x_hat = np.array([rx[0], rx[1], rx[2], bias])
        print(f"Estimate of Receiver Position: ({rx[0]:.3f} m, {rx[1]:.3f} m, {rx[2]:.3f} m)")
        print(f"Estimate of Receiver Clock Offset: {bias / c:.6f} s = {1000 * bias / c:.3f} ms")
        
        return x_hat

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