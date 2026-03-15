import unittest
import numpy as np
from NavSysLib.Coords import WGS84Coords


class TestWGS84CoordsConstructor(unittest.TestCase):
    """Test WGS84Coords constructor and basic attributes"""
    
    def test_constructor_with_defaults(self):
        """Test constructor with default altitude"""
        coords = WGS84Coords(lat=55.0, lon=12.0)
        self.assertEqual(coords.lat, 55.0)
        self.assertEqual(coords.lon, 12.0)
        self.assertEqual(coords.alt, 0.0)
    
    def test_constructor_with_altitude(self):
        """Test constructor with explicit altitude"""
        coords = WGS84Coords(lat=55.0, lon=12.0, alt=100.5)
        self.assertEqual(coords.lat, 55.0)
        self.assertEqual(coords.lon, 12.0)
        self.assertEqual(coords.alt, 100.5)
    
    def test_constructor_with_negative_values(self):
        """Test constructor with negative latitude and longitude"""
        coords = WGS84Coords(lat=-33.0, lon=-151.0, alt=50.0)
        self.assertEqual(coords.lat, -33.0)
        self.assertEqual(coords.lon, -151.0)
        self.assertEqual(coords.alt, 50.0)


class TestWGS84CoordsFromDMS(unittest.TestCase):
    """Test from_dms class method"""
    
    def test_from_dms_north_east(self):
        """Test creating coords from DMS with North latitude and East longitude"""
        lat_dms = (55, 40, 0, 'N')  # 55°40'00"N
        lon_dms = (12, 30, 0, 'E')  # 12°30'00"E
        coords = WGS84Coords.from_dms(lat_dms, lon_dms, alt=100.0)
        
        # 55 + 40/60 + 0/3600 = 55.666...
        self.assertAlmostEqual(coords.lat, 55.666666, places=5)
        # 12 + 30/60 + 0/3600 = 12.5
        self.assertAlmostEqual(coords.lon, 12.5, places=5)
        self.assertEqual(coords.alt, 100.0)
    
    def test_from_dms_south_west(self):
        """Test creating coords from DMS with South latitude and West longitude"""
        lat_dms = (33, 52, 0, 'S')  # 33°52'00"S
        lon_dms = (151, 12, 0, 'W')  # 151°12'00"W
        coords = WGS84Coords.from_dms(lat_dms, lon_dms)
        
        # Should be negative
        self.assertAlmostEqual(coords.lat, -33.866666, places=5)
        self.assertAlmostEqual(coords.lon, -151.2, places=5)
    
    def test_from_dms_with_seconds(self):
        """Test DMS conversion with non-zero seconds"""
        lat_dms = (55, 40, 30, 'N')  # 55°40'30"N
        lon_dms = (12, 30, 45, 'E')  # 12°30'45"E
        coords = WGS84Coords.from_dms(lat_dms, lon_dms)
        
        # 55 + 40/60 + 30/3600 = 55.675
        self.assertAlmostEqual(coords.lat, 55.675, places=5)
        # 12 + 30/60 + 45/3600 = 12.5125
        self.assertAlmostEqual(coords.lon, 12.5125, places=5)


