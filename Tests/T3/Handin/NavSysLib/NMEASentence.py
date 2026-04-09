from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional, List, Tuple

# utility functions; relative import when used as package, absolute when run as script
try:
    from .utilities import nmea_str_to_time, nmea_str_to_date, safe_int, safe_float, dm_to_deg
except ImportError:  # pragma: no cover - fallback for direct execution
    from utilities import nmea_str_to_time, nmea_str_to_date, safe_int, safe_float, dm_to_deg


@dataclass
class NMEASentence():
    """Base class for NMEA sentences. Contains common fields and methods for parsing and validating NMEA sentences."""
    talker: str
    format: str
    fields: List[str]
    checksum: Optional[str]
    string: str

    def __post_init__(self):
        # Validate checksum if provided
        if self.checksum is not None:
            if not self.validate_checksum():
                raise ValueError(f"Invalid checksum for sentence: {self.string}")

    def calculate_checksum(self) -> int:
        """Calculate the checksum for this sentence (without $ and without *checksum)"""
        body = self.string.strip()
        if body.startswith('$'):
            body = body[1:]
        if '*' in body:
            body = body.split('*', 1)[0]
        
        cs = 0
        for ch in body:
            cs ^= ord(ch)
        return cs

    def validate_checksum(self) -> bool:
        """Validate the checksum of this sentence. Returns True if valid, False if invalid or not provided."""
        if self.checksum is None:
            return False
        try:
            provided = int(self.checksum, 16)
        except ValueError:
            return False
        computed = self.calculate_checksum()
        return provided == computed

    def is_valid(self) -> bool:
        """Check if the sentence is valid (has a valid checksum)"""
        return self.validate_checksum()
        
    @classmethod
    def parse(cls, sentence: str) -> 'NMEASentence':
        s = sentence.strip()
        if not s:
            raise ValueError("Empty sentence")
        if s[0] == '$':
            s = s[1:]

        # split checksum
        if '*' in s:
            body, cs_str = s.split('*', 1)
            cs_str = cs_str.strip()
        else:
            body = s
            cs_str = None

        # split fields
        parts = body.split(',')
        header = parts[0]
        talker = header[:2] if len(header) >= 2 else header
        fmt = header[2:]
        fields = parts[1:]

        return cls(talker=talker, format=fmt, fields=fields, checksum=cs_str, string=sentence)


@dataclass
class GGASentence(NMEASentence):
    time: Optional[time]
    latitude: Optional[float]
    longitude: Optional[float]
    fix_quality: Optional[int]
    num_satellites: Optional[int]
    horizontal_dilution: Optional[float]
    altitude: Optional[float]
    altitude_units: Optional[str]
    geoid_height: Optional[float]
    geoid_height_units: Optional[str]

    @classmethod
    def from_nmea(cls, n: NMEASentence) -> 'GGASentence':
        f = n.fields
        time = nmea_str_to_time(f[0]) if len(f) > 0 else None
        lat = dm_to_deg(f[1]) if len(f) > 1 else None
        lat_dir = f[2] if len(f) > 2 else ''
        lon = dm_to_deg(f[3]) if len(f) > 3 else None
        lon_dir = f[4] if len(f) > 4 else ''
        if lat is not None and lat_dir.upper() == 'S':
            lat = -lat
        if lon is not None and lon_dir.upper() == 'W':
            lon = -lon
        fix_quality = safe_int(f[5]) if len(f) > 5 else None
        num_sat = safe_int(f[6]) if len(f) > 6 else None
        hdop = safe_float(f[7]) if len(f) > 7 else None
        alt = safe_float(f[8]) if len(f) > 8 else None
        alt_u = f[9] if len(f) > 9 else None
        geoid = safe_float(f[10]) if len(f) > 10 else None
        geoid_u = f[11] if len(f) > 11 else None

        return cls(talker=n.talker, format=n.format, fields=n.fields, checksum=n.checksum, string=n.string,
                   time=time, latitude=lat, longitude=lon, fix_quality=fix_quality,
                   num_satellites=num_sat, horizontal_dilution=hdop,
                   altitude=alt, altitude_units=alt_u,
                   geoid_height=geoid, geoid_height_units=geoid_u)

    def get_alt_above_ellipsoid(self) -> Optional[float]:
        """Calculate altitude above ellipsoid using geoid height if available"""
        if self.altitude is not None and self.geoid_height is not None:
            return self.altitude + self.geoid_height
        return None

    def is_valid(self) -> bool:
        """Override to also check fix quality"""
        if not super().is_valid():
            return False
        if self.fix_quality is None or self.fix_quality == 0:
            return False
        if self.fix_quality in [0, 6, 7, 8]:
            return False
        return True

