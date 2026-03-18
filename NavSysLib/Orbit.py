# Orbit.py

from dataclasses import dataclass
from typing import Optional
from .utilities import *

@dataclass
class Ephemeris:
    """Class representing satellite ephemeris data."""
    sqrt_a: float = 0.0  # Square root of semi-major axis (m^0.5)
    t_oe: float = 0.0  # Reference epoch time-of-ephemeris (s)
    wn: int = 0  # GPS week number
    M_0: float = 0.0  # Mean anomaly at reference time (rad)
    e: float = 0.0  # Eccentricity
    i_0: float = 0.0  # Orbit inclination angle at reference time (rad)
    Omega_0: float = 0.0  # Longitude of ascending node of orbit plane at weekly epoch (rad)
    omega: float = 0.0  # Argument of perigee (rad)
    d_eta: float = 0.0  # Mean angular velocity correction term (rad/s)
    Omega_dot: float = RIGHT_ASCENSION_RATE  # Rate of right ascension (rad/s)
    C_uc: float = 0.0  # Amplitude of the cosine harmonic correction term to the argument of latitude (rad)
    C_us: float = 0.0  # Amplitude of the sine harmonic correction term to the argument of latitude (rad)
    C_rc: float = 0.0  # Amplitude of the cosine harmonic correction term to the orbit radius (m)
    C_rs: float = 0.0  # Amplitude of the sine harmonic correction
    C_ic: float = 0.0  # Amplitude of the cosine harmonic correction term to the angle of inclination (rad)
    C_is: float = 0.0  # Amplitude of the sine harmonic correction
    idot: float = 0.0  # Rate of change of inclination (rad/s)
    iode: int = 0  # Issue of ephemeris data (0-255)


@dataclass
class Almanac:
    """Class representing satellite almanac data."""
    wn: int = 0  # Almanac week number
    t_oa: float = 0.0  # Reference epoch time-of-almanac (s)
    M_0: float = 0.0  # Mean anomaly at reference time (rad)
    sqrt_a: float = 0.0  # Square root of semi-major axis (m^0.5)
    e: float = 0.0  # Eccentricity
    Omega_0: float = 0.0  # Longitude of ascending node of orbit plane at weekly epoch (rad)
    delta_i: float = 0.0  # Inclination angle at reference time (rad)
    omega: float = 0.0  # Argument of perigee (rad)
    Omega_dot: float = RIGHT_ASCENSION_RATE  # Rate of right ascension (rad/s)
    

