from NavSysLib.utilities import *
from NavSysLib.Coords import WGS84Coords

# E1
print("\nExercise 1")

# Create p1 from DMS format
# p1 = (38º 46´ 49.61´´ N, 9º 29´ 56.19´´ W, 103 m)
p1 = WGS84Coords.from_dms(
    (38, 46, 49.61, 'N'),
    (9, 29, 56.19, 'W'),
    103
)

print(f"Original (DDº MM´ SS.ss´´): {p1.to_dms_string()}")
print(f"a) DDº MM.mmm´: {p1.to_dm_string()}")
print(f"b) DD.dddº: {p1.to_decimal_string()}")


# E2
# Convert p1 to x, y, z
print("\nExercise 2")
print(p1.to_ecef_string())


# E3
print("\nExercise 3")
p2 = WGS84Coords.from_ecef(4910384.3, -821478.6, 3973549.6)
print(f"a) {p2.to_decimal_string()}")
print(f"b) {p2.to_dm_string()}")
print(f"c) {p2.to_dms_string()}")


# E4
# Compute distance between p1 and p2
print("\nExercise 4")
distance = p1.distance_to(p2)
print(f"Distance between p1 and p2: {distance:.2f} m")

# E5
# Compute azimuth and elevation from p1 to p2
print("\nExercise 5")
az, el = p1.az_el_to(p2)
print(f"Azimuth from p1 to p2: {az:.2f}°")
print(f"Elevation from p1 to p2: {el:.2f}°")