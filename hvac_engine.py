# hvac_engine.py

class HVACValidatorEngine:
    def __init__(self, location="Default Zone", area_sqmt=0.0):
        self.location = location
        self.area_sqmt = area_sqmt

    def calculate_manual_scenario(self, scenario_type, params, amb_temp=None, amb_rh=None):
        """
        Calculates explicit sizing and ambient deration physics, incorporating 
        specific ambient Dry-Bulb Temperature and Relative Humidity parameters.
        """
        deration_factor = 0.95
        latent_multiplier = 1.0

        # Advanced Psychrometric Scaling Matrix
        if amb_temp is not None and amb_rh is not None:
            if amb_temp >= 45:
                deration_factor = 0.82
            elif amb_temp >= 40:
                deration_factor = 0.88
            elif amb_temp >= 35:
                deration_factor = 0.92
                
            if amb_rh >= 75:
                latent_multiplier = 1.18
            elif amb_rh >= 60:
                latent_multiplier = 1.10
        else:
            loc = self.location.lower()
            if any(x in loc for x in ["delhi", "indore", "rajasthan", "north"]):
                deration_factor = 0.88
                latent_multiplier = 1.0
            elif any(x in loc for x in ["mumbai", "chennai", "kolkata", "coastal"]):
                deration_factor = 0.92
                latent_multiplier = 1.15

        # Base Load Scenario Router
        if "Scenario 1" in scenario_type:
            glass_area = params.get("glass_area_sqmt", 0)
            appliances_kw = params.get("appliances_kw", 0)
            
            base_load_tr = (self.area_sqmt / 16.0) * latent_multiplier
            solar_gain_tr = glass_area * 0.08
            internal_gain_tr = appliances_kw * 0.284
            
            gross_tr = base_load_tr + solar_gain_tr + internal_gain_tr
            net_required_tr = round(gross_tr / deration_factor, 1)
            tech_recommended = "High-Efficiency Inverter VRF System (AHRI 1230 Certified)"
            
        elif "Scenario 2" in scenario_type:
            occupancy = params.get("occupancy", 10)
            equipment_kw = params.get("equipment_kw", 0)
            floors = params.get("floors", 1)
            
            base_load_tr = ((self.area_sqmt * floors) / 12.0) * latent_multiplier
            people_load_tr = (occupancy * 500) / 12000  
            it_load_tr = equipment_kw * 0.284
            
            gross_tr = base_load_tr + people_load_tr + it_load_tr
            net_required_tr = round(gross_tr / deration_factor, 1)
            
            if net_required_tr > 120:
                tech_recommended = "Central Water-Cooled Screw Chiller Plant"
            else:
                tech_recommended = "Modular Air-Cooled Scroll Chiller Array"
                
        else:  # Scenario 3: Process Cooling Industrial
            water_flow_lpm = params.get("water_flow_lpm", 100)
            temp_in = params.get("temp_in", 30)
            temp_out = params.get("temp_out", 15)
            
            mass_flow = water_flow_lpm / 60.0
            delta_t = temp_in - temp_out
            kw_load = mass_flow * 4.186 * delta_t
            process_tr = kw_load / 3.517  
            
            net_required_tr = round((process_tr * 1.25) / deration_factor, 1)
            tech_recommended = "Heavy-Duty Process Water Chiller (Shell & Tube Framework)"

        return net_required_tr, deration_factor, latent_multiplier, tech_recommended

    def generate_wizard_boq(self, target_tr, scenario_type):
        total_cfm = round(target_tr * 400, 0)
        chilled_water_flow_gpm = round(target_tr * 2.4, 1)
        
        if "Industrial" in scenario_type:
            boq = [
                {"Item": "Industrial Process Chiller", "Specification": f"Heavy duty skid unit Cap {target_tr} TR", "Qty": "1 Unit"},
                {"Item": "Primary Circulation Pump", "Specification": f"SS316 Pump Flow {chilled_water_flow_gpm} GPM at 35m head", "Qty": "2 Nos (1W+1SB)"},
                {"Item": "Insulated Process Piping", "Specification": "MS Heavy Class Pipe with PUF insulation", "Qty": "1 Lot"},
                {"Item": "Shell and Tube Heat Exchanger", "Specification": "Cleanable marine grade copper tubed HX unit", "Qty": "1 No"},
                {"Item": "Industrial Gauge Panel", "Specification": "PT100 Temp transmitters and digital flowmeters", "Qty": "1 Set"}
            ]
        elif "Commercial" in scenario_type:
            boq = [
                {"Item": "Central Air-Conditioning Plant", "Specification": f"High COP Chiller Assembly Cap {target_tr} TR", "Qty": "1 Lot"},
                {"Item": "Chilled Water Pump Sets", "Specification": f"End Suction Monoblock Pumps approx {chilled_water_flow_gpm} GPM", "Qty": "2 Nos"},
                {"Item": "Air Handling Units (AHUs)", "Specification": f"Double skin layout running at {total_cfm} Total CFM", "Qty": f"{max(1, int(total_cfm//3500))} Units"},
                {"Item": "Galvanized Iron Ducts", "Specification": "Pre fabricated rectangular ducts matching SMACNA class", "Qty": f"{int(target_tr * 12)} Sqm"},
                {"Item": "BMS Sensor Suite", "Specification": "DDC controller loops with motorized dampers", "Qty": "1 Lot"}
            ]
        else: # Residential
            boq = [
                {"Item": "VRF Outdoor Heat Pump Module", "Specification": f"Top Discharge Inverter unit Cap {target_tr} TR", "Qty": "1 Unit"},
                {"Item": "Indoor Terminal Units", "Specification": "Mix of Hi Wall Slim profiles and Cassettes", "Qty": f"{max(2, int(target_tr//1.5))} Units"},
                {"Item": "Refrigerant Copper Piping", "Specification": "Deoxidized seamless copper tubing with sleeves", "Qty": "Running Meters"},
                {"Item": "Central Touch Controller", "Specification": "7 inch centralized zone monitor display pane", "Qty": "1 Unit"}
            ]
            
        return boq