@dataclass
class GLLSentence(NMEASentence):
    latitude: Optional[float]
    longitude: Optional[float]
    time: Optional[time]
    status: Optional[str]
    mode: Optional[str]

    @classmethod
    def from_nmea(cls, n: NMEASentence) -> 'GLLSentence':
        f = n.fields
        lat = dm_to_deg(f[0]) if len(f) > 0 else None
        lat_dir = f[1] if len(f) > 1 else ''
        lon = dm_to_deg(f[2]) if len(f) > 2 else None
        lon_dir = f[3] if len(f) > 3 else ''
        if lat is not None and lat_dir.upper() == 'S':
            lat = -lat
        if lon is not None and lon_dir.upper() == 'W':
            lon = -lon
        time = nmea_str_to_time(f[4]) if len(f) > 4 else None
        status = f[5] if len(f) > 5 else None
        mode = f[6] if len(f) > 6 else None

        return cls(talker=n.talker, format=n.format, fields=n.fields, checksum=n.checksum, string=n.string,
                   latitude=lat, longitude=lon, time=time, status=status, mode=mode)

    def is_valid(self) -> bool:
        """Override to also check status"""
        if not super().is_valid():
            return False
        if self.status is None or self.status.upper() != 'A':
            return False
        return True

@dataclass
class GSASentence(NMEASentence):
    mode: Optional[str]
    fix_type: Optional[int]
    satellite_prns: Optional[List[Optional[int]]]
    pdop: Optional[float]
    hdop: Optional[float]
    vdop: Optional[float]

    @classmethod
    def from_nmea(cls, n: NMEASentence) -> 'GSASentence':
        f = n.fields
        mode = f[0] if len(f) > 0 else None
        fix_type = safe_int(f[1]) if len(f) > 1 else None
        prns = []
        for i in range(2, 14):
            if len(f) > i and f[i] != '':
                prns.append(safe_int(f[i]))
            else:
                prns.append(None)
        pdop = safe_float(f[14]) if len(f) > 14 else None
        hdop = safe_float(f[15]) if len(f) > 15 else None
        vdop = safe_float(f[16]) if len(f) > 16 else None

        return cls(talker=n.talker, format=n.format, fields=n.fields, checksum=n.checksum, string=n.string,
                   mode=mode, fix_type=fix_type, satellite_prns=prns, pdop=pdop, hdop=hdop, vdop=vdop)


@dataclass
class GSVSentence(NMEASentence):
    num_messages: Optional[int]
    message_number: Optional[int]
    num_satellites: Optional[int]
    satellite_info: Optional[List[Tuple[Optional[int], Optional[int], Optional[int], Optional[int]]]]

    @classmethod
    def from_nmea(cls, n: NMEASentence) -> 'GSVSentence':
        f = n.fields
        num_msgs = safe_int(f[0]) if len(f) > 0 else None
        msg_num = safe_int(f[1]) if len(f) > 1 else None
        num_sats = safe_int(f[2]) if len(f) > 2 else None
        sat_info = []
        idx = 3
        while idx + 3 < len(f):
            prn = safe_int(f[idx])
            elev = safe_int(f[idx + 1])
            az = safe_int(f[idx + 2])
            snr = safe_int(f[idx + 3])
            sat_info.append((prn, elev, az, snr))
            idx += 4

        return cls(talker=n.talker, format=n.format, fields=n.fields, checksum=n.checksum, string=n.string,
                   num_messages=num_msgs, message_number=msg_num, num_satellites=num_sats, satellite_info=sat_info)


