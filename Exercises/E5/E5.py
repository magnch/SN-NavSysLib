import os
import numpy as np
import itertools
from NavSysLib.Coords import *
from NavSysLib.utilities import *
from NavSysLib.Orbit import Orbit


# E1
r1 = WGS84Coords.from_ecef(4918525, -791212, 3969762)
s10 = WGS84Coords.from_ecef(-5845119, -14047494, 21837689)
# a)
true_range = r1.distance_to(s10)
print(f"True range: {true_range:.2f} m")
# b)
pseudo_range = r1.pseudo_range_to(s10, receiver_delta_t=5e-4)
print(f"Pseudo range: {pseudo_range:.2f} m")


# E2
# a) z: 8
# b) H: 4x8
# c) x: 4
# d) H^T: 8x4
# e) (H^T)H: 8x8
# f) ((H^T)H)^-1: 8x8
# g) (H^T)H)^-1(H^T)z: 8


# E3
M = np.array([
    [1.108, -0.148, 0.491, 0.608],
    [-0.148, 0.386, 0.165, -0.011],
    [0.491, 0.165, 1.152, 0.590],
    [0.608, -0.011, 0.590, 0.570]
])

pdop_val = pdop(M=M)
print(f"PDOP: {pdop_val:.2f}")


wn = 2056
tow = 536400

r1_ecef = (4918525.18, -791212.21, 3969762.19)
r1_coords = WGS84Coords.from_ecef(*r1_ecef)

# Load Ephemerides
eph_file = os.path.join(os.path.dirname(__file__), "ub1.ubx.2056.540000b.eph")
orbits = get_orbits_from_eph_file(eph_file, reference_wn=wn)

# E6
# r3
r3_ecef = np.array([4918510.02634744, -791215.407423002, 3969631.08558596])

visible_orbits = r1_coords.get_orbits_from_elevation_mask(orbits, tow=tow, wn=wn, elevation_mask=10)
# Load pseudoranges from file
pr_file = os.path.join(os.path.dirname(__file__), "npr.txt")
pseudoranges = []
with open(pr_file, 'r') as f:
    for line in f:
        if line.strip():
            pseudoranges.append(float(line.split()[0]))

estimated_pos = r1_coords.get_position_from_orbits_and_pseudoranges(orbits, pseudoranges, tow=tow, wn=wn, elevation_mask=10, num_iter=100, tol=1e-3, initial_guess=r3_ecef)
print(f"Estimated position (ECEF): {estimated_pos}")

# E7
print("\n--- E7 ---")
min_pdop = float('inf')
max_pdop = -float('inf')
min_hdop = float('inf')
max_hdop = -float('inf')

import contextlib
import sys
import io

print(f"Ephemerides loaded #sat= {len(visible_orbits)}")
for i, ob in enumerate(visible_orbits):
    sv = ob.ephemeris.sv_num
    t_tx = ob.get_tx_time_from_ref_point(wn, tow, r1_ecef, 1e-4)
    sat_coords = ob.get_pos_at_tx_time(t_tx, wn, tow, True)
    xyz = sat_coords.to_ecef()
    print(f"sat{i+1:02d}(SVN{sv}) = ( {xyz[0]:.3f} m, {xyz[1]:.3f} m, {xyz[2]:.3f} m)")

for r in range(4, len(visible_orbits) + 1):
    min_pdop = float('inf')
    max_pdop = -float('inf')
    min_hdop = float('inf')
    max_hdop = -float('inf')
    
    min_pdop_svs = None
    max_pdop_svs = None
    min_hdop_svs = None
    max_hdop_svs = None

    for subset in itertools.combinations(visible_orbits, r):
        with contextlib.redirect_stdout(io.StringIO()): # suppress print spam
            pdop = r1_coords.get_pdop_from_orbits(subset, wn=wn, tow=tow, elevation_mask=10)
            hdop = r1_coords.get_hdop_from_orbits(subset, wn=wn, tow=tow, elevation_mask=10)
        
        subset_svs = tuple(ob.ephemeris.sv_num for ob in subset)

        if pdop is not None:
            if pdop < min_pdop:
                min_pdop = pdop
                min_pdop_svs = subset_svs
            if pdop > max_pdop:
                max_pdop = pdop
                max_pdop_svs = subset_svs
                
        if hdop is not None:
            if hdop < min_hdop:
                min_hdop = hdop
                min_hdop_svs = subset_svs
            if hdop > max_hdop:
                max_hdop = hdop
                max_hdop_svs = subset_svs
                
    visible_svs = [ob.ephemeris.sv_num for ob in visible_orbits]
    
    def get_binary_str(subset):
        return "".join(['1' if sv in subset else '0' for sv in visible_svs])
    
    def get_sv_str(subset):
        return "[" + " ".join([str(sv) for sv in subset]) + " ]"
        
    print(f"{r} satellites min(PDOP) = {min_pdop:.2f} {get_binary_str(min_pdop_svs)} SVN = {get_sv_str(min_pdop_svs)}")
    print(f"max(PDOP) = {max_pdop:.2f} {get_binary_str(max_pdop_svs)} SVN = {get_sv_str(max_pdop_svs)}")
    print(f"{r} satellites min(HDOP) = {min_hdop:.2f} {get_binary_str(min_hdop_svs)} SVN = {get_sv_str(min_hdop_svs)}")
    print(f"max(HDOP) = {max_hdop:.2f} {get_binary_str(max_hdop_svs)} SVN = {get_sv_str(max_hdop_svs)}")

# E8
print("\n--- E8 ---")
pr_matrix = np.loadtxt(pr_file)
num_epochs = pr_matrix.shape[1]
errors = []

for i in range(num_epochs):
    epoch_tow = 536400 + i
    prs = pr_matrix[:, i]
    with contextlib.redirect_stdout(io.StringIO()):
        est_pos = r1_coords.get_position_from_orbits_and_pseudoranges(
            orbits, prs, tow=epoch_tow, wn=wn, elevation_mask=10, 
            num_iter=10, tol=1e-3, initial_guess=r3_ecef)
    if est_pos is not None:
        err = np.linalg.norm(np.array(est_pos[:3]) - np.array(r1_ecef))
        errors.append(err)

mean_err = np.mean(errors)
print(f"Mean error = {mean_err:.3f} m (r0 = r3, {len(errors)} measurements)")