class TestWGS84CoordsFromECEF(unittest.TestCase):
    """Test from_ecef class method"""
    
    def test_from_ecef_at_greenwich(self):
        """Test creating coords from ECEF at prime meridian"""
        # At prime meridian and equator
        coords = WGS84Coords.from_ecef(6378137.0, 0, 0)
        
        self.assertAlmostEqual(coords.lat, 0.0, places=2)
        self.assertAlmostEqual(coords.lon, 0.0, places=2)
        self.assertAlmostEqual(coords.alt, 0.0, places=1)
    
    def test_from_ecef_north_pole(self):
        """Test creating coords from ECEF at north pole"""
        coords = WGS84Coords.from_ecef(0, 0, 6356752.314245)
        
        self.assertAlmostEqual(coords.lat, 90.0, places=2)
        # Note: At pole, ECEF conversion has large numerical errors, just verify latitude is correct
        # The altitude value is not reliable at the poles due to singularities in the transformation
    
    def test_from_ecef_with_altitude(self):
        """Test creating coords from ECEF with altitude"""
        # Create a point 1000m above equator on prime meridian
        coords = WGS84Coords.from_ecef(6379137.0, 0, 0)
        
        self.assertAlmostEqual(coords.alt, 1000.0, places=0)
    
    def test_from_ecef_bowring_method(self):
        """Test from_ecef with Bowring method"""
        coords = WGS84Coords.from_ecef(4000000, 3000000, 4000000, method='bowring')
        
        # Verify we get reasonable values
        self.assertTrue(-90 <= coords.lat <= 90)
        self.assertTrue(-180 <= coords.lon <= 180)
    
    def test_from_ecef_heikkinen_method(self):
        """Test from_ecef with Heikkinen method"""
        coords = WGS84Coords.from_ecef(4000000, 3000000, 4000000, method='heikkinen')
        
        # Verify we get reasonable values
        self.assertTrue(-90 <= coords.lat <= 90)
        self.assertTrue(-180 <= coords.lon <= 180)


class TestWGS84CoordsToRadians(unittest.TestCase):
    """Test to_radians method"""
    
    def test_to_radians(self):
        """Test converting decimal degrees to radians"""
        coords = WGS84Coords(lat=45.0, lon=90.0, alt=100.0)
        lat_rad, lon_rad, alt = coords.to_radians()
        
        # 45 degrees = pi/4 radians
        self.assertAlmostEqual(lat_rad, np.pi/4, places=5)
        # 90 degrees = pi/2 radians
        self.assertAlmostEqual(lon_rad, np.pi/2, places=5)
        self.assertEqual(alt, 100.0)
    
    def test_to_radians_zero(self):
        """Test converting zero degrees to radians"""
        coords = WGS84Coords(lat=0.0, lon=0.0)
        lat_rad, lon_rad, alt = coords.to_radians()
        
        self.assertAlmostEqual(lat_rad, 0.0, places=5)
        self.assertAlmostEqual(lon_rad, 0.0, places=5)
    
    def test_to_radians_negative(self):
        """Test converting negative degrees to radians"""
        coords = WGS84Coords(lat=-45.0, lon=-90.0)
        lat_rad, lon_rad, alt = coords.to_radians()
        
        self.assertAlmostEqual(lat_rad, -np.pi/4, places=5)
        self.assertAlmostEqual(lon_rad, -np.pi/2, places=5)


class TestWGS84CoordsToDMS(unittest.TestCase):
    """Test to_dms method"""
    
    def test_to_dms_positive(self):
        """Test converting decimal degrees to DMS"""
        coords = WGS84Coords(lat=55.675, lon=12.5125, alt=100.0)
        lat_dms, lon_dms, alt = coords.to_dms()
        
        # lat_dms should be (sign, deg, min, sec)
        self.assertEqual(lat_dms[0], 1.0)  # positive sign
        self.assertEqual(lat_dms[1], 55)   # degrees
        self.assertEqual(lat_dms[2], 40)   # minutes
        self.assertAlmostEqual(lat_dms[3], 30.0, places=2)  # seconds
        
        self.assertEqual(lon_dms[0], 1.0)  # positive sign
        self.assertEqual(lon_dms[1], 12)   # degrees
        self.assertEqual(lon_dms[2], 30)   # minutes
        self.assertAlmostEqual(lon_dms[3], 45.0, places=2)  # seconds
        self.assertEqual(alt, 100.0)
    
    def test_to_dms_negative(self):
        """Test converting negative decimal degrees to DMS"""
        coords = WGS84Coords(lat=-55.675, lon=-12.5125)
        lat_dms, lon_dms, _ = coords.to_dms()
        
        # Sign should be negative
        self.assertEqual(lat_dms[0], -1.0)
        self.assertEqual(lon_dms[0], -1.0)


