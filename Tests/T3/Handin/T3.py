import os
import numpy as np
import itertools
from NavSysLib.Coords import *
from NavSysLib.utilities import *
from NavSysLib.Orbit import Orbit

# Load ephemerides
eph_file = os.path.join(os.path.dirname(__file__), "ns2025-2026_WA3.eph")
orbits = get_orbits_from_eph_file(eph_file, reference_wn=2056)
print(f"Loaded {len(orbits)} orbits")

# Load pseudo-ranges
pr_file = os.path.join(os.path.dirname(__file__), "ns2025-2026_WA3.pr")
pseudoranges = []
with open(pr_file, 'r') as f:
    for line in f:
        if line.strip():
            pseudoranges.append(float(line.strip()))
            
print(f"Loaded {len(pseudoranges)} pseudoranges.")


# E1
print("\n----- Exercise 1 -----")

r = WGS84Coords.from_ecef(4918532, -791213, 3969755)
wn = 2057
tow = 24

visible_sats = r.get_orbits_from_elevation_mask(orbits, tow=tow, wn=wn, elevation_mask=0)
print(f"Visible satellites at TOW {tow} s:")
for sat in visible_sats:
    sat_pos = sat.wgs84_ecef_position(tow, wn, return_coords=True)
    print(f"  - SVN {sat.ephemeris.sv_num}")
    print(f"    Position (ECEF): {sat_pos.to_ecef_string()}")
    print(f"    Direction cosines: {r.direction_cosines_to(sat_pos)}")

gdop = r.get_gdop_from_orbits(visible_sats, tow=tow, wn=wn, elevation_mask=0)
hdop = r.get_hdop_from_orbits(visible_sats, tow=tow, wn=wn, elevation_mask=0)

print(f"GDOP: {gdop:.2f}")
print(f"HDOP: {hdop:.2f}")


# E2
print("\n----- Exercise 2 -----")

# a)
estimated_pos = r.get_position_from_orbits_and_pseudoranges(orbits, pseudoranges, tow=tow, wn=wn, elevation_mask=0, num_iter=1)
print(f"Estimated position (ECEF): {estimated_pos}")

# b)
timestamp = 2057*604800 + 24 - 0.000200
print(f"Timestamp: {timestamp}")


# E3
print("\n----- Exercise 3 -----")

estimated_pos_non_iter = r.get_position_from_orbits_and_pseudoranges_non_iterative(orbits, pseudoranges, tow=tow, wn=wn, elevation_mask=0, num_iter=1)
print(f"Estimated position (ECEF, non-iterative): {estimated_pos_non_iter}")

