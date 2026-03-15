from NavSysLib.utilities import *
from NavSysLib.NMEASentence import *
from NavSysLib.NMEALog import *


nmea_log = NMEALog.from_file("Exercises/E1/ISTShuttle.nmea")

# E1
print("\nExercise 1")
nmea_count = nmea_log.get_sentence_count()
gga_count = nmea_log.get_sentence_count("GGA")
gll_count = nmea_log.get_sentence_count("GLL")
print(f"Total sentences: {nmea_count}")
print(f"GGA sentences: {gga_count}")
print(f"GLL sentences: {gll_count}")

# E2
print("\nExercise 2")
for format in nmea_formats:
    if nmea_log.get_sentence_count(format) > 0:
        print(f"{format} sentences were logged.")

# E3
print("\nExercise 3")
for format in nmea_formats:
    count = nmea_log.get_sentence_count(format)
    print(f"Message rate for {format}: {count/nmea_count*100:.2f}%")
        

# E4
print("\nExercise 4")
# Find first sentence with date and time
start_time = nmea_log.get_start_datetime()
end_time = nmea_log.get_end_datetime()
print(f"Start time: {start_time}")
print(f"End time: {end_time}")
time_val = time(11, 2, 59, 600000)
gga_sent = nmea_log.get_sentence_by_attr_value("time", time_val, format="GGA")
print(f"GGA sentence at 110259.600: {gga_sent.string if gga_sent else 'Not found'}")


# E5
print("\nExercise 5")
# Get corners of bounding box
min_lat = nmea_log.get_min_latitude()
min_lon = nmea_log.get_min_longitude()
max_lat = nmea_log.get_max_latitude()
max_lon = nmea_log.get_max_longitude()

print(f"Bounding box corners:")
print(f"({min_lat}, {min_lon})")
print(f"({max_lat}, {min_lon})")
print(f"({min_lat}, {max_lon})")
print(f"({max_lat}, {max_lon})")

# E6
print("\nExercise 6")
# Get min and max altitude, with timestamps
min_sentence = nmea_log.get_sentence_by_attr_min("altitude", format="GGA")
max_sentence = nmea_log.get_sentence_by_attr_max("altitude", format="GGA")
if min_sentence and max_sentence:
    print(f"Minimum altitude: {min_sentence.altitude} m at {min_sentence.time}")
    print(f"Maximum altitude: {max_sentence.altitude} m at {max_sentence.time}")

# E7
print("\nExercise 7")
alt_gain = nmea_log.get_cumulative_altitude_gain()
alt_loss = nmea_log.get_cumulative_altitude_loss()
print(f"Cumulative altitude gain: {alt_gain:.2f} m")
print(f"Cumulative altitude loss: {alt_loss:.2f} m")

# E8
print("\nExercise 8")
max_velocity = nmea_log.get_sentence_by_attr_max("speed_kmh", format="VTG")
if max_velocity:
    print(f"Maximum velocity: {max_velocity.speed_kmh} km/h")
else:
    print("No VTG sentences found or no valid velocity data available.")

# E9
# Get max number of satellites in view 
print("\nExercise 9")
max_sat_sentence = nmea_log.get_sentence_by_attr_max("num_satellites", format="GSV")
if max_sat_sentence:
    print(f"Maximum satellites in view: {max_sat_sentence.num_satellites}")
else:   
    print("No GSV sentences found or no valid satellite data available.")

# E10
# Get max elevation angle of satellites in view
print("\nExercise 10")
max_elev = nmea_log.get_max_sat_elevation()
if max_elev is not None:
    print(f"Maximum satellite elevation angle: {max_elev} degrees")
else:
    print("No GSV sentences found or no valid elevation data available.")

# E11
print("\nExercise 11")
# Check checksum of all sentences
valid_count = 0
invalid_count = 0
for sentence in nmea_log.sentences:
    if not sentence.validate_checksum():
        print(f"Invalid checksum: {sentence.string}")
        invalid_count += 1
    else:
        valid_count += 1
print(f"Valid sentences: {valid_count}")
print(f"Invalid sentences: {invalid_count}")