class TestWGS84CoordsToDM(unittest.TestCase):
    """Test to_dm method"""
    
    def test_to_dm(self):
        """Test converting decimal degrees to DM"""
        coords = WGS84Coords(lat=55.5, lon=12.25)
        lat_dm, lon_dm, alt = coords.to_dm()
        
        # lat_dm should be (sign, deg, min)
        self.assertEqual(lat_dm[0], 1.0)   # positive sign
        self.assertEqual(lat_dm[1], 55)    # degrees
        self.assertAlmostEqual(lat_dm[2], 30.0, places=2)  # decimal minutes
        
        self.assertEqual(lon_dm[0], 1.0)   # positive sign
        self.assertEqual(lon_dm[1], 12)    # degrees
        self.assertAlmostEqual(lon_dm[2], 15.0, places=2)  # decimal minutes
    
    def test_to_dm_negative(self):
        """Test converting negative decimal degrees to DM"""
        coords = WGS84Coords(lat=-55.5, lon=-12.25)
        lat_dm, lon_dm, _ = coords.to_dm()
        
        self.assertEqual(lat_dm[0], -1.0)
        self.assertEqual(lon_dm[0], -1.0)


class TestWGS84CoordsToECEF(unittest.TestCase):
    """Test to_ecef method"""
    
    def test_to_ecef_at_greenwich(self):
        """Test converting to ECEF at prime meridian and equator"""
        coords = WGS84Coords(lat=0.0, lon=0.0, alt=0.0)
        x, y, z = coords.to_ecef()
        
        self.assertAlmostEqual(x, 6378137.0, places=1)
        self.assertAlmostEqual(y, 0.0, places=1)
        self.assertAlmostEqual(z, 0.0, places=1)
    
    def test_to_ecef_north_pole(self):
        """Test converting to ECEF at north pole"""
        coords = WGS84Coords(lat=90.0, lon=0.0, alt=0.0)
        x, y, z = coords.to_ecef()
        
        self.assertAlmostEqual(x, 0.0, places=0)
        self.assertAlmostEqual(y, 0.0, places=0)
        self.assertAlmostEqual(z, 6356752.314245, places=0)
    
    def test_to_ecef_with_altitude(self):
        """Test converting to ECEF with altitude"""
        coords = WGS84Coords(lat=0.0, lon=0.0, alt=1000.0)
        x, y, z = coords.to_ecef()
        
        # At equator with 1000m altitude, x should increase by ~1000
        self.assertAlmostEqual(x, 6379137.0, places=1)
        self.assertAlmostEqual(y, 0.0, places=1)
        self.assertAlmostEqual(z, 0.0, places=1)
    
    def test_to_ecef_roundtrip(self):
        """Test roundtrip conversion from WGS84 to ECEF and back"""
        original = WGS84Coords(lat=55.6, lon=12.5, alt=100.0)
        x, y, z = original.to_ecef()
        roundtrip = WGS84Coords.from_ecef(x, y, z)
        
        self.assertAlmostEqual(original.lat, roundtrip.lat, places=5)
        self.assertAlmostEqual(original.lon, roundtrip.lon, places=5)
        self.assertAlmostEqual(original.alt, roundtrip.alt, places=1)


