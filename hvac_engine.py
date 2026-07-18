# ==========================================
# SECURE CORE ENGINEERING LOGIC ENGINE
# Standards Reference: ISHRAE / ASHRAE / ECBC India
# ==========================================

class HVACValidatorEngine:
    def __init__(self, location, space_type, area_sqmt, design_tr, safety_factor=1.15):
        self.location = location
        self.space_type = space_type
        self.area_sqmt = area_sqmt
        self.design_tr = design_tr
        self.safety_factor = safety_factor
        
        # Indian ECBC Wall U-Value Limits (W/m²K) for Composite/Hot-Dry Climates
        self.MAX_WALL_U_VALUE = 0.40 
        # ISHRAE Baseline Ventilation Requirements (CFM per Person + CFM per SqFt converted roughly)
        self.VENTILATION_RULES = {
            "Office": {"cfm_per_person": 5, "cfm_per_sqft": 0.06, "occupant_density_sqmt": 10},
            "Server Room": {"cfm_per_person": 5, "cfm_per_sqft": 0.12, "occupant_density_sqmt": 50},
            "Conference Room": {"cfm_per_person": 15, "cfm_per_sqft": 0.06, "occupant_density_sqmt": 3}
        }

    def calculate_heat_load(self, actual_wall_u, current_occupancy):
        """
        Calculates heat load using standard thermal transmittance.
        Q = U * A * deltaT + Internal Heat Gains
        Indian design ambient peak outdoor temp assumed at 43°C, indoor comfort at 24°C (deltaT = 19)
        """
        delta_t = 19 
        
        # 1. Envelope Heat Gain (Sensible)
        envelope_load_watts = actual_wall_u * (self.area_sqmt * 3) * delta_t # Assumes 3m ceiling height for wall area estimate
        
        # 2. Internal Heat Gain (People + Equipment baseline)
        if self.space_type in self.VENTILATION_RULES:
            occupants = max(current_occupancy, round(self.area_sqmt / self.VENTILATION_RULES[self.space_type]["occupant_density_sqmt"]))
        else:
            occupants = current_occupancy
            
        people_load_watts = occupants * 120 # 120W heat dissipation per person sitting
        equipment_load_watts = self.area_sqmt * 25 # 25W/sqmt standard laptop/lighting load baseline
        
        total_load_watts = (envelope_load_watts + people_load_watts + equipment_load_watts) * self.safety_factor
        
        # Convert Watts to Tons of Refrigeration (1 TR = 3517 Watts)
        calculated_tr = total_load_watts / 3517
        return round(calculated_tr, 2), occupants

    def run_compliance_check(self, actual_wall_u, current_occupancy, equipment_cop):
        """
        Executes strict cross-checks against codes and returns actionable matrices.
        """
        calculated_tr, calculated_occupants = self.calculate_heat_load(actual_wall_u, current_occupancy)
        report = {
            "status": "PASS",
            "non_compliances": [],
            "savings_suggestions": [],
            "metrics": {
                "calculated_tr": calculated_tr,
                "designed_tr": self.design_tr,
                "deviation_percentage": round(((self.design_tr - calculated_tr) / calculated_tr) * 100, 2)
            }
        }

        # Check 1: Sizing Validation (Undersized / Oversized rules)
        deviation = report["metrics"]["deviation_percentage"]
        if deviation > 20:
            report["status"] = "FAIL"
            report["non_compliances"].append(
                f"CRITICAL OVERSIZING: Designed capacity ({self.design_tr} TR) is {deviation}% higher than the calculated peak scientific requirement ({calculated_tr} TR). This will cause compressor short-cycling, poor humidity control, and high electricity bills."
            )
            # End-user commercial savings calculations based on average Indian commercial DISCOM tariffs (~₹9 per kWh)
            potential_savings = round((self.design_tr - calculated_tr) * 1.2 * 8 * 250 * 9, 0) # rough annual savings matrix
            report["savings_suggestions"].append(
                f"SUGGESTION: Downsize equipment capacity closer to {calculated_tr} TR. Implement a Multi-Stage Compressor or a Variable Frequency Drive (VFD) chiller pack. Estimated annual operational electricity savings: ~Rs. {potential_savings:,}."
            )
        elif deviation < -10:
            report["status"] = "FAIL"
            report["non_compliances"].append(
                f"CRITICAL UNDERSIZING: Designed capacity ({self.design_tr} TR) is {abs(deviation)}% lower than calculated peak thermal load ({calculated_tr} TR). The system will fail to maintain indoor comfort parameters during Indian peak summer months."
            )

        # Check 2: Building Envelope ECBC Compliance
        if actual_wall_u > self.MAX_WALL_U_VALUE:
            report["status"] = "FAIL"
            report["non_compliances"].append(
                f"ENVELOPE NON-COMPLIANCE: Wall U-Value is {actual_wall_u} W/m²K, which exceeds the max limits set by India's Energy Conservation Building Code (ECBC) max limit of {self.MAX_WALL_U_VALUE} W/m²K."
            )
            report["savings_suggestions"].append(
                "SUGGESTION: Add 50mm of Rockwool insulation or extruded polystyrene (XPS) boards to external walls to lower the U-value. This directly downsizes structural cooling infrastructure requirements."
            )

        # Check 3: Efficiency Check (BEE / AHRI baselines)
        if equipment_cop < 3.5:
            report["status"] = "FAIL"
            report["non_compliances"].append(
                f"EFFICIENCY DEFICIT: Equipment Coefficient of Performance (COP) is {equipment_cop}. Modern high-efficiency systems should meet or exceed a COP of 4.5 under AHRI standard conditions."
            )

        return report

# --- Local Test Verification Pipeline ---
if __name__ == "__main__":
    # Simulate an actual Indian corporate office project audit
    # Let's say a consultant designed a 45 TR system for a 500 sqmt space, with poor wall insulation
    validator = HVACValidatorEngine(location="Delhi", space_type="Office", area_sqmt=500, design_tr=45.0)
    audit_results = validator.run_compliance_check(actual_wall_u=0.65, current_occupancy=50, equipment_cop=3.0)
    
    print("\n=======================================================")
    print("      HVAC VALIDATOR ENGINEERING ENGINE TEST RUN       ")
    print("=======================================================")
    print(f"AUDIT STATUS: {audit_results['status']}")
    print(f"Calculated Ideal Load: {audit_results['metrics']['calculated_tr']} TR")
    print(f"User Designed Load: {audit_results['metrics']['designed_tr']} TR")
    print(f"Sizing Deviation: {audit_results['metrics']['deviation_percentage']}%")
    print("\nIdentified Issues / Non-Compliances:")
    for issue in audit_results['non_compliances']:
        print(f" ❌ {issue}")
    print("\nActionable Optimization & Financial Savings:")
    for suggestion in audit_results['savings_suggestions']:
        print(f" 💡 {suggestion}")
    print("=======================================================\n")