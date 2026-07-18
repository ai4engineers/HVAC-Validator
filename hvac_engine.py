# hvac_engine.py

class HVACValidatorEngine:
    def __init__(self, location="Default Zone", space_type="Comfort", area_sqmt=0.0, design_tr=0.0):
        self.location = location
        self.space_type = space_type
        self.area_sqmt = area_sqmt
        self.design_tr = design_tr

    def calculate_manual_scenario(self, scenario_type, params):
        """
        Calculates explicit sizing and ambient deration physics for 3 specialized scenarios.
        """
        # Ambient Ambient Deration Factor determination based on Region
        # Severe dry heat (e.g., Delhi, Indore) or coastal humidity scales ambient derating
        loc = self.location.lower()
        if any(x in loc for x in ["delhi", "indore", "rajasthan", "north"]):
            deration_factor = 0.88  # 12% capacity loss due to extreme peak ambient dry-bulb temps
        elif any(x in loc for x in ["mumbai", "chennai", "kolkata", "coastal"]):
            deration_factor = 0.92  # 8% capacity loss due to high latent heat load / condensation
        else:
            deration_factor = 0.95  # Standard rating baseline

        if scenario_type == "Scenario 1: Residential Bungalow":
            glass_area = params.get("glass_area_sqmt", 0)
            appliances_kw = params.get("appliances_kw", 0)
            
            # Physics: Base envelope load + solar radiation gain through glass + internal load
            base_load_tr = self.area_sqmt / 16.0 
            solar_gain_tr = glass_area * 0.08
            internal_gain_tr = appliances_kw * 0.284  # 1 kW = 0.284 TR
            
            gross_tr = base_load_tr + solar_gain_tr + internal_gain_tr
            net_required_tr = round(gross_tr / deration_factor, 1)
            tech_recommended = "High-Efficiency Inverter VRF System (AHRI 1230 Certified)"
            
        elif scenario_type == "Scenario 2: Commercial Building":
            occupancy = params.get("occupancy", 10)
            equipment_kw = params.get("equipment_kw", 0)
            floors = params.get("floors", 1)
            
            # Physics: People metabolic load + lighting/IT hardware load + structural building height scale
            base_load_tr = (self.area_sqmt * floors) / 12.0
            people_load_tr = (occupancy * 500) / 12000  # 500 BTU/hr per person baseline
            it_load_tr = equipment_kw * 0.284
            
            gross_tr = base_load_tr + people_load_tr + it_load_tr
            net_required_tr = round(gross_tr / deration_factor, 1)
            
            if net_required_tr > 120:
                tech_recommended = "Central Water-Cooled Screw/Centrifugal Chiller Plant (AHRI 550/590)"
            else:
                tech_recommended = "Modular Air-Cooled Scroll Chiller Array"
                
        else:  # Scenario 3: Process Cooling Industrial
            water_flow_lpm = params.get("water_flow_lpm", 100)
            temp_in = params.get("temp_in", 30)
            temp_out = params.get("temp_out", 15)
            
            # Core Thermodynamic Formula: Q = m * C * deltaT
            # Flow in LPM converted to kg/s, specific heat of water = 4.186 kJ/kg°C
            mass_flow = water_flow_lpm / 60.0  # kg/sec
            delta_t = temp_in - temp_out
            kw_load = mass_flow * 4.186 * delta_t
            process_tr = kw_load / 3.517  # 1 TR = 3.517 kW
            
            # Heavy safety factor for industrial process fluctuations
            net_required_tr = round((process_tr * 1.25) / deration_factor, 1)
            tech_recommended = "Heavy-Duty Industrial Process Water Chiller (Shell & Tube Evaporator)"

        return net_required_tr, deration_factor, tech_recommended

    def generate_wizard_boq(self, target_tr, scenario_type):
        # Pump and Airflow calculations adjusted by target scale
        total_cfm = round(target_tr * 400, 0)
        chilled_water_flow_gpm = round(target_tr * 2.4, 1)
        
        if "Industrial" in scenario_type:
            boq = [
                {"Item": "Industrial Process Chiller", "Specification": f"Heavy duty skid-mounted unit, Cap: {target_tr} TR", "Qty": "1 Unit"},
                {"Item": "Primary Circulation Pump", "Specification": f"SS316 Impeller Pump, Flow: {chilled_water_flow_gpm} GPM @ 35m head", "Qty": "2 Nos (1W+1SB)"},
                {"Item": "Insulated Process Piping", "Specification": "MS Heavy Class Pipe with PUF insulation & GI cladding", "Qty": "1 Lot"},
                {"Item": "Shell & Tube Heat Exchanger", "Specification": "Highly cleanable marine grade copper-tubed HX unit", "Qty": "1 No"},
                {"Item": "Industrial Gauge Panel", "Specification": "PT100 Temp transmitters, electromagnetic flowmeter, dual bar gauges", "Qty": "1 Set"}
            ]
        elif "Commercial" in scenario_type:
            boq = [
                {"Item": "Central Air-Conditioning Plant", "Specification": f"High COP Chiller Assembly, Cap: {target_tr} TR", "Qty": "1 Lot"},
                {"Item": "Chilled Water Pump Sets", "Specification": f"End Suction Monoblock Pumps (~{chilled_water_flow_gpm} GPM)", "Qty": "2 Nos"},
                {"Item": "Air Handling Units (AHUs)", "Specification": f"Double skin layout running at {total_cfm} Total CFM", "Qty": f"{max(1, int(total_cfm//3500))} Units"},
                {"Item": "Galvanized Iron (GI) Ducts", "Specification": "Pre-fabricated rectangular ducts matching SMACNA class", "Qty": f"{int(target_tr * 12)} Sqm"},
                {"Item": "BMS Sensor Suite", "Specification": "DDC controller loops, motorized dampers, digital thermostats", "Qty": "1 Lot"}
            ]
        else: # Residential
            boq = [
                {"Item": "VRF Outdoor Heat Pump Module", "Specification": f"Top-Discharge Inverter unit, Cap: {target_tr} TR", "Qty": "1 Unit"},
                {"Item": "Indoor Terminal Units", "Specification": "Mix of Hi-Wall Slim profiles and 4-Way Compact Cassettes", "Qty": f"{max(2, int(target_tr//1.5))} Units"},
                {"Item": "Refrigerant Copper Piping", "Specification": "Deoxidized seamless copper tubing with elastomeric sleeves", "Qty": "Running Meters"},
                {"Item": "Central Touch Controller", "Specification": "7-inch centralized zone monitor display pane", "Qty": "1 Unit"}
            ]
            
        return boq