""" Unit tests for NavSysLib/utilities.py """

import numpy as np
import pytest
from datetime import date, time, datetime
from NavSysLib.utilities import *


###############################################################################
# E1
###############################################################################

# ---------------------------------------------------------
# Safe conversion functions
# ---------------------------------------------------------

def test_safe_int_valid():
    """Test safe_int with valid string integers"""
    assert safe_int("42") == 42
    assert safe_int("0") == 0
    assert safe_int("-100") == -100
    assert safe_int("999999") == 999999

def test_safe_int_invalid():
    """Test safe_int with invalid inputs"""
    assert safe_int("abc") is None
    assert safe_int("12.5") is None
    assert safe_int("") is None
    assert safe_int("12a") is None
    assert safe_int(None) is None

def test_safe_float_valid():
    """Test safe_float with valid string floats"""
    assert safe_float("3.14") == pytest.approx(3.14)
    assert safe_float("0.0") == pytest.approx(0.0)
    assert safe_float("-2.5") == pytest.approx(-2.5)
    assert safe_float("1e5") == pytest.approx(100000.0)
    assert safe_float("42") == pytest.approx(42.0)

def test_safe_float_invalid():
    """Test safe_float with invalid inputs"""
    assert safe_float("abc") is None
    assert safe_float("1.2.3") is None
    assert safe_float("") is None
    assert safe_float(None) is None

# ---------------------------------------------------------
# NMEA conversion functions
# ---------------------------------------------------------

def test_dm_to_deg_latitude_format():
    """Test dm_to_deg with latitude format (ddmm.mmmm)"""
    # 5530.5 = 55 degrees 30.5 minutes = 55.50833...
    result = dm_to_deg("5530.5")
    assert result == pytest.approx(55.50833333, abs=1e-6)
    
    # 0000.0 = 0 degrees
    assert dm_to_deg("0000.0") == pytest.approx(0.0)
    
    # 8945.0 = 89 degrees 45 minutes = 89.75
    assert dm_to_deg("8945.0") == pytest.approx(89.75)

def test_dm_to_deg_longitude_format():
    """Test dm_to_deg with longitude format (dddmm.mmmm)"""
    # 01230.5 = 12 degrees 30.5 minutes = 12.50833...
    result = dm_to_deg("01230.5")
    assert result == pytest.approx(12.50833333, abs=1e-6)
    
    # 12030.0 = 120 degrees 30 minutes = 120.5
    assert dm_to_deg("12030.0") == pytest.approx(120.5)

def test_dm_to_deg_edge_cases():
    """Test dm_to_deg with edge cases"""
    # Empty string
    assert dm_to_deg("") is None
    assert dm_to_deg(None) is None
    
    # Invalid format
    assert dm_to_deg("abc") is None
    assert dm_to_deg("invalid") is None

def test_nmea_str_to_datetime_time_only():
    """Test nmea_str_to_datetime with time-only format (hhmmss)"""
    result = nmea_str_to_datetime("110259")
    assert result.hour == 11
    assert result.minute == 2
    assert result.second == 59

def test_nmea_str_to_datetime_date_and_time():
    """Test nmea_str_to_datetime with date and time format (ddmmyyhhmmss)"""
    result = nmea_str_to_datetime("250913110259")
    assert result.day == 25
    assert result.month == 9
    assert result.year == 2013
    assert result.hour == 11
    assert result.minute == 2
    assert result.second == 59

def test_nmea_str_to_datetime_invalid():
    """Test nmea_str_to_datetime with invalid inputs"""
    assert nmea_str_to_datetime("") is None
    assert nmea_str_to_datetime("123") is None  # Too short
    assert nmea_str_to_datetime("abc") is None
    assert nmea_str_to_datetime(None) is None

def test_nmea_str_to_date():
    """Test nmea_str_to_date conversion"""
    result = nmea_str_to_date("250913")
    assert isinstance(result, date)
    assert result.day == 25
    assert result.month == 9
    assert result.year == 2013

def test_nmea_str_to_date_invalid():
    """Test nmea_str_to_date with invalid inputs"""
    assert nmea_str_to_date("") is None
    assert nmea_str_to_date("abc") is None
    assert nmea_str_to_date("not a date") is None

def test_nmea_str_to_time():
    """Test nmea_str_to_time conversion"""
    result = nmea_str_to_time("110259.600")
    assert isinstance(result, time)
    assert result.hour == 11
    assert result.minute == 2
    assert result.second == 59
    assert result.microsecond == 600000

def test_nmea_str_to_time_alternate():
    """Test nmea_str_to_time with different time values"""
    result = nmea_str_to_time("000000.000")
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0

