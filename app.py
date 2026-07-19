import streamlit as st
from fpdf import FPDF
from hvac_engine import HVACValidatorEngine

st.set_page_config(page_title="HVAC Advanced Wizard", page_icon="🏢", layout="wide")

st.title("🏢 Advanced HVAC Design Wizard & Sizing Framework")
st.markdown("##### Direct Engineering Calculations • Ambient Multipliers • Global Unit Adaptors")
st.write("---")

# ==========================================
# SIDEBAR: CLIENT CREDENTIALS
# ==========================================
st.sidebar.header("👤 Customer Details")
cust_name = st.sidebar.text_input("Customer/Company Name", placeholder="e.g., Agni Engineering Clients")
project_ref = st.sidebar.text_input("Project Reference ID", placeholder="e.g., WIZ-2026-IND")
contact_person = st.sidebar.text_input("Contact Engineer Name")
city_location = st.sidebar.text_input("Project Site Location / City", value="Indore")

st.sidebar.write("---")
st.sidebar.header("🌐 Preferred Unit Framework")
unit_system = st.sidebar.selectbox(
    "Select Interface Units:",
    ["Metric System (sq.m, kW, LPM, °C)", 
     "English / Imperial System (sq.ft, BTU/hr, GPM, °F)", 
     "Indian Regional Field Units (Sq.ft, TR, LPM, °C)"]
)

st.sidebar.write("---")
st.sidebar.caption("⚡ **Engine Integrity:** Calculations fully map across ASHRAE psychrometric metrics automatically.")

# ==========================================
# MAIN INTERFACE SELECTOR
# ==========================================
input_mode = st.radio("Select Engineering Data Input Mode:", ["Option A: Manual Parameter Input Wizard (No Drawings Ready)", "Option B: Document Upload Processing Pipeline (PDF/TXT)"], index=0)

wizard_params = {}
selected_scenario = None
area_sqmt = 0.0

