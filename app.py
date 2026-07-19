import streamlit as st
from fpdf import FPDF
from hvac_engine import HVACValidatorEngine

st.set_page_config(page_title="HVAC Advanced Wizard", page_icon="🏢", layout="wide")

st.title("🏢 Advanced HVAC Design Wizard & Sizing Framework")
st.markdown("##### Direct Engineering Calculations • Ambient Multipliers • AHRI Verification Pipelines")
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
st.sidebar.caption("⚡ **Engine Standard Integrity:** Calculations use ASHRAE weather matrices and AHRI baseline tolerances.")

# ==========================================
# MAIN INTERFACE SELECTOR
# ==========================================
input_mode = st.radio("Select Engineering Data Input Mode:", ["Option A: Manual Parameter Input Wizard (No Drawings Ready)", "Option B: Document Upload Processing Pipeline (PDF/TXT)"], index=0)

wizard_params = {}
selected_scenario = None
area_input = 0.0

if "Manual Parameter Input Wizard" in input_mode:
    st.subheader("🛠️ Step-by-Step Mechanical Parameter Survey")
    
    selected_scenario = st.selectbox("Choose Target Engineering Scenario:", [
        "Scenario 1: Residential Bungalow (Comfort Cooling)",
        "Scenario 2: Commercial Building (Comfort Cooling)",
        "Scenario 3: Process Cooling Industrial (Thermal Fluid Load)"
    ])
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        if selected_scenario != "Scenario 3: Process Cooling Industrial (Thermal Fluid Load)":
            area_input = st.number_input("Net Floor / Carpet Area (Square Meters):", min_value=10.0, value=250.0, step=10.0)
        
        if "Scenario 1" in selected_scenario:
            wizard_params["glass_area_sqmt"] = st.number_input("Estimated Exposed Facade Glass Area (Sq. Meters):", min_value=0.0, value=40.0)
            wizard_params["appliances_kw"] = st.number_input("Total Internal Appliance Heat Dissipation Load (kW):", min_value=0.0, value=8.0)
            
        elif "Scenario 2" in selected_scenario:
            wizard_params["floors"] = st.number_input("Number of Superstructure Floors:", min_value=1, value=2, step=1)
            wizard_params["occupancy"] = st.number_input("Peak Human Occupancy Count per Floor:", min_value=1, value=40)
            wizard_params["equipment_kw"] = st.number_input("Server / IT Hardware Load Vector (kW):", min_value=0.0, value=15.0)
            
        elif "Scenario 3" in selected_scenario:
            wizard_params["water_flow_lpm"] = st.number_input("Process Circuit Fluid Circulation Flow Rate (Liters Per Minute):", min_value=1.0, value=200.0)
            wizard_params["temp_in"] = st.number_input("Hot Return Process Water Temperature (°C):", min_value=0.0, value=32.0)
            wizard_params["temp_out"] = st.number_input("Target Cold Chilled Supply Water Temperature (°C):", min_value=0.0, value=12.0)

    with col_y:
        st.info("🧬 **Thermodynamic Calculation Parameters Applied:**\n\n"
                "• **Extreme Thermal Deration Map:** Accounted for localized micro-climates.\n"
                "• **AHRI Component Sizing:** Automatic conversion from gross physics tonnage bounds into standard market equipment sizes.")

    engine = HVACValidatorEngine(location=city_location, area_sqmt=area_input)
    target_tr, derat, tech = engine.calculate_manual_scenario(selected_scenario, wizard_params)
    boq_data = engine.generate_wizard_boq(target_tr, selected_scenario)

    st.write("---")
    st.subheader("📊 Instant Engineering Sizing & Asset Output")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Recommended Net Capacity", f"{target_tr} TR")
    m_col2.metric("Ambient Deration Multiplier", f"{derat} (Efficiency Factor)")
    m_col3.metric("Recommended System Tech", tech.split("(")[0])
    
    st.write("### 📋 Generated Technical Bill of Quantities (BoQ)")
    st.table(boq_data)

    def build_wizard_pdf(cust, ref, eng, city, sc, tr, tech, derat, boq):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 15)
        pdf.cell(0, 10, "EXECUTIVE HVAC INFRASTRUCTURE STRUCTURAL ESTIMATE", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Client Profile: {cust if cust else 'N/A'} | Site City: {city}", ln=True)
        pdf.cell(0, 6, f"Project Reference: {ref if ref else 'N/A'} | Lead Engineer: {eng if eng else 'N/A'}", ln=True)
        pdf.cell(0, 6, f"Target Pipeline: {sc}", ln=True)
        pdf.cell(0, 6, f"Engine Calculated Tonnage Capacity: {tr} TR (Deration Applied: {derat})", ln=True)
        pdf.cell(0, 6, f"Selected Technology Core: {tech}", ln=True)
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Itemized Bill of Materials / Equipment Specs:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        for i, r in enumerate(boq):
            pdf.multi_cell(0, 6, f"[{i+1}] {r['Item']} -> Spec: {r['Specification']} | Qty: {r['Qty']}")
        name_f = "Wizard_HVAC_Engineering_Report.pdf"
        pdf.output(name_f)
        return name_f

    pdf_file = build_wizard_pdf(cust_name, project_ref, contact_person, city_location, selected_scenario, target_tr, tech, derat, boq_data)
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Export Engineering Report & Estimate (PDF)", data=f, file_name="HVAC_Wizard_Report.pdf", mime="application/pdf")

else:
    st.subheader("📁 Drag & Drop Document Verification Hub")
    uploaded_files = st.file_uploader("Upload engineering PDFs / Text files:", accept_multiple_files=True)
    if uploaded_files:
        st.success(f"Processing {len(uploaded_files)} files under old layout rules...")