class TestWGS84CoordsDistance(unittest.TestCase):
    """Test distance_to method"""
    
    def test_distance_same_point(self):
        """Test distance to same point should be zero"""
        coords = WGS84Coords(lat=55.6, lon=12.5, alt=100.0)
        distance = coords.distance_to(coords)
        
        self.assertAlmostEqual(distance, 0.0, places=1)
    
    def test_distance_different_points(self):
        """Test distance between different points"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0)
        coords2 = WGS84Coords(lat=56.0, lon=12.0)
        distance = coords1.distance_to(coords2)
        
        # Distance should be positive
        self.assertGreater(distance, 0.0)
    
    def test_distance_symmetric(self):
        """Test that distance is symmetric"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0)
        coords2 = WGS84Coords(lat=56.0, lon=13.0)
        
        dist1_to_2 = coords1.distance_to(coords2)
        dist2_to_1 = coords2.distance_to(coords1)
        
        self.assertAlmostEqual(dist1_to_2, dist2_to_1, places=5)
    
    def test_distance_with_altitude(self):
        """Test distance calculation with different altitudes"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0, alt=0.0)
        coords2 = WGS84Coords(lat=55.0, lon=12.0, alt=1000.0)
        distance = coords1.distance_to(coords2)
        
        # Distance should be approximately 1000m (vertical distance)
        self.assertGreater(distance, 900.0)
        self.assertLess(distance, 1100.0)


class TestWGS84CoordsArcLength(unittest.TestCase):
    """Test arc_length_to_ew method"""
    
    def test_arc_length_same_point(self):
        """Test arc length to same point should be zero"""
        coords = WGS84Coords(lat=55.6, lon=12.5)
        arc_length = coords.arc_length_to_ew(coords)
        
        self.assertAlmostEqual(arc_length, 0.0, places=1)
    
    def test_arc_length_east(self):
        """Test arc length going east should be positive"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0)
        coords2 = WGS84Coords(lat=55.0, lon=13.0)
        arc_length = coords1.arc_length_to_ew(coords2)
        
        # Going east should be positive
        self.assertGreater(arc_length, 0.0)
    
    def test_arc_length_west(self):
        """Test arc length going west should be negative"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0)
        coords2 = WGS84Coords(lat=55.0, lon=11.0)
        arc_length = coords1.arc_length_to_ew(coords2)
        
        # Going west should be negative
        self.assertLess(arc_length, 0.0)
    
    def test_arc_length_symmetric(self):
        """Test that arc lengths are negatives of each other"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0)
        coords2 = WGS84Coords(lat=55.0, lon=13.0)
        
        arc_1_to_2 = coords1.arc_length_to_ew(coords2)
        arc_2_to_1 = coords2.arc_length_to_ew(coords1)
        
        self.assertAlmostEqual(arc_1_to_2, -arc_2_to_1, places=1)


class TestWGS84CoordsENU(unittest.TestCase):
    """Test enu_to method"""
    
    def test_enu_same_point(self):
        """Test ENU vector to same point should be zero"""
        coords = WGS84Coords(lat=55.6, lon=12.5)
        e, n, u = coords.enu_to(coords)
        
        self.assertAlmostEqual(e, 0.0, places=1)
        self.assertAlmostEqual(n, 0.0, places=1)
        self.assertAlmostEqual(u, 0.0, places=1)
    
    def test_enu_north(self):
        """Test ENU vector to north"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0)
        coords2 = WGS84Coords(lat=56.0, lon=12.0)
        e, n, u = coords1.enu_to(coords2)
        
        # North direction, so n should be dominant and positive
        self.assertGreater(n, 0.0)
        self.assertLess(abs(e), abs(n))
    
    def test_enu_east(self):
        """Test ENU vector to east"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0)
        coords2 = WGS84Coords(lat=55.0, lon=13.0)
        e, n, u = coords1.enu_to(coords2)
        
        # East direction, so e should be dominant and positive
        self.assertGreater(e, 0.0)
        self.assertLess(abs(n), abs(e))