def test_nmea_str_to_time_invalid():
    """Test nmea_str_to_time with invalid inputs"""
    assert nmea_str_to_time("") is None
    assert nmea_str_to_time("12:34:56") is None  # Wrong format
    assert nmea_str_to_time("abc") is None
    assert nmea_str_to_time(None) is None

def test_knots_to_kmh_valid():
    """Test knots to km/h conversion with valid inputs"""
    # 1 knot = 1.852 km/h
    assert knots_to_kmh(1.0) == pytest.approx(1.852)
    assert knots_to_kmh(0.0) == pytest.approx(0.0)
    assert knots_to_kmh(10.0) == pytest.approx(18.52)
    assert knots_to_kmh(100.0) == pytest.approx(185.2)

def test_knots_to_kmh_negative():
    """Test knots to km/h with negative values"""
    assert knots_to_kmh(-1.0) == pytest.approx(-1.852)
    assert knots_to_kmh(-10.0) == pytest.approx(-18.52)

def test_knots_to_kmh_none():
    """Test knots to km/h with None input"""
    assert knots_to_kmh(None) is None

###############################################################################
# E2
###############################################################################


#---------------------------------------------------------------------
# WGS-84 non-constants
#---------------------------------------------------------------------

def test_wgs84_radius_of_curvature():
    """Test radius of curvature at equator and at 45 deg latitude"""
    # At equator RN should equal WGS84_A
    RN_eq = wgs84_radius_of_curvature(0.0)
    assert RN_eq == pytest.approx(WGS84_A, rel=1e-10)

    # At a non-zero latitude, RN should be larger than a (WGS-84 is oblate)
    RN_45 = wgs84_radius_of_curvature(np.deg2rad(45))
    assert RN_45 > WGS84_A

def test_wgs84_circumference_at_lat():
    """Test circumference at equator and at 60 deg latitude"""
    # Equator circumference ≈ 2*pi*a
    circ_eq = wgs84_circumference_at_lat(0.0)
    assert circ_eq == pytest.approx(2 * np.pi * WGS84_A, rel=1e-6)

    # At 60 deg the circumference should be roughly half the equatorial
    circ_60 = wgs84_circumference_at_lat(np.deg2rad(60))
    assert circ_60 == pytest.approx(circ_eq / 2, rel=1e-2)


# ---------------------------------------------------------------------
# Distance
# ---------------------------------------------------------------------

def test_euclidean_distance():
    """Test euclidean distance with known values"""
    # Same point -> 0
    assert euclidean_distance(0, 0, 0, 0, 0, 0) == pytest.approx(0.0)

    # Unit distance along each axis
    assert euclidean_distance(0, 0, 0, 1, 0, 0) == pytest.approx(1.0)
    assert euclidean_distance(0, 0, 0, 0, 1, 0) == pytest.approx(1.0)
    assert euclidean_distance(0, 0, 0, 0, 0, 1) == pytest.approx(1.0)

    # 3-4-5 triangle in 2D (z=0)
    assert euclidean_distance(0, 0, 0, 3, 4, 0) == pytest.approx(5.0)

    # 3D diagonal
    assert euclidean_distance(1, 2, 3, 4, 6, 3) == pytest.approx(5.0)


# ---------------------------------------------------------------------
# Angle utilities
# ---------------------------------------------------------------------

def test_deg2rad():
    """Test degree to radian conversion"""
    assert deg2rad(0) == pytest.approx(0.0)
    assert deg2rad(180) == pytest.approx(np.pi)
    assert deg2rad(90) == pytest.approx(np.pi / 2)
    assert deg2rad(360) == pytest.approx(2 * np.pi)
    assert deg2rad(-90) == pytest.approx(-np.pi / 2)

def test_rad2deg():
    """Test radian to degree conversion"""
    assert rad2deg(0) == pytest.approx(0.0)
    assert rad2deg(np.pi) == pytest.approx(180.0)
    assert rad2deg(np.pi / 2) == pytest.approx(90.0)
    assert rad2deg(2 * np.pi) == pytest.approx(360.0)

def test_dms_to_decimal():
    """Test DMS to decimal degrees conversion"""
    # 45° 30' 36" = 45.51°
    assert dms_to_decimal(45, 30, 36) == pytest.approx(45.51, abs=1e-10)

    # 0° 0' 0" = 0.0
    assert dms_to_decimal(0, 0, 0) == pytest.approx(0.0)

    # Negative sign: -45° 30' 36" = -45.51
    assert dms_to_decimal(45, 30, 36, sign=-1) == pytest.approx(-45.51, abs=1e-10)

    # 90° 0' 0" = 90.0
    assert dms_to_decimal(90, 0, 0) == pytest.approx(90.0)

