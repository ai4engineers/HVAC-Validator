import streamlit as st
from fpdf import FPDF
from hvac_engine import HVACValidatorEngine

st.set_page_config(page_title="Agni Enterprise HVAC", page_icon="🛡️", layout="wide")

# ==========================================
# ENTERPRISE BRANDING & CSS INJECTION
# ==========================================
st.markdown("""
    <style>
        /* Hide Streamlit Default Watermarks */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Global Font & Professional Styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Premium Header Styling */
        .premium-header {
            background-color: #0B192C;
            color: #FFFFFF;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        }
        .premium-header h1 {
            color: #FFFFFF;
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }
        .premium-header p {
            color: #8A94A7;
            margin: 5px 0 0 0;
            font-size: 14px;
        }
        
        /* Section styling */
        .section-header {
            color: #0B192C;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 10px;
            margin-top: 20px;
            margin-bottom: 20px;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="premium-header">
        <h1>🛡️ Agni Engineering Global Validations</h1>
        <p>SECURE INFRASTRUCTURE ASSESSMENT & HVAC THERMODYNAMIC MODELING</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR: CLIENT CREDENTIALS
# ==========================================
st.sidebar.markdown("### 🔒 Secure Session Data")
cust_name = st.sidebar.text_input("Corporate Client / Entity", placeholder="Client Name")
project_ref = st.sidebar.text_input("Project Reference ID", placeholder="REF-2026-IND")
contact_person = st.sidebar.text_input("Assigned Chief Engineer")
city_location = st.sidebar.text_input("Site Location (City/Region)", value="Indore")

st.sidebar.write("---")
st.sidebar.markdown("### 🌐 Localization Settings")
unit_system = st.sidebar.selectbox(
    "Unit Framework:",
    ["Metric System (sq.m, kW, °C)", 
     "English / Imperial (sq.ft, BTU, °F)", 
     "Indian Regional (Sq.ft, TR, °C)"]
)
st.sidebar.caption("Validated against ASHRAE & AHRI 2026 Standards.")

# ==========================================
# MAIN INTERFACE SELECTOR
# ==========================================
st.markdown('<div class="section-header">Select Operational Mode</div>', unsafe_allow_html=True)
input_mode = st.radio("", ["A: Manual Engineering Parameter Synthesis (Wizard)", "B: Automated Blueprint / Schematic Extraction (PDF)"], index=0, label_visibility="collapsed")

wizard_params = {}
selected_scenario = None
area_sqmt = 0.0
amb_t = None
amb_rh = None

if "Manual" in input_mode:
    
    selected_scenario = st.selectbox("Design Application Pipeline:", [
        "Scenario 1: Residential Comfort Cooling (Bungalow/Villa)",
        "Scenario 2: Commercial Comfort Cooling (Office/Retail)",
        "Scenario 3: Industrial Process Cooling (Thermal Fluid)"
    ])
    
    st.write("---")
    
    # ----------------------------------------------------
    # NEW: EXPLICIT AMBIENT WEATHER CONDITIONS
    # ----------------------------------------------------
    st.markdown("#### 🌤️ Localized Weather & Psychrometric Data")
    use_custom_weather = st.checkbox("Provide exact weather data (Checking this overrides city-based estimates)")
    if use_custom_weather:
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            if "English" in unit_system:
                amb_f = st.slider("Peak Ambient Dry-Bulb Temperature (°F):", min_value=70, max_value=125, value=105)
                amb_t = (amb_f - 32) * 5/9
            else:
                amb_t = st.slider("Peak Ambient Dry-Bulb Temperature (°C):", min_value=20, max_value=52, value=40)
        with w_col2:
            amb_rh = st.slider("Peak Relative Humidity (RH %):", min_value=10, max_value=100, value=50)
            
    st.write("---")
    st.markdown("#### 📐 Structural & Load Parameters")
    col_x, col_y = st.columns(2)
    
    with col_x:
        if "Scenario 3" not in selected_scenario:
            if "Metric" in unit_system:
                area_sqmt = st.number_input("Net Floor Area (Square Meters):", min_value=10.0, value=250.0, step=10.0)
            else:
                area_in = st.number_input("Net Floor Area (Square Feet):", min_value=100.0, value=2700.0, step=100.0)
                area_sqmt = area_in * 0.092903 
        
        if "Scenario 1" in selected_scenario:
            if "Metric" in unit_system:
                wizard_params["glass_area_sqmt"] = st.number_input("Exposed Glass Facade (Sq. Meters):", min_value=0.0, value=40.0)
            else:
                glass_in = st.number_input("Exposed Glass Facade (Sq. Feet):", min_value=0.0, value=430.0)
                wizard_params["glass_area_sqmt"] = glass_in * 0.092903
                
            wizard_params["appliances_kw"] = st.number_input("Internal Appliance Heat Load (kW):", min_value=0.0, value=8.0)
            
        elif "Scenario 2" in selected_scenario:
            wizard_params["floors"] = st.number_input("Floor Count:", min_value=1, value=2, step=1)
            wizard_params["occupancy"] = st.number_input("Peak Human Occupancy (Per Floor):", min_value=1, value=40)
            wizard_params["equipment_kw"] = st.number_input("IT Hardware / Server Load (kW):", min_value=0.0, value=15.0)
            
        elif "Scenario 3" in selected_scenario:
            if "English" in unit_system:
                flow_in = st.number_input("Process Flow Rate (GPM):", min_value=1.0, value=50.0)
                wizard_params["water_flow_lpm"] = flow_in * 3.78541
                t_in = st.number_input("Hot Return Temp (°F):", min_value=32.0, value=90.0)
                t_out = st.number_input("Target Cold Supply Temp (°F):", min_value=32.0, value=54.0)
                wizard_params["temp_in"] = (t_in - 32) * 5/9
                wizard_params["temp_out"] = (t_out - 32) * 5/9
            else:
                wizard_params["water_flow_lpm"] = st.number_input("Process Flow Rate (LPM):", min_value=1.0, value=200.0)
                wizard_params["temp_in"] = st.number_input("Hot Return Temp (°C):", min_value=0.0, value=32.0)
                wizard_params["temp_out"] = st.number_input("Target Cold Supply Temp (°C):", min_value=0.0, value=12.0)

    with col_y:
        st.success("✅ **Continuous Validations Active**\n\nThe engine is securely analyzing thermal bridging, psychrometric latent shifts, and thermodynamic energy equations in real-time.")

    # Execution
    engine = HVACValidatorEngine(location=city_location, area_sqmt=area_sqmt)
    target_tr, derat, lat_multi, tech = engine.calculate_manual_scenario(selected_scenario, wizard_params, amb_t, amb_rh)
    boq_data = engine.generate_wizard_boq(target_tr, selected_scenario)

    if "Metric" in unit_system:
        display_cap = f"{target_tr} TR ({round(target_tr * 3.517, 1)} kW cooling)"
    elif "English" in unit_system:
        display_cap = f"{round(target_tr * 12000, 0):,} BTU/hr ({target_tr} Tons)"
    else:
         display_cap = f"{target_tr} TR (Tonnage capacity)"

    st.write("---")
    st.markdown('<div class="section-header">System Physics & Asset Output</div>', unsafe_allow_html=True)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Required Capacity", display_cap)
    m_col2.metric("Temp Deration Factor", f"{derat}")
    m_col3.metric("Latent Load Shift", f"+{int((lat_multi-1)*100)}%" if lat_multi > 1 else "Nominal")
    m_col4.metric("Engineered Solution", tech.split("(")[0])
    
    st.write("### Verified Bill of Quantities (BoQ)")
    st.table(boq_data)

    def build_wizard_pdf(cust, ref, eng, city, sc, tr_str, tech, derat, lat, boq):
        pdf = FPDF()
        pdf.add_page()
        # Header styling
        pdf.set_fill_color(11, 25, 44)
        pdf.rect(0, 0, 210, 30, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 15)
        pdf.cell(0, 10, "AGNI ENGINEERING: SECURE HVAC STRUCTURAL AUDIT", ln=True, align="C")
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Corporate Entity: {cust if cust else 'N/A'} | Jurisdiction: {city}", ln=True)
        pdf.cell(0, 6, f"Project Reference: {ref if ref else 'N/A'} | Lead Analyst: {eng if eng else 'N/A'}", ln=True)
        pdf.cell(0, 6, f"Application Pipeline: {sc}", ln=True)
        pdf.cell(0, 6, f"Validated Capacity: {tr_str} (Deration: {derat} | Latent Multiplier: {lat})", ln=True)
        pdf.cell(0, 6, f"Approved Core Technology: {tech}", ln=True)
        pdf.ln(8)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Itemized Bill of Materials & Approved Specs:", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
        for i, r in enumerate(boq):
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, f"[{i+1}] Item: {r['Item']} | Qty: {r['Qty']}", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(10)
            pdf.cell(0, 5, f"Specs: {r['Specification']}", ln=True)
            pdf.ln(2)
            
        name_f = "Secure_HVAC_Engineering_Report.pdf"
        pdf.output(name_f)
        return name_f

    pdf_file = build_wizard_pdf(cust_name, project_ref, contact_person, city_location, selected_scenario, display_cap, tech, derat, lat_multi, boq_data)
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Execute Secure Download (Certified PDF)", data=f, file_name="Agni_Certified_HVAC_Audit.pdf", mime="application/pdf")

else:
    st.markdown('<div class="section-header">Secure Document Ingestion Hub</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload engineering PDFs / Text files:", accept_multiple_files=True)