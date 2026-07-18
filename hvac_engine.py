# hvac_engine.py

class HVACValidatorEngine:
    def __init__(self, location, space_type, area_sqmt, design_tr=0.0):
        self.location = location
        self.space_type = space_type
        self.area_sqmt = area_sqmt
        self.design_tr = design_tr

    def calculate_from_scratch(self, building_type, occupancy=10):
        """
        Calculates cooling load based on building type rules-of-thumb
        Commercial: ~150 sqmt/TR or ~40 Watts/sqmt
        Residential Bungalow: ~200 sqmt/TR or ~30 Watts/sqmt
        """
        if "commercial" in building_type.lower():
            calculated_tr = max(2.0, round((self.area_sqmt / 12.0), 2)) # Approx 12 sqmt per TR baseline
        else: # Residential/Bungalow
            calculated_tr = max(1.5, round((self.area_sqmt / 16.0), 2)) # Approx 16 sqmt per TR baseline
        
        return calculated_tr

    def generate_full_boq(self, target_tr, building_type):
        # Select Chiller Type based on sizing scale
        if target_tr > 100:
            chiller_type = "Water-Cooled Centrifugal Chiller (AHRI 550/590 Certified)"
            cooling_tower = f"Induced Draft Cooling Tower: {round(target_tr * 1.2, 1)} TR"
        elif target_tr > 30:
            chiller_type = "Air-Cooled Screw Chiller (AHRI 550/590 Certified)"
            cooling_tower = "N/A (Air-Cooled)"
        else:
            chiller_type = "Variable Refrigerant Flow (VRF) Inverter System (AHRI 1230 Certified)"
            cooling_tower = "N/A (DX System)"

        # Pump Sizing Math (Primary/Secondary chilled water flows)
        chilled_water_flow_gpm = round(target_tr * 2.4, 1) # Rule: 2.4 GPM per TR
        pump_head_m = 25 # Standard structural head estimate
        pump_kw = round((chilled_water_flow_gpm * pump_head_m) / 1000, 2)

        # Air Handling Units (AHU) and Air Flow Math
        total_cfm = round(target_tr * 400, 0) # Rule: 400 CFM per TR
        ahu_count = max(1, int(total_cfm // 3000))
        cfm_per_ahu = round(total_cfm / ahu_count, 0)

        # Main Duct Sizing (based on equal friction at 0.1 inch wg/100ft)
        main_duct_area_sqin = (total_cfm / 1200) * 144 # 1200 FPM velocity baseline
        duct_width = round((main_duct_area_sqin) ** 0.5, 0)
        duct_size_str = f"{int(duct_width * 1.2)}mm x {int(duct_width * 0.8)}mm"

        # Piping sizes (based on water velocity limits)
        if chilled_water_flow_gpm > 200:
            pipe_size = "150 mm Dia MS Heavy Class"
        elif chilled_water_flow_gpm > 80:
            pipe_size = "100 mm Dia MS Heavy Class"
        else:
            pipe_size = "50 mm Dia GI/MS Class"

        # Compile the comprehensive structural list
        boq = [
            {"Item": "Primary Cooling Source", "Specification": chiller_type, "Qty": "1 Lot"},
            {"Item": "Heat Rejection System", "Specification": cooling_tower, "Qty": "1 Unit" if "Water" in chiller_type else "0"},
            {"Item": "Chilled Water Pumps", "Specification": f"End Suction Pumps, Flow: {chilled_water_flow_gpm} GPM @ {pump_head_m}m Head (~{pump_kw} kW)", "Qty": "2 Nos (1W + 1SB)"},
            {"Item": "Air Handling Units (AHUs)", "Specification": f"Double Skin AHU, Capacity: {cfm_per_ahu} CFM with Pre-filters", "Qty": f"{ahu_count} Nos"},
            {"Item": "Ventilation Fan Units", "Specification": "Axial Flow Inline Fans for Fresh Air Injection (ASHRAE 62.1 compliant)", "Qty": "2 Nos"},
            {"Item": "Main Header Ductwork", "Specification": f"G.I. Ducting Sheet (0.8mm/22G) sized at approx {duct_size_str}", "Qty": f"{round(self.area_sqmt * 1.2, 0)} Sqm"},
            {"Item": "Chilled Water Piping", "Specification": f"{pipe_size} with anti-corrosive primer coating", "Qty": "Rmt As per Layout"},
            {"Item": "Motorized Valves & Balancing", "Specification": "Pressure Independent Balancing Valves (PIBV) & 2-Way Modulating Valves", "Qty": "1 Set per AHU"},
            {"Item": "Gauges & Sensors", "Specification": "Industrial Pressure Gauges (0-10 bar), Dial Thermometers & Wet-bulb Sensors", "Qty": "1 Lot"},
            {"Item": "Thermal Insulation", "Specification": "Class 'O' Nitrile Rubber Insulation (19mm thickness) with Aluminum cladding", "Qty": "1 Lot"},
            {"Item": "Automation / BMS Sensors", "Specification": "Digital Temp/RH Transmitters, Flow Meters, Carbon Dioxide (CO2) Sensors", "Qty": "1 Lot"}
        ]
        return boq, chiller_type