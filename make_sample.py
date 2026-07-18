# ==========================================
# TEST AUTOMATION PIPELINE - GENERATE HVAC PROJECT REPORT
# This script builds a text-based layout for validation testing.
# ==========================================

import os

report_content = """
===========================================================
      AGNI ENGINEERING ASSOCIATES - MECHANICAL DRAWING SPEC
===========================================================
PROJECT PROFILE: Commercial Office Complex Expansion
LOCATION DETAILS: New Delhi, India (Composite Hot Climate Zone)
CLIENT ASSIGNMENT ID: AEA-2026-HVAC-09

1. SPACE ARCHITECTURE PROFILE
-----------------------------------------
Floor Designation: Level 3 Corporate Wing
Space Profile Typology: Office Space Layout
Total Floor Area Footprint: 500 sqmt
Ceiling Clearance Elevation: 3.0 meters
Assigned Personnel Density Target: 50 Occupants

2. BUILDING ENVELOPE METRICS
-----------------------------------------
External Wall Assemblies: 230mm brick masonry structure with external cement plaster.
Calculated Thermal Transmittance: actual_wall_u = 0.65 W/m2K
Glazing Window System Profile: Single glass pane clear assemblies.

3. AIR CONDITIONING INFRASTRUCTURE DESIGN SPECIFICATIONS
-----------------------------------------
Selected Centralized Configuration: Air-Cooled VRF Multi-Split System Array
Total Specified Design Capacity: design_tr = 45.0 TR
System Part Load Optimization: Fixed speed operational profile.
Manufacturer Efficiency Validation Check: equipment_cop = 3.0
Air Distribution Duct Plan: Galvanized Iron (GI) framework with fiberglass thermal wraps.
Fresh Air System Component Array: Dedicated fresh air intake fans operating without VFD sensors.

===========================================================
                    END OF SPECIFICATION FILE
===========================================================
"""

# Write the text structure into a simulated design doc profile
file_path = "sample_hvac_spec.txt"
with open(file_path, "w", encoding="utf-8") as file:
    file.write(report_content.strip())

print(f"\n[SUCCESS] Sample engineering file successfully generated inside project directory: '{file_path}'")