def test_decimal_to_dms():
    """Test decimal degrees to DMS conversion"""
    sign, d, m, s = decimal_to_dms(45.51)
    assert sign == 1
    assert d == 45
    assert m == 30
    assert s == pytest.approx(36.0, abs=1e-6)

    # Negative
    sign, d, m, s = decimal_to_dms(-45.51)
    assert sign == -1
    assert d == 45
    assert m == 30
    assert s == pytest.approx(36.0, abs=1e-6)

    # Zero
    sign, d, m, s = decimal_to_dms(0.0)
    assert d == 0
    assert m == 0
    assert s == pytest.approx(0.0, abs=1e-6)

def test_decimal_to_dm():
    """Test decimal degrees to DM conversion"""
    sign, d, minutes = decimal_to_dm(45.5)
    assert sign == 1
    assert d == 45
    assert minutes == pytest.approx(30.0, abs=1e-10)

    # Negative
    sign, d, minutes = decimal_to_dm(-45.5)
    assert sign == -1
    assert d == 45
    assert minutes == pytest.approx(30.0, abs=1e-10)


# ---------------------------------------------------------------------
# Geodetic <-> ECEF
# ---------------------------------------------------------------------

def test_ecef_to_long():
    """Test longitude extraction from ECEF coordinates"""
    # On the prime meridian (y=0, x>0) -> lon = 0
    assert ecef_to_long(WGS84_A, 0) == pytest.approx(0.0, abs=1e-10)

    # On the 90° E meridian (x=0, y>0) -> lon = pi/2
    assert ecef_to_long(0, WGS84_A) == pytest.approx(np.pi / 2, abs=1e-10)

    # On the 180° meridian (x<0, y=0) -> lon = pi
    assert ecef_to_long(-WGS84_A, 0) == pytest.approx(np.pi, abs=1e-10)

def test_ecef_to_lat_bowring():
    """Test Bowring latitude from ECEF, using a known point on the equator and at pole"""
    # Point on equator, prime meridian, h=0
    x, y, z = llh_to_ecef(0.0, 0.0, 0.0)
    lat = ecef_to_lat_bowring(x, y, z)
    assert lat == pytest.approx(0.0, abs=1e-8)

    # Point at North Pole
    x, y, z = llh_to_ecef(np.pi / 2, 0.0, 0.0)
    lat = ecef_to_lat_bowring(x, y, z)
    assert lat == pytest.approx(np.pi / 2, abs=1e-8)

    # Mid-latitude: 45 deg N
    lat_in = np.deg2rad(45.0)
    x, y, z = llh_to_ecef(lat_in, 0.0, 0.0)
    lat = ecef_to_lat_bowring(x, y, z)
    assert lat == pytest.approx(lat_in, abs=1e-8)

def test_ecef_to_lat_heikkinen():
    """Test Heikkinen latitude from ECEF, using a known point on the equator and at pole"""
    # Point on equator
    x, y, z = llh_to_ecef(0.0, 0.0, 0.0)
    lat = ecef_to_lat_heikkinen(x, y, z)
    assert lat == pytest.approx(0.0, abs=1e-8)

    # Point at North Pole
    x, y, z = llh_to_ecef(np.pi / 2, 0.0, 0.0)
    lat = ecef_to_lat_heikkinen(x, y, z)
    assert lat == pytest.approx(np.pi / 2, abs=1e-8)

    # Mid-latitude: 45 deg N
    lat_in = np.deg2rad(45.0)
    x, y, z = llh_to_ecef(lat_in, 0.0, 0.0)
    lat = ecef_to_lat_heikkinen(x, y, z)
    assert lat == pytest.approx(lat_in, abs=1e-8)

def test_ecef_to_llh():
    """Test round-trip ECEF->LLH using Bowring and Heikkinen methods"""
    # Known geodetic point: Trondheim approx (63.43°N, 10.40°E, 50m)
    lat_in = np.deg2rad(63.43)
    lon_in = np.deg2rad(10.40)
    h_in = 50.0

    x, y, z = llh_to_ecef(lat_in, lon_in, h_in)

    # Bowring
    lat, lon, h = ecef_to_llh(x, y, z, method='bowring')
    assert lat == pytest.approx(lat_in, abs=1e-8)
    assert lon == pytest.approx(lon_in, abs=1e-8)
    assert h == pytest.approx(h_in, abs=1e-3)

    # Heikkinen
    lat, lon, h = ecef_to_llh(x, y, z, method='heikkinen')
    assert lat == pytest.approx(lat_in, abs=1e-8)
    assert lon == pytest.approx(lon_in, abs=1e-8)
    assert h == pytest.approx(h_in, abs=1e-3)