@dataclass
class Orbit:
    """Orbit model derived from Ephemeris and/or Almanac."""

    ephemeris: Optional[Ephemeris] = None  # Ephemeris source data
    almanac: Optional[Almanac] = None  # Almanac source data
    mu: float = MU  # Earth GM (m^3/s^2)

    def __post_init__(self):
        """Infer missing orbit source fields from available source data."""
        self._normalize_sources()

    def _fill_zero_from_other(self, target, source, field_pairs):
        """Copy source values into zero-valued target fields when possible."""
        for target_field, source_field in field_pairs:
            target_value = getattr(target, target_field)
            source_value = getattr(source, source_field)
            if target_value == 0 and source_value != 0:
                setattr(target, target_field, source_value)

    def _normalize_sources(self):
        """Build and cross-fill ephemeris/almanac where values can be inferred."""
        if self.ephemeris is None and self.almanac is None:
            return

        if self.ephemeris is None and self.almanac is not None:
            self.ephemeris = Ephemeris(
                sqrt_a=self.almanac.sqrt_a,
                t_oe=self.almanac.t_oa,
                wn=self.almanac.wn,
                M_0=self.almanac.M_0,
                e=self.almanac.e,
                i_0=self.almanac.delta_i,
                Omega_0=self.almanac.Omega_0,
                omega=self.almanac.omega,
                Omega_dot=self.almanac.Omega_dot,
                d_eta=0.0,
            )

        if self.almanac is None and self.ephemeris is not None:
            self.almanac = Almanac(
                wn=self.ephemeris.wn,
                t_oa=self.ephemeris.t_oe,
                M_0=self.ephemeris.M_0,
                sqrt_a=self.ephemeris.sqrt_a,
                e=self.ephemeris.e,
                Omega_0=self.ephemeris.Omega_0,
                delta_i=self.ephemeris.i_0,
                omega=self.ephemeris.omega,
                Omega_dot=self.ephemeris.Omega_dot,
            )

        self._fill_zero_from_other(
            self.ephemeris,
            self.almanac,
            [
                ("sqrt_a", "sqrt_a"),
                ("t_oe", "t_oa"),
                ("wn", "wn"),
                ("M_0", "M_0"),
                ("e", "e"),
                ("i_0", "delta_i"),
                ("Omega_0", "Omega_0"),
                ("omega", "omega"),
                ("Omega_dot", "Omega_dot"),
            ],
        )

        self._fill_zero_from_other(
            self.almanac,
            self.ephemeris,
            [
                ("sqrt_a", "sqrt_a"),
                ("t_oa", "t_oe"),
                ("wn", "wn"),
                ("M_0", "M_0"),
                ("e", "e"),
                ("delta_i", "i_0"),
                ("Omega_0", "Omega_0"),
                ("omega", "omega"),
                ("Omega_dot", "Omega_dot"),
            ],
        )

    @classmethod
    def from_orbital_parameters(
        cls,
        a: float,
        e: float,
        arg_perigee: float = 0.0,
        i: float = 0.0,
        raan: float = 0.0,
        M0: float = 0.0,
        toe: float = 0.0,
        delta_n: float = 0.0,
        wn: int = 0,
        mu: float = MU,
    ):
        """Create Orbit from direct orbital parameters."""
        if a <= 0.0:
            raise ValueError("a must be positive")

        eph = Ephemeris(
            sqrt_a=a ** 0.5,
            t_oe=toe,
            wn=wn,
            M_0=M0,
            e=e,
            i_0=i,
            Omega_0=raan,
            omega=arg_perigee,
            d_eta=delta_n,
        )
        return cls(ephemeris=eph, mu=mu)

    def _source(self):
        """Return preferred source object (ephemeris first, then almanac)."""
        if self.ephemeris is not None:
            return self.ephemeris
        if self.almanac is not None:
            return self.almanac
        raise ValueError("Orbit requires ephemeris or almanac")

    def semimajor_axis(self) -> float:
        """Return semi-major axis a in meters."""
        return self._source().sqrt_a ** 2

    def eccentricity(self) -> float:
        """Return orbital eccentricity."""
        return self._source().e
    
    def delta_t(self, wn: int, tow_s: float) -> float:
        """Return time difference in seconds between given GPS epoch and orbit reference epoch."""
        return gps_delta_t(wn, tow_s, self.week_number(), self.reference_tow())

    def inclination(self, wn: Optional[int] = None, tow: Optional[float] = None, arg_lat: Optional[float] = None) -> float:
        """Return inclination in radians, accounting for idot time evolution and harmonic terms."""
        src = self._source()
        if isinstance(src, Ephemeris):
            i_0 = src.i_0
            if tow is not None and wn is not None and arg_lat is not None:
                i_0 += src.idot * self.delta_t(wn, tow)
            i_0 += src.C_ic * np.cos(2 * arg_lat) + src.C_is * np.sin(2 * arg_lat)
            return i_0
        return src.delta_i

    def right_ascension(self, wn: Optional[int] = None, tow: Optional[float] = None) -> float:
        """Return right ascension of ascending node in radians, accounting for Omega_dot time evolution."""
        Omega_0 = self._source().Omega_0
        if self.ephemeris is not None and tow is not None and wn is not None:
            Omega_0 += self.ephemeris.Omega_dot * self.delta_t(self.ephemeris.wn, tow)
        return Omega_0
    
    def longitude_of_ascending_node(self, wn: int, tow: float) -> float:
        """Return longitude of ascending node in radians, accounting for Omega_dot time evolution."""
        return self.right_ascension(wn=wn, tow=tow) - EARTH_ROT_RATE * (self.delta_t(wn, tow) + self.reference_tow())

    def argument_of_perigee(self) -> float:
        """Return argument of perigee in radians."""
        return self._source().omega

    def reference_tow(self) -> float:
        """Return reference TOW in seconds (toe for ephemeris, toa for almanac)."""
        src = self._source()
        if isinstance(src, Ephemeris):
            return src.t_oe
        return src.t_oa

    def mean_anomaly_reference(self) -> float:
        """Return reference mean anomaly M0 in radians."""
        return self._source().M_0

    def week_number(self) -> int:
        """Return week number."""
        return self._source().wn

    def delta_eta(self) -> float:
        """Return mean motion correction delta_n in rad/s."""
        if self.ephemeris is not None:
            return self.ephemeris.d_eta
        return 0.0

    def period(self) -> float:
        """Return orbital period T in seconds."""
        return orbital_period(self.semimajor_axis(), mu=self.mu)

    def mean_angular_velocity(self) -> float:
        """Return mean angular velocity eta in rad/s."""
        return mean_angular_velocity(self.semimajor_axis(), d_eta=self.delta_eta(), mu=self.mu)

    def mean_anomaly_at_time(self, time_since_perigee_s: float) -> float:
        """Return mean anomaly M in radians for elapsed time since perigee passage."""
        M = self.mean_angular_velocity() * time_since_perigee_s
        return M

    def mean_anomaly_at_tow(self, wn: int, tow: float) -> float:
        """Return mean anomaly M in radians at given TOW using toe, M0 and corrected mean motion."""
        d_t = self.delta_t(wn, tow)
        M = mean_anomaly_M0(self.mean_anomaly_reference(), d_t, self.mean_angular_velocity())
        return M

    def eccentric_anomaly_from_mean(self, M_rad: float, tol: float = 1e-12, max_iter: int = 50) -> float:
        """Solve Kepler's equation M = E - e sin(E) for E in radians."""
        return eccentric_anomaly(M_rad, self.eccentricity(), tol=tol, max_iter=max_iter)

    def orbital_radius(self, E_rad: float, arg_lat: Optional[float] = None) -> float:
        """Calculate orbital radius r from eccentric anomaly E, corrected for harmonic terms."""
        r_0 = orbital_radius(self.semimajor_axis(), self.eccentricity(), E_rad)
        if self.ephemeris is not None and arg_lat is not None:
            r_0 += self.ephemeris.C_rc * np.cos(2 * arg_lat) + self.ephemeris.C_rs * np.sin(2 * arg_lat)
        return r_0

    def true_anomaly(self, E_rad: float) -> float:
        """Calculate true anomaly v from eccentric anomaly E."""
        return true_anomaly(E_rad, self.eccentricity())

    def argument_of_latitude(self, true_anomaly_rad: float) -> float:
        """Return argument of latitude phi = omega + v in radians, accounting for C_uc/C_us corrections."""
        arg = self.argument_of_perigee() + true_anomaly_rad
        return arg
    
    def argument_of_latitude_corrected(self, arg_latitude_rad: float) -> float:
        """Return argument of latitude phi corrected for harmonic terms."""
        if self.ephemeris is not None:
            arg_latitude_rad += self.ephemeris.C_uc * np.cos(2 * arg_latitude_rad) + self.ephemeris.C_us * np.sin(2 * arg_latitude_rad)
        return arg_latitude_rad

    def parameters_at_time(self, t_since_perigee_s: float) -> dict:
        """Return all common exercise orbital parameters at elapsed time since perigee.
        
        Returns:
            dict with keys: T, eta, M, E, r, true_anomaly, arg_latitude
        """
        T = self.period()
        eta = self.mean_angular_velocity()
        M = self.mean_anomaly_at_time(t_since_perigee_s)
        E = self.eccentric_anomaly_from_mean(M)
        r = self.orbital_radius(E)
        phi_0 = self.true_anomaly(E)
        phi = self.argument_of_latitude(phi_0)

        return {
            "T": T,
            "eta": eta,
            "M": M,
            "E": E,
            "r": r,
            "true_anomaly": phi_0,
            "arg_latitude": phi,
        }

    def perigee_tow_near_toe(self) -> float:
        """Return perigee TOW (s) corresponding to the toe branch."""
        return perigee_tow_from_toe(self.reference_tow(), self.mean_anomaly_reference(), self.mean_angular_velocity())

    def first_perigee_tow_in_week(self, week_seconds: float = 604800.0) -> float:
        """Return first perigee TOW (s) within GPS week bounds."""
        return first_perigee_tow_in_week(self.reference_tow(), self.mean_anomaly_reference(), self.mean_angular_velocity(), week_seconds=week_seconds)

    def wgs84_position(self, wn=0, tow=0) -> tuple:
        """Return ECEF position (x, y, z) in meters, accounting for harmonic corrections."""
        a = self.semimajor_axis()
        eta = self.mean_angular_velocity()
        d_t = self.delta_t(wn, tow)
        M = self.mean_anomaly_reference() + eta * d_t
        E = self.eccentric_anomaly_from_mean(M)
        phi_0 = self.true_anomaly(E)
        phi = self.argument_of_latitude(phi_0)
        u = self.argument_of_latitude_corrected(phi)
        r = self.orbital_radius(E)
        i = self.inclination(wn, tow, arg_lat=phi)
        Omega = self.longitude_of_ascending_node(wn, tow)

        print(f"a: {a}\neta: {eta}\nd_t: {d_t}\nM: {M}\nE: {E}\nphi_0: {phi_0}\nphi: {phi}\nu: {u}\nr: {r}\ni: {i}\nOmega: {Omega}")

        ecef_vec = np.array([r * np.cos(u), r * np.sin(u), 0.0]) @ rot_x(-i) @ rot_z(-Omega)
        return tuple(ecef_vec)