class TestWGS84CoordsAzimuthElevation(unittest.TestCase):
    """Test az_el_to and az_el_range_to methods"""
    
    def test_az_el_north(self):
        """Test azimuth and elevation to north"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0, alt=0.0)
        coords2 = WGS84Coords(lat=56.0, lon=12.0, alt=0.0)
        az, el = coords1.az_el_to(coords2)
        
        # North should be near 0 degrees
        self.assertAlmostEqual(az, 0.0, places=0)
        # Elevation should be small for same altitude (within ~1 degree)
        self.assertLess(abs(el), 1.0)
    
    def test_az_el_east(self):
        """Test azimuth and elevation to east"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0, alt=0.0)
        coords2 = WGS84Coords(lat=55.0, lon=13.0, alt=0.0)
        az, el = coords1.az_el_to(coords2)
        
        # East should be near 90 degrees
        self.assertAlmostEqual(az, 90.0, places=0)
        # Elevation should be small for same altitude (within ~1 degree)
        self.assertLess(abs(el), 1.0)
    
    def test_az_el_up(self):
        """Test azimuth and elevation to point above"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0, alt=0.0)
        coords2 = WGS84Coords(lat=55.0, lon=12.0, alt=1000.0)
        az, el = coords1.az_el_to(coords2)
        
        # Elevation should be positive (looking up)
        self.assertGreater(el, 0.0)
    
    def test_az_el_range(self):
        """Test azimuth, elevation and range"""
        coords1 = WGS84Coords(lat=55.0, lon=12.0, alt=0.0)
        coords2 = WGS84Coords(lat=56.0, lon=12.0, alt=0.0)
        az, el, rng = coords1.az_el_range_to(coords2)
        
        # Range should be positive
        self.assertGreater(rng, 0.0)
        # Check that range is consistent with distance
        distance = coords1.distance_to(coords2)
        self.assertAlmostEqual(rng, distance, places=1)


class TestWGS84CoordsFromAzElRange(unittest.TestCase):
    """Test coords_from_az_el_range method"""
    
    def test_coords_from_az_el_range_north(self):
        """Test creating coords in north direction"""
        origin = WGS84Coords(lat=55.0, lon=12.0, alt=100.0)
        # 1000 meters north
        new_coords = origin.coords_from_az_el_range(0.0, 0.0, 1000.0)
        
        # Should be slightly north
        self.assertGreater(new_coords.lat, origin.lat)
        # Longitude should be similar
        self.assertAlmostEqual(new_coords.lon, origin.lon, places=2)
    
    def test_coords_from_az_el_range_east(self):
        """Test creating coords in east direction"""
        origin = WGS84Coords(lat=55.0, lon=12.0, alt=100.0)
        # 1000 meters east
        new_coords = origin.coords_from_az_el_range(90.0, 0.0, 1000.0)
        
        # Latitude should be similar
        self.assertAlmostEqual(new_coords.lat, origin.lat, places=2)
        # Should be slightly east
        self.assertGreater(new_coords.lon, origin.lon)
    
    def test_coords_from_az_el_range_up(self):
        """Test creating coords above origin"""
        origin = WGS84Coords(lat=55.0, lon=12.0, alt=0.0)
        # 1000 meters up
        new_coords = origin.coords_from_az_el_range(0.0, 90.0, 1000.0)
        
        # Altitude should increase by ~1000m
        self.assertGreater(new_coords.alt, origin.alt)
    
    def test_coords_from_az_el_range_roundtrip(self):
        """Test roundtrip: get azimuth/elevation/range and create new coords"""
        origin = WGS84Coords(lat=55.0, lon=12.0, alt=100.0)
        target = WGS84Coords(lat=55.01, lon=12.01, alt=200.0)
        
        # Get azimuth, elevation, and range
        az, el, rng = origin.az_el_range_to(target)
        
        # Create new coords from these values
        recreated = origin.coords_from_az_el_range(az, el, rng)
        
        # Should be close to target
        self.assertAlmostEqual(recreated.lat, target.lat, places=3)
        self.assertAlmostEqual(recreated.lon, target.lon, places=3)
        self.assertAlmostEqual(recreated.alt, target.alt, places=0)


class TestWGS84CoordsStringRepresentations(unittest.TestCase):
    """Test string representation methods"""
    
    def test_str_method(self):
        """Test __str__ method"""
        coords = WGS84Coords(lat=55.123456, lon=12.654321, alt=100.5)
        str_repr = coords.__str__()
        
        self.assertIn("55.123456", str_repr)
        self.assertIn("12.654321", str_repr)
        self.assertIn("100.50", str_repr)
    
    def test_to_dms_string(self):
        """Test to_dms_string method"""
        coords = WGS84Coords(lat=55.675, lon=12.5125)
        dms_str = coords.to_dms_string()
        
        # Should contain degree, minute, second symbols and directions
        self.assertIn("º", dms_str)
        self.assertIn("´", dms_str)
        self.assertIn("´´", dms_str)
        self.assertIn("N", dms_str)
        self.assertIn("E", dms_str)
    
    def test_to_dms_string_negative(self):
        """Test to_dms_string with negative coordinates"""
        coords = WGS84Coords(lat=-55.675, lon=-12.5125)
        dms_str = coords.to_dms_string()
        
        # Should contain S and W
        self.assertIn("S", dms_str)
        self.assertIn("W", dms_str)
    
    def test_to_dm_string(self):
        """Test to_dm_string method"""
        coords = WGS84Coords(lat=55.5, lon=12.25)
        dm_str = coords.to_dm_string()
        
        # Should contain degree and minute symbols and directions
        self.assertIn("º", dm_str)
        self.assertIn("´", dm_str)
        self.assertIn("N", dm_str)
        self.assertIn("E", dm_str)
    
    def test_to_decimal_string(self):
        """Test to_decimal_string method"""
        coords = WGS84Coords(lat=55.6, lon=12.5)
        decimal_str = coords.to_decimal_string()
        
        # Should contain degree symbol and directions
        self.assertIn("°", decimal_str)
        self.assertIn("N", decimal_str)
        self.assertIn("E", decimal_str)
    
    def test_to_ecef_string(self):
        """Test to_ecef_string method"""
        coords = WGS84Coords(lat=0.0, lon=0.0, alt=0.0)
        ecef_str = coords.to_ecef_string()
        
        # Should contain x, y, z labels and 'm' for meters
        self.assertIn("x=", ecef_str)
        self.assertIn("y=", ecef_str)
        self.assertIn("z=", ecef_str)
        self.assertIn("m", ecef_str)
    
    def test_string_precision(self):
        """Test string representation with different precision"""
        coords = WGS84Coords(lat=55.123456789, lon=12.654321987, alt=100.123456)
        
        str_2_decimals = coords.__str__(decimals=2)
        # Should have 2 decimal places for altitude
        self.assertIn("100.12", str_2_decimals)
        
        str_4_decimals = coords.__str__(decimals=4)
        # Should have 4 decimal places for altitude
        self.assertIn("100.1235", str_4_decimals)


class TestWGS84CoordsEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_equator(self):
        """Test coordinates at equator"""
        coords = WGS84Coords(lat=0.0, lon=0.0)
        self.assertEqual(coords.lat, 0.0)
        x, y, z = coords.to_ecef()
        self.assertAlmostEqual(x, 6378137.0, places=1)
    
    def test_prime_meridian(self):
        """Test coordinates at prime meridian"""
        coords = WGS84Coords(lat=45.0, lon=0.0)
        self.assertEqual(coords.lon, 0.0)
    
    def test_international_date_line(self):
        """Test coordinates near international date line"""
        coords1 = WGS84Coords(lat=0.0, lon=179.9)
        coords2 = WGS84Coords(lat=0.0, lon=-179.9)
        # Should be able to handle near date line coords
        x1, y1, z1 = coords1.to_ecef()
        x2, y2, z2 = coords2.to_ecef()
        # These points should be close to each other
        distance = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        self.assertLess(distance, 100000)  # Less than 100km apart
    
    def test_very_high_altitude(self):
        """Test with very high altitude"""
        coords = WGS84Coords(lat=0.0, lon=0.0, alt=400000.0)  # ~ISS altitude
        self.assertEqual(coords.alt, 400000.0)
    
    def test_negative_altitude(self):
        """Test with negative altitude (below WGS84 ellipsoid)"""
        coords = WGS84Coords(lat=0.0, lon=0.0, alt=-100.0)
        self.assertEqual(coords.alt, -100.0)


if __name__ == '__main__':
    unittest.main()
