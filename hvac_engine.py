# hvac_engine.py
import re

class HVACValidatorEngine:
    def __init__(self, location="Default Zone", area_sqmt=0.0):
        self.location = location
        self.area_sqmt = area_sqmt

    def process_uploaded_document_text(self, text_content):
        """
        Parses raw text extracted from uploaded engineering drawings or specs,
        identifying key thermal area targets dynamically.
        """
        # Search for structural area indicators in text (e.g., '2500 sqft', '300 sqm')
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*(sqft|sqm|square\s+meters|sq\.ft)', text_content, re.IGNORECASE)
        detected_area = 200.0 # Secure fallback default
        
        if area_match:
            val = float(area_match.group(1))
            unit = area_match.group(2).lower()
            if "sqft" in unit or "sq.ft" in unit:
                detected_area = val * 0.092903
            else:
                detected_area = val

        # Default standard commercial optimization calculations for automated document pipeline
        deration_factor = 0.90
        base_load_tr = (detected_area / 12.0) * 1.05
        net_required_tr = round(base_load_tr / deration_factor, 1)
        tech_recommended = "Document-Inferred Modular Air-Cooled Scroll Array"
        
        return {
            "detected_area_sqmt": round(detected_area, 1),
            "calculated_tr": net_required_tr,
            "deration_factor": deration_factor,
            "latent_multiplier": 1.05,
            "technology": tech_recommended
        }

    def calculate_manual_scenario(self, scenario_type, params, amb_temp=None, amb_rh=None):
        deration_factor = 0.95
        latent_multiplier = 1.0

        if amb_temp is not None and amb_rh is not None:
            if amb_temp >= 45: deration_factor = 0.82
            elif amb_temp >= 40: deration_factor = 0.88
            elif amb_temp >= 35: deration_factor = 0.92
                
            if amb_rh >= 75: latent_multiplier = 1.18
            elif amb_rh >= 60: latent_multiplier = 1.10
        else:
            loc = self.location.lower()
            if any(x in loc for x in ["delhi", "indore", "rajasthan"]): deration_factor = 0.88
            elif any(x in loc for x in ["mumbai", "chennai", "kolkata"]): deration_factor = 0.92; latent_multiplier = 1.15

        if "Scenario 1" in scenario_type:
            glass_area = params.get("glass_area_sqmt", 0)
            appliances_kw = params.get("appliances_kw", 0)
            base_load_tr = (self.area_sqmt / 16.0) * latent_multiplier
            gross_tr = base_load_tr + (glass_area * 0.08) + (appliances_kw * 0.284)
            net_required_tr = round(gross_tr / deration_factor, 1)
            tech_recommended = "High-Efficiency Inverter VRF System (AHRI 1230 Certified)"
        elif "Scenario 2" in scenario_type:
            occupancy = params.get("occupancy", 10)
            equipment_kw = params.get("equipment_kw", 0)
            floors = params.get("floors", 1)
            base_load_tr = ((self.area_sqmt * floors) / 12.0) * latent_multiplier
            gross_tr = base_load_tr + ((occupancy * 500) / 12000) + (equipment_kw * 0.284)
            net_required_tr = round(gross_tr / deration_factor, 1)
            tech_recommended = "Central Water-Cooled Screw Chiller Plant"
        else:
            water_flow_lpm = params.get("water_flow_lpm", 100)
            delta_t = params.get("temp_in", 32) - params.get("temp_out", 12)
            process_tr = ((water_flow_lpm / 60.0) * 4.186 * delta_t) / 3.517
            net_required_tr = round((process_tr * 1.25) / deration_factor, 1)
            tech_recommended = "Heavy-Duty Process Water Chiller (Shell & Tube Framework)"

        return net_required_tr, deration_factor, latent_multiplier, tech_recommended

    def generate_wizard_boq(self, target_tr, scenario_type):
        total_cfm = round(target_tr * 400, 0)
        chilled_water_flow_gpm = round(target_tr * 2.4, 1)
        if "Industrial" in scenario_type or "Document-Inferred" in scenario_type:
            return [
                {"Item": "Industrial Process Chiller", "Specification": f"Heavy duty skid unit Cap {target_tr} TR", "Qty": "1 Unit"},
                {"Item": "Primary Circulation Pump", "Specification": f"SS316 Pump Flow {chilled_water_flow_gpm} GPM", "Qty": "2 Nos"},
                {"Item": "Insulated Process Piping", "Specification": "MS Heavy Class Pipe with PUF insulation", "Qty": "1 Lot"}
            ]
        elif "Commercial" in scenario_type:
            return [
                {"Item": "Central Air-Conditioning Plant", "Specification": f"High COP Chiller Assembly Cap {target_tr} TR", "Qty": "1 Lot"},
                {"Item": "Air Handling Units (AHUs)", "Specification": f"Double skin layout running at {total_cfm} Total CFM", "Qty": f"{max(1, int(total_cfm//3500))} Units"},
                {"Item": "Galvanized Iron Ducts", "Specification": "Pre fabricated rectangular ducts matching SMACNA class", "Qty": f"{int(target_tr * 12)} Sqm"}
            ]
        else:
            return [
                {"Item": "VRF Outdoor Heat Pump Module", "Specification": f"Top Discharge Inverter unit Cap {target_tr} TR", "Qty": "1 Unit"},
                {"Item": "Indoor Terminal Units", "Specification": "Mix of Hi Wall Slim profiles and Cassettes", "Qty": f"{max(2, int(target_tr//1.5))} Units"}
            ]