def test_llh_to_ecef():
    """Test LLH to ECEF conversion at equator/prime meridian"""
    # At equator, prime meridian, h=0 -> x = a, y = 0, z = 0
    x, y, z = llh_to_ecef(0.0, 0.0, 0.0)
    assert x == pytest.approx(WGS84_A, rel=1e-10)
    assert y == pytest.approx(0.0, abs=1e-6)
    assert z == pytest.approx(0.0, abs=1e-6)

    # At North Pole, h=0 -> x ≈ 0, y ≈ 0, z ≈ b
    x, y, z = llh_to_ecef(np.pi / 2, 0.0, 0.0)
    assert x == pytest.approx(0.0, abs=1e-6)
    assert y == pytest.approx(0.0, abs=1e-6)
    assert z == pytest.approx(WGS84_B, rel=1e-10)

    # Round-trip check at an arbitrary point
    lat_in = np.deg2rad(51.5)
    lon_in = np.deg2rad(-0.1)
    h_in = 100.0
    x, y, z = llh_to_ecef(lat_in, lon_in, h_in)
    lat, lon, h = ecef_to_llh(x, y, z)
    assert lat == pytest.approx(lat_in, abs=1e-8)
    assert lon == pytest.approx(lon_in, abs=1e-8)
    assert h == pytest.approx(h_in, abs=1e-3)


# ---------------------------------------------------------------------
# ENU frame
# ---------------------------------------------------------------------

def test_rot_x():
    """Test rotation matrix about x-axis"""
    # Identity for 0 angle
    R = rot_x(0.0)
    np.testing.assert_array_almost_equal(R, np.eye(3))

    # 90 deg rotation: y->z, z->-y
    R = rot_x(np.pi / 2)
    v = R @ np.array([0, 1, 0])
    np.testing.assert_array_almost_equal(v, [0, 0, 1], decimal=10)

def test_rot_y():
    """Test rotation matrix about y-axis"""
    R = rot_y(0.0)
    np.testing.assert_array_almost_equal(R, np.eye(3))

    # 90 deg rotation: z->x, x->-z
    R = rot_y(np.pi / 2)
    v = R @ np.array([0, 0, 1])
    np.testing.assert_array_almost_equal(v, [1, 0, 0], decimal=10)

def test_rot_z():
    """Test rotation matrix about z-axis"""
    R = rot_z(0.0)
    np.testing.assert_array_almost_equal(R, np.eye(3))

    # 90 deg rotation: x->y, y->-x
    R = rot_z(np.pi / 2)
    v = R @ np.array([1, 0, 0])
    np.testing.assert_array_almost_equal(v, [0, 1, 0], decimal=10)

def test_ecef_to_enu():
    """Test ECEF to ENU conversion: a delta vector pointing North at equator/prime meridian"""
    lat_ref = 0.0
    lon_ref = 0.0
    # A small delta in the z-direction in ECEF at equator/prime meridian = North in ENU
    enu = ecef_to_enu(0, 0, 1, lat_ref, lon_ref)
    assert enu[0] == pytest.approx(0.0, abs=1e-10)  # East
    assert enu[1] == pytest.approx(1.0, abs=1e-10)  # North
    assert enu[2] == pytest.approx(0.0, abs=1e-10)  # Up

def test_enu_to_ecef():
    """Test ENU to ECEF conversion: round-trip with ecef_to_enu"""
    lat_ref = np.deg2rad(63.43)
    lon_ref = np.deg2rad(10.40)
    e_in, n_in, u_in = 100.0, 200.0, 50.0

    dx, dy, dz = enu_to_ecef(e_in, n_in, u_in, lat_ref, lon_ref)
    enu_out = ecef_to_enu(dx, dy, dz, lat_ref, lon_ref)

    assert enu_out[0] == pytest.approx(e_in, abs=1e-6)
    assert enu_out[1] == pytest.approx(n_in, abs=1e-6)
    assert enu_out[2] == pytest.approx(u_in, abs=1e-6)

def test_az():
    """Test azimuth calculation from ENU components"""
    # Due North: e=0, n=1 -> az=0
    assert az(0, 1) == pytest.approx(0.0, abs=1e-10)
    # Due East: e=1, n=0 -> az=90
    assert az(1, 0) == pytest.approx(90.0, abs=1e-10)
    # Due South: e=0, n=-1 -> az=180
    assert az(0, -1) == pytest.approx(180.0, abs=1e-10)
    # Due West: e=-1, n=0 -> az=-90
    assert az(-1, 0) == pytest.approx(-90.0, abs=1e-10)