@dataclass
class RMCSentence(NMEASentence):
    time: Optional[time]
    status: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    speed_over_ground: Optional[float]
    track_angle: Optional[float]
    date: Optional[date]
    magnetic_variation: Optional[float]
    magnetic_variation_direction: Optional[str]
    # Custom attributes
    timestamp: Optional[datetime]

    @classmethod
    def from_nmea(cls, n: NMEASentence) -> 'RMCSentence':
        f = n.fields
        time = nmea_str_to_time(f[0]) if len(f) > 0 else None
        status = f[1] if len(f) > 1 else None
        lat = dm_to_deg(f[2]) if len(f) > 2 else None
        lat_dir = f[3] if len(f) > 3 else ''
        lon = dm_to_deg(f[4]) if len(f) > 4 else None
        lon_dir = f[5] if len(f) > 5 else ''
        if lat is not None and lat_dir.upper() == 'S':
            lat = -lat
        if lon is not None and lon_dir.upper() == 'W':
            lon = -lon
        sog = safe_float(f[6]) if len(f) > 6 else None
        track = safe_float(f[7]) if len(f) > 7 else None
        date_obj = nmea_str_to_date(f[8]) if len(f) > 8 else None
        mag_var = safe_float(f[9]) if len(f) > 9 else None
        mag_dir = f[10] if len(f) > 10 else None

        # Create timestamp from date and time fields
        timestamp = None
        if time is not None and date_obj is not None:
            try:
                timestamp = datetime.combine(date_obj, time)
            except Exception:
                pass

        return cls(talker=n.talker, format=n.format, fields=n.fields, checksum=n.checksum, string=n.string,
                   time=time, status=status, latitude=lat, longitude=lon,
                   speed_over_ground=sog, track_angle=track, date=date_obj,
                   magnetic_variation=mag_var, magnetic_variation_direction=mag_dir, timestamp=timestamp)

    def is_valid(self) -> bool:
        """Override to also check status"""
        if not super().is_valid():
            return False
        if self.status is None or self.status.upper() != 'A':
            return False
        return True

@dataclass
class VTGSentence(NMEASentence):
    track_true: Optional[float]
    track_magnetic: Optional[float]
    speed_knots: Optional[float]
    speed_kmh: Optional[float]
    mode: Optional[str]

    @classmethod
    def from_nmea(cls, n: NMEASentence) -> 'VTGSentence':
        f = n.fields
        # field order (units included):
        # 0: track_true
        # 1: 'T'
        # 2: track_magnetic
        # 3: 'M'
        # 4: speed_knots
        # 5: 'N'
        # 6: speed_kmh
        # 7: 'K'
        # 8: mode (A/D)
        track_true = safe_float(f[0]) if len(f) > 0 else None
        track_mag = safe_float(f[2]) if len(f) > 2 else None
        spd_kn = safe_float(f[4]) if len(f) > 4 else None
        spd_km = safe_float(f[6]) if len(f) > 6 else None
        # mode is located after the "K" unit indicator
        mode = f[8] if len(f) > 8 else None

        return cls(talker=n.talker, format=n.format, fields=n.fields, checksum=n.checksum, string=n.string,
                   track_true=track_true, track_magnetic=track_mag,
                   speed_knots=spd_kn, speed_kmh=spd_km, mode=mode)

    def is_valid(self) -> bool:
        """Override to also check mode"""
        if not super().is_valid():
            return False
        if self.mode is None or self.mode.upper() not in ['A', 'D']:
            return False
        return True

@dataclass
class ZDASentence(NMEASentence):
    time: Optional[time]
    day: Optional[int]
    month: Optional[int]
    year: Optional[int]
    local_zone_hours: Optional[int]
    local_zone_minutes: Optional[int]
    # Custom attributes
    date: Optional[date]
    timestamp: Optional[datetime]


    @classmethod
    def from_nmea(cls, n: NMEASentence) -> 'ZDASentence':
        f = n.fields
        time = nmea_str_to_time(f[0]) if len(f) > 0 else None
        day = safe_int(f[1]) if len(f) > 1 else None
        month = safe_int(f[2]) if len(f) > 2 else None
        year = safe_int(f[3]) if len(f) > 3 else None
        local_zone_hours = safe_int(f[4]) if len(f) > 4 else None
        local_zone_minutes = safe_int(f[5]) if len(f) > 5 else None

        # Create date and timestamp from ZDA fields
        date_obj = None
        if day is not None and month is not None and year is not None:
            try:
                date_obj = date(year, month, day)
            except Exception:
                print(f"Failed to create date from ZDA fields: day={day}, month={month}, year={year}")
                pass
        timestamp = None
        if time is not None and date_obj is not None:
            try:
                timestamp = datetime.combine(date_obj, time)
            except Exception:
                print(f"Failed to create timestamp from ZDA fields: date={date_obj}, time={time}")
                pass

        return cls(talker=n.talker, format=n.format, fields=n.fields, checksum=n.checksum, string=n.string,
                   time=time, day=day, month=month, year=year, local_zone_hours=local_zone_hours, 
                   local_zone_minutes=local_zone_minutes, date=date_obj, timestamp=timestamp)