if "Manual Parameter Input Wizard" in input_mode:
    st.subheader("🛠️ Step-by-Step Mechanical Parameter Survey")
    
    selected_scenario = st.selectbox("Choose Target Engineering Scenario:", [
        "Scenario 1: Residential Bungalow (Comfort Cooling)",
        "Scenario 2: Commercial Building (Comfort Cooling)",
        "Scenario 3: Process Cooling Industrial (Thermal Fluid Load)"
    ])
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        # DYNAMIC ACCORDING TO USER ACCESSIBILITY SELECTORS
        if "Scenario 3" not in selected_scenario:
            if "Metric" in unit_system:
                area_in = st.number_input("Net Floor / Carpet Area (Square Meters):", min_value=10.0, value=250.0, step=10.0)
                area_sqmt = area_in
            else:
                area_in = st.number_input("Net Floor / Carpet Area (Square Feet):", min_value=100.0, value=2700.0, step=100.0)
                area_sqmt = area_in * 0.092903  # Convert to standard engine metric layout unit internally
        
        if "Scenario 1" in selected_scenario:
            if "Metric" in unit_system:
                wizard_params["glass_area_sqmt"] = st.number_input("Estimated Exposed Facade Glass Area (Sq. Meters):", min_value=0.0, value=40.0)
            else:
                glass_in = st.number_input("Estimated Exposed Facade Glass Area (Sq. Feet):", min_value=0.0, value=430.0)
                wizard_params["glass_area_sqmt"] = glass_in * 0.092903
                
            wizard_params["appliances_kw"] = st.number_input("Total Internal Appliance Heat Dissipation Load (kW):", min_value=0.0, value=8.0)
            
        elif "Scenario 2" in selected_scenario:
            wizard_params["floors"] = st.number_input("Number of Superstructure Floors:", min_value=1, value=2, step=1)
            wizard_params["occupancy"] = st.number_input("Peak Human Occupancy Count per Floor:", min_value=1, value=40)
            wizard_params["equipment_kw"] = st.number_input("Server / IT Hardware Load Vector (kW):", min_value=0.0, value=15.0)
            
        elif "Scenario 3" in selected_scenario:
            if "English" in unit_system:
                flow_in = st.number_input("Fluid Circulation Flow Rate (Gallons Per Minute - GPM):", min_value=1.0, value=50.0)
                wizard_params["water_flow_lpm"] = flow_in * 3.78541
                t_in = st.number_input("Hot Return Fluid Temperature (°F):", min_value=32.0, value=90.0)
                t_out = st.number_input("Target Cold Chilled Supply Water Temp (°F):", min_value=32.0, value=54.0)
                wizard_params["temp_in"] = (t_in - 32) * 5/9
                wizard_params["temp_out"] = (t_out - 32) * 5/9
            else:
                wizard_params["water_flow_lpm"] = st.number_input("Fluid Circulation Flow Rate (Liters Per Minute - LPM):", min_value=1.0, value=200.0)
                wizard_params["temp_in"] = st.number_input("Hot Return Process Water Temperature (°C):", min_value=0.0, value=32.0)
                wizard_params["temp_out"] = st.number_input("Target Cold Chilled Supply Water Temperature (°C):", min_value=0.0, value=12.0)

    with col_y:
        st.info("💡 **Inclusive Multi-Unit Interpreter Enabled**\n\n"
                "The engine translates everyday consumer entries (like square feet or Fahrenheit) into thermodynamic physics standards automatically behind the scenes. No mechanical degree required!")

    # Execute Calculations
    engine = HVACValidatorEngine(location=city_location, area_sqmt=area_sqmt)
    target_tr, derat, tech = engine.calculate_manual_scenario(selected_scenario, wizard_params)
    boq_data = engine.generate_wizard_boq(target_tr, selected_scenario)

    # Dynamic unit presentation for output sizing
    if "Metric" in unit_system:
        display_cap = f"{target_tr} TR ({round(target_tr * 3.517, 1)} kW cooling capacity)"
    elif "English" in unit_system:
        display_cap = f"{round(target_tr * 12000, 0):,} BTU/hr ({target_tr} Tons)"
    else:
         display_cap = f"{target_tr} TR (Tonnage capacity)"

    st.write("---")
    st.subheader("📊 Instant Engineering Sizing & Asset Output")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Recommended Net Capacity", display_cap)
    m_col2.metric("Ambient Deration Multiplier", f"{derat} (Efficiency Factor)")
    m_col3.metric("Recommended System Tech", tech)
    
    st.write("### 📋 Generated Technical Bill of Quantities (BoQ)")
    st.table(boq_data)

    # SECURE PDF GENERATOR BLOCK WITH CLEANED LINE-WRAPPING WIDTHS TO SOLVE EXCEPTION
    def build_wizard_pdf(cust, ref, eng, city, sc, tr_str, tech, derat, boq):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "EXECUTIVE HVAC INFRASTRUCTURE STRUCTURAL ESTIMATE", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Client Profile: {cust if cust else 'N/A'} | Site City: {city}", ln=True)
        pdf.cell(0, 6, f"Project Reference: {ref if ref else 'N/A'} | Lead Engineer: {eng if eng else 'N/A'}", ln=True)
        pdf.cell(0, 6, f"Target Pipeline: {sc}", ln=True)
        pdf.cell(0, 6, f"Engine Calculated Tonnage Capacity: {tr_str} (Deration: {derat})", ln=True)
        pdf.cell(0, 6, f"Selected Technology Core: {tech}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Itemized Bill of Materials / Equipment Specs:", ln=True)
        pdf.ln(2)
        
        # Safe structural rendering loop avoiding long multi_cell line calculations
        for i, r in enumerate(boq):
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, f"[{i+1}] Item: {r['Item']} | Qty: {r['Qty']}", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(10) # Indent description line
            pdf.cell(0, 5, f"Specs: {r['Specification']}", ln=True)
            pdf.ln(2)
            
        name_f = "Wizard_HVAC_Engineering_Report.pdf"
        pdf.output(name_f)
        return name_f

    pdf_file = build_wizard_pdf(cust_name, project_ref, contact_person, city_location, selected_scenario, display_cap, tech, derat, boq_data)
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Export Engineering Report & Estimate (PDF)", data=f, file_name="HVAC_Wizard_Report.pdf", mime="application/pdf")

else:
    st.subheader("📁 Drag & Drop Document Verification Hub")
    uploaded_files = st.file_uploader("Upload engineering PDFs / Text files:", accept_multiple_files=True)