def test_el():
    """Test elevation calculation from ENU components"""
    # Horizontal: u=0 -> el=0
    assert el(1, 0, 0) == pytest.approx(0.0, abs=1e-10)
    # Straight up: e=0, n=0, u=1 -> el=90
    assert el(0, 0, 1) == pytest.approx(90.0, abs=1e-10)
    # 45 degrees: e=1, n=0, u=1 -> el=45
    assert el(1, 0, 1) == pytest.approx(45.0, abs=1e-10)

def test_enu_to_az_el():
    """Test combined azimuth/elevation from ENU"""
    azimuth, elevation = enu_to_az_el(1, 0, 1)
    assert azimuth == pytest.approx(90.0, abs=1e-10)
    assert elevation == pytest.approx(45.0, abs=1e-10)

def test_enu_to_az_el_range():
    """Test azimuth, elevation and range from ENU"""
    azimuth, elevation, range_m = enu_to_az_el_range(1, 0, 0)
    assert azimuth == pytest.approx(90.0, abs=1e-10)
    assert elevation == pytest.approx(0.0, abs=1e-10)
    assert range_m == pytest.approx(1.0, abs=1e-10)

    # 3D vector
    azimuth, elevation, range_m = enu_to_az_el_range(3, 4, 0)
    assert range_m == pytest.approx(5.0, abs=1e-10)

def test_az_el_range_to_enu():
    """Test round-trip: az/el/range -> ENU -> az/el/range"""
    az_in, el_in, r_in = 45.0, 30.0, 1000.0
    e, n, u = az_el_range_to_enu(az_in, el_in, r_in)
    az_out, el_out, r_out = enu_to_az_el_range(e, n, u)

    assert az_out == pytest.approx(az_in, abs=1e-8)
    assert el_out == pytest.approx(el_in, abs=1e-8)
    assert r_out == pytest.approx(r_in, abs=1e-6)


# ---------------------------------------------------------------------
# Datum transformations
# ---------------------------------------------------------------------

def test_molodensky_transform():
    """Test Molodensky transform with zero shifts returns original coordinates"""
    lat_in = np.deg2rad(60.0)
    lon_in = np.deg2rad(10.0)
    h_in = 100.0

    # Zero transformation -> output should equal input
    lat_out, lon_out, h_out = molodensky_transform(
        lat_in, lon_in, h_in,
        da=0, df=0, dX=0, dY=0, dZ=0
    )
    assert lat_out == pytest.approx(lat_in, abs=1e-12)
    assert lon_out == pytest.approx(lon_in, abs=1e-12)
    assert h_out == pytest.approx(h_in, abs=1e-6)

    # Non-zero shifts should change the coordinates
    lat_out2, lon_out2, h_out2 = molodensky_transform(
        lat_in, lon_in, h_in,
        da=-23, df=-0.00000008121, dX=-87, dY=-98, dZ=-121
    )
    assert lat_out2 != pytest.approx(lat_in, abs=1e-10)
    assert lon_out2 != pytest.approx(lon_in, abs=1e-10)

def test_ecef_datum_transform():
    """Test ECEF datum transformation with zero translation"""
    lat_in = np.deg2rad(60.0)
    lon_in = np.deg2rad(10.0)
    h_in = 100.0

    # Zero translation between same datum -> output should equal input
    lat_out, lon_out, h_out = ecef_datum_transform(
        lat_in, lon_in, h_in,
        dX=0, dY=0, dZ=0,
        a2=WGS84_A, f2=WGS84_F,
        a1=WGS84_A, f1=WGS84_F
    )
    assert lat_out == pytest.approx(lat_in, abs=1e-8)
    assert lon_out == pytest.approx(lon_in, abs=1e-8)
    assert h_out == pytest.approx(h_in, abs=1e-3)

def test_ecef_datum_transform_with_translation():
    """Test ECEF datum transformation with non-zero translation"""
    lat_in = np.deg2rad(60.0)
    lon_in = np.deg2rad(10.0)
    h_in = 100.0

    # Non-zero translation should change the coordinates
    lat_out, lon_out, h_out = ecef_datum_transform(
        lat_in, lon_in, h_in,
        dX=100, dY=100, dZ=100,
        a2=WGS84_A, f2=WGS84_F,
        a1=WGS84_A, f1=WGS84_F
    )
    # Verify coordinates changed
    assert lat_out != pytest.approx(lat_in, abs=1e-8)
    assert lon_out != pytest.approx(lon_in, abs=1e-8)
    assert h_out != pytest.approx(h_in, abs=1e-3)


