# support both package and direct execution imports
try:
    from .NMEASentence import *
    from .utilities import *
    from .Coords import *
except ImportError:  # pragma: no cover
    from NMEASentence import *
    from utilities import *
    from Coords import *

class NMEALog:
    sentences: List[NMEASentence]
    gga_sentences: List[GGASentence]
    gll_sentences: List[GLLSentence]
    gsa_sentences: List[GSASentence]
    gsv_sentences: List[GSVSentence]
    rmc_sentences: List[RMCSentence]
    vtg_sentences: List[VTGSentence]
    zda_sentences: List[ZDASentence]
    strings: List[str]


    def add_sentence(self, sentence: str):
        try:
            nmea = NMEASentence.parse(sentence)
            self.sentences.append(nmea)
            self.strings.append(sentence)
            if nmea.format == 'GGA':
                self.gga_sentences.append(GGASentence.from_nmea(nmea))
            elif nmea.format == 'GLL':
                self.gll_sentences.append(GLLSentence.from_nmea(nmea))
            elif nmea.format == 'GSA':
                self.gsa_sentences.append(GSASentence.from_nmea(nmea))
            elif nmea.format == 'GSV':
                self.gsv_sentences.append(GSVSentence.from_nmea(nmea))
            elif nmea.format == 'RMC':
                self.rmc_sentences.append(RMCSentence.from_nmea(nmea))
            elif nmea.format == 'VTG':
                self.vtg_sentences.append(VTGSentence.from_nmea(nmea))
            elif nmea.format == 'ZDA':
                self.zda_sentences.append(ZDASentence.from_nmea(nmea))
        except Exception as e:
            print(f"Failed to parse sentence: {sentence}. Error: {e}")
    
    @classmethod
    def from_strings(cls, sentences: List[str]) -> 'NMEALog':
        # create empty log and populate
        log = cls()
        for s in sentences:
            log.add_sentence(s)
        return log

    @classmethod
    def from_file(cls, filename: str) -> 'NMEALog':
        with open(filename, 'r') as f:
            lines = f.readlines()
        return cls.from_strings(lines)

    def __init__(self):
        # initialize storage lists before parsing
        self.sentences = []
        self.gga_sentences = []
        self.gll_sentences = []
        self.gsa_sentences = []
        self.gsv_sentences = []
        self.rmc_sentences = []
        self.vtg_sentences = []
        self.zda_sentences = []
        self.strings = []

    @property
    def format_dict(self) -> dict[str, list]:
        """Returns a dictionary mapping NMEA format strings to their sentence lists."""
        return {
            'GGA': self.gga_sentences,
            'GLL': self.gll_sentences,
            'GSA': self.gsa_sentences,
            'GSV': self.gsv_sentences,
            'RMC': self.rmc_sentences,
            'VTG': self.vtg_sentences,
            'ZDA': self.zda_sentences,
        }

    def get_sentence_count(self, format: str = "") -> int:
        """Returns the total number of sentences in the log."""
        if format != "":
            return len(self.format_dict.get(format, []))
        return len(self.sentences)
    
    def get_sentences_by_format(self, format: str) -> List[NMEASentence]:
        """Returns a list of sentences for the given NMEA format."""
        return self.format_dict.get(format, [])
    
    def get_sentence_by_attr_value(self, attr: str, value, format: str = "") -> Optional[NMEASentence]:
        if format != "":
            for sentence in self.format_dict.get(format, []):
                if hasattr(sentence, attr) and getattr(sentence, attr) == value and sentence.is_valid():
                    return sentence
        else:
            for format, sentences in self.format_dict.items():
                for sentence in sentences:
                    if hasattr(sentence, attr) and getattr(sentence, attr) == value and sentence.is_valid():
                        return sentence
        return None

    def get_sentence_by_attr_min(self, attr: str, format: str = "") -> Optional[NMEASentence]:
        min_sentence = None
        if format != "":
            for sentence in self.format_dict.get(format, []):
                if hasattr(sentence, attr) and getattr(sentence, attr) is not None and sentence.is_valid():
                    if min_sentence is None or getattr(sentence, attr) < getattr(min_sentence, attr):
                        min_sentence = sentence
        else:
            for format, sentences in self.format_dict.items():
                for sentence in sentences:
                    if hasattr(sentence, attr) and getattr(sentence, attr) is not None and sentence.is_valid():
                        if min_sentence is None or getattr(sentence, attr) < getattr(min_sentence, attr):
                            min_sentence = sentence
        return min_sentence
    
    def get_sentence_by_attr_max(self, attr: str, format: str = "") -> Optional[NMEASentence]:
        max_sentence = None
        if format != "":
            for sentence in self.format_dict.get(format, []):
                if hasattr(sentence, attr) and getattr(sentence, attr) is not None and sentence.is_valid():
                    if max_sentence is None or getattr(sentence, attr) > getattr(max_sentence, attr):
                        max_sentence = sentence
        else:
            for format, sentences in self.format_dict.items():
                for sentence in sentences:
                    if hasattr(sentence, attr) and getattr(sentence, attr) is not None and sentence.is_valid():
                        if max_sentence is None or getattr(sentence, attr) > getattr(max_sentence, attr):
                            max_sentence = sentence
        return max_sentence

    def get_start_datetime(self) -> Optional[datetime]:
        """Returns the date and time of the start of the logging session. 
        Combines the earliest date with the earliest time, possibly from
        two different sentences"""
        earliest_date = None
        earliest_time = None
        for format in ['RMC', 'ZDA', 'GGA', 'GLL']:  # these formats may contain date/time info
            for sentence in self.format_dict.get(format, []):
                if hasattr(sentence, 'date') and sentence.date is not None:
                    if earliest_date is None or sentence.date < earliest_date:
                        earliest_date = sentence.date
                if hasattr(sentence, 'time') and sentence.time is not None:
                    if earliest_time is None or sentence.time < earliest_time:
                        earliest_time = sentence.time
        if earliest_date is not None and earliest_time is not None:
            return datetime.combine(earliest_date, earliest_time)
        return None
            

    def get_end_datetime(self) -> Optional[datetime]:
        """Returns the date and time of the end of the logging session. 
        Combines the latest date with the latest time, possibly from
        two different sentences"""
        latest_date = None
        latest_time = None
        for format in ['RMC', 'ZDA', 'GGA', 'GLL']:  # these formats may contain date/time info
            for sentence in self.format_dict.get(format, []):
                if hasattr(sentence, 'date') and sentence.date is not None:
                    if latest_date is None or sentence.date > latest_date:
                        latest_date = sentence.date
                if hasattr(sentence, 'time') and sentence.time is not None:
                    if latest_time is None or sentence.time > latest_time:
                        latest_time = sentence.time
        if latest_date is not None and latest_time is not None:
            return datetime.combine(latest_date, latest_time)
        return None

    def get_sentence_from_time_str(self, time_str: str, format: str = "ZDA") -> Optional[NMEASentence]:
        """Returns the first sentence of the given format with a timestamp matching the given time string, or None if no such sentence is found."""
        target_time = nmea_str_to_time(time_str)
        for sentence in self.format_dict.get(format, []):
            if hasattr(sentence, 'time') and sentence.time is not None:
                if sentence.time == target_time:
                    return sentence
        return None
    
    def get_longitudes(self) -> List[float]:
        """Returns a list of all longitude values from sentences that contain longitude information."""
        longitudes = []
        for format in ['GGA', 'GLL', 'RMC']:
            for sentence in self.format_dict.get(format, []):
                if hasattr(sentence, 'longitude') and sentence.longitude is not None and sentence.is_valid():
                    longitudes.append(sentence.longitude)
        return longitudes

    def get_latitudes(self) -> List[float]:
        """Returns a list of all latitude values from sentences that contain latitude information."""
        latitudes = []
        for format in ['GGA', 'GLL', 'RMC']:
            for sentence in self.format_dict.get(format, []):
                if hasattr(sentence, 'latitude') and sentence.latitude is not None and sentence.is_valid():
                    latitudes.append(sentence.latitude)
        return latitudes

    def get_altitudes(self, reference: str = "geoid") -> List[float]:
        """Returns a list of all altitude values from sentences that contain altitude information."""
        altitudes = []
        for sentence in self.format_dict.get('GGA', []):
            if hasattr(sentence, 'altitude') and sentence.altitude is not None and sentence.is_valid():
                if reference == "geoid":
                    altitudes.append(sentence.altitude)
                elif reference == "ellipsoid":
                    alt_above_ellipsoid = sentence.get_alt_above_ellipsoid()
                    if alt_above_ellipsoid is not None:
                        altitudes.append(alt_above_ellipsoid)
        return altitudes
    
    def get_min_longitude(self) -> Optional[float]:
        """Returns the minimum longitude value from all sentences that contain longitude information."""
        min_lon = min(self.get_longitudes(), default=None)
        return min_lon

    def get_max_longitude(self) -> Optional[float]:
        """Returns the maximum longitude value from all sentences that contain longitude information."""
        max_lon = max(self.get_longitudes(), default=None)
        return max_lon

    def get_min_latitude(self) -> Optional[float]:
        """Returns the minimum latitude value from all sentences that contain latitude information."""
        min_lat = min(self.get_latitudes(), default=None)
        return min_lat

    def get_max_latitude(self) -> Optional[float]:
        """Returns the maximum latitude value from all sentences that contain latitude information."""
        max_lat = max(self.get_latitudes(), default=None)
        return max_lat

    def get_min_altitude(self, reference: str = "geoid") -> Optional[float]:
        """Returns the minimum altitude value from all sentences that contain altitude information."""
        min_alt = min(self.get_altitudes(reference=reference), default=None)
        return min_alt

    def get_max_altitude(self, reference: str = "geoid") -> Optional[float]:
        """Returns the maximum altitude value from all sentences that contain altitude information."""
        max_alt = max(self.get_altitudes(reference=reference), default=None)
        return max_alt

    def get_sentence_with_min_altitude(self, reference: str = "geoid") -> Optional[NMEASentence]:
        """Returns the sentence with the minimum altitude value from all sentences that contain altitude information."""
        min_alt = self.get_min_altitude(reference=reference)
        for sentence in self.format_dict.get('GGA', []):
            if hasattr(sentence, 'altitude') and sentence.altitude == min_alt and sentence.is_valid():
                return sentence
        return None

    def get_sentence_with_max_altitude(self, reference: str = "geoid") -> Optional[NMEASentence]:
        """Returns the sentence with the maximum altitude value from all sentences that contain altitude information."""
        max_alt = self.get_max_altitude(reference=reference)
        for sentence in self.format_dict.get('GGA', []):
            if hasattr(sentence, 'altitude') and sentence.altitude == max_alt and sentence.is_valid():
                return sentence
        return None

    def get_cumulative_altitude_gain(self, reference: str = "geoid") -> float:
        """Returns the cumulative altitude gain across all sentences that contain altitude information."""
        altitudes = self.get_altitudes(reference=reference)
        gain = 0.0
        for i in range(1, len(altitudes)):
            if altitudes[i] > altitudes[i-1]:
                gain += altitudes[i] - altitudes[i-1]
        return gain

    def get_cumulative_altitude_loss(self, reference: str = "geoid") -> float:
        """Returns the cumulative altitude loss across all sentences that contain altitude information."""
        altitudes = self.get_altitudes(reference=reference)
        loss = 0.0
        for i in range(1, len(altitudes)):
            if altitudes[i] < altitudes[i-1]:
                loss += altitudes[i-1] - altitudes[i]
        return loss

    def get_velocities_kmh(self) -> List[float]:
        """Returns a list of all velocity values from sentences that contain velocity information."""
        velocities = []
        for sentence in self.format_dict.get('VTG', []):
            # attribute name is speed_kmh in VTGSentence
            if hasattr(sentence, 'speed_kmh') and sentence.speed_kmh is not None and sentence.is_valid():
                velocities.append(sentence.speed_kmh)
        return velocities

    def get_max_velocity_kmh(self) -> Optional[float]:
        """Returns the maximum velocity value from all sentences that contain velocity information."""
        max_vel = max(self.get_velocities_kmh(), default=None)
        return max_vel
    
    def get_max_sat_elevation(self) -> Optional[float]:
        """Returns the maximum satellite elevation angle from all GSV sentences."""
        max_elev = None
        for sentence in self.format_dict.get('GSV', []):
            if (hasattr(sentence, 'satellite_info') and
                    sentence.satellite_info is not None and sentence.is_valid()):
                for sat in sentence.satellite_info:
                    # sat is a tuple: (prn, elevation, azimuth, snr)
                    if sat and len(sat) >= 2:
                        elev = sat[1]
                        if elev is not None and (max_elev is None or elev > max_elev):
                            max_elev = elev
        return max_elev
    
    def get_distance_travelled(self) -> Optional[float]:
        """Returns the total distance travelled based on the latitude and longitude values from sentences that contain this information. Uses the Haversine formula to calculate distance between consecutive points."""
        coords = []
        invalid_points = 0
        for sentence in self.format_dict.get('GGA', []):
            if hasattr(sentence, 'latitude') and hasattr(sentence, 'longitude') and hasattr(sentence, 'altitude'):
                if sentence.latitude is not None and sentence.longitude is not None and sentence.altitude is not None and sentence.is_valid():
                    coords.append((sentence.latitude, sentence.longitude, sentence.altitude))
                elif not sentence.is_valid():
                    invalid_points += 1
        if len(coords) < 2:
            return None
        print(f"Number of valid coordinate points: {len(coords)}")
        print(f"Number of invalid coordinate points: {invalid_points}")
        # convert to xyz
        total_distance = 0.0
        for i in range(1, len(coords)):
            lat1, lon1, alt1 = coords[i-1]
            lat2, lon2, alt2 = coords[i]
            point1 = WGS84Coords(lat1, lon1, alt1)
            point2 = WGS84Coords(lat2, lon2, alt2)
            total_distance += point1.distance_to(point2)
        return total_distance
