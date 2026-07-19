import streamlit as st
from fpdf import FPDF
from hvac_engine import HVACValidatorEngine

st.set_page_config(page_title="Conformity.AI | AeroVanguard", page_icon="⚙️", layout="wide")

# ==========================================
# CUSTOM TEAL & GRADIENT BRANDING INJECTION
# ==========================================
st.markdown("""
    <style>
        /* Hide Default System Footers/Menus for Proprietary Look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Clean Global Typography (Conforms to UI, Offline and Print guidelines) */
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #FFFFFF;
        }
        
        /* Xylem-Inspired Corporate Header with the exact #007da3 base */
        .xylem-header {
            background-color: #007da3;
            color: #FFFFFF;
            padding: 30px;
            border-radius: 4px;
            margin-bottom: 25px;
            border-bottom: 5px solid #67dfff;
        }
        .xylem-header h1 {
            color: #FFFFFF !important;
            margin: 0;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .xylem-header p {
            color: #67dfff;
            margin: 5px 0 0 0;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1px;
        }
        
        /* Corporate Trust Statement Block */
        .trust-banner {
            background-color: #F8FAFC;
            border-left: 4px solid #007da3;
            padding: 15px;
            margin-bottom: 25px;
            font-size: 13.5px;
            color: #334155;
            font-style: italic;
            border-radius: 0 4px 4px 0;
        }
        
        /* Linear Gradient Dividers mapping exact requested color spectrum */
        .gradient-line {
            height: 4px;
            background: linear-gradient(90deg, #67dfff, #007da3, #61d605);
            margin-top: 25px;
            margin-bottom: 25px;
            border-radius: 2px;
        }
        
        /* Metric Cards Accentuation */
        div[data-testid="stMetricValue"] {
            color: #007da3 !important;
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

# Main Branding Header Bar
st.markdown("""
    <div class="xylem-header">
        <h1>AeroVanguard Sciences</h1>
        <p>CONFORMITY.AI — ENTERPRISE VALIDATION & MECHANICAL ESTIMATION ENGINE</p>
    </div>
""", unsafe_allow_html=True)

# Trust Statement Insertion
st.markdown("""
    <div class="trust-banner">
        🛡️ <strong>System Assurance Statement:</strong> Trusted globally by leading architects, consultants, contractors, and engineers to verify, validate, ensure conformity, and provide structural design guidance.
    </div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR: SECURE ACCOUNT DETAILS
# ==========================================
st.sidebar.markdown("### 🔒 System Security Context")
cust_name = st.sidebar.text_input("Client Entity Name", placeholder="e.g., Global Infrastructure Corp")
project_ref = st.sidebar.text_input("Verification Audit ID", placeholder="e.g., CONF-2026-T4")
contact_person = st.sidebar.text_input("Reviewing Authority / Engineer")
city_location = st.sidebar.text_input("Jurisdiction Region / City", value="Indore")

st.sidebar.write("---")
st.sidebar.markdown("### 🌐 Localization Settings")
unit_system = st.sidebar.selectbox(
    "Unit Paradigm Selector:",
    ["Metric System (sq.m, kW, °C)", 
     "English / Imperial (sq.ft, BTU, °F)", 
     "Indian Regional Units (Sq.ft, TR, °C)"]
)
st.sidebar.caption("Compliant Framework pipelines: AHRI 550/590, AHRI 1230, and ASHRAE Weather Metrics.")

# ==========================================
# CORE SCENARIO WIZARD SYSTEM
# ==========================================
st.markdown("### 📊 Operational Mode Routing Pipelines")
input_mode = st.radio("", ["Option A: Manual Parameter Synthesis Framework (No Drawings Active)", "Option B: Automated Blueprint Text Extraction Pipeline (PDF/TXT)"], index=0, label_visibility="collapsed")

st.markdown('<div class="gradient-line"></div>', unsafe_allow_html=True)

wizard_params = {}
selected_scenario = None
area_sqmt = 0.0
amb_t = None
amb_rh = None

if "Manual Parameter" in input_mode:
    st.markdown("### 🛠️ Mechanical Parameter Survey Wizard")
    selected_scenario = st.selectbox("Select Target Sizing Model Scenario:", [
        "Scenario 1: Residential Comfort Sizing (Bungalows & Luxury Villas)",
        "Scenario 2: Commercial Comfort Sizing (Office Layouts & Commercial Retail)",
        "Scenario 3: Industrial Process Cooling (High Thermodynamic Fluid Loads)"
    ])
    
    st.write("---")
    
    # Psychrometric Parameter Inputs
    st.markdown("#### 🌤️ Environmental Conditions & Climate Profile")
    use_custom_weather = st.checkbox("Inject explicit ambient psychrometric logs (Overrides city baseline profiles)")
    if use_custom_weather:
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            if "English" in unit_system:
                amb_f = st.slider("Design Ambient Dry-Bulb Temperature (°F):", min_value=70, max_value=125, value=104)
                amb_t = (amb_f - 32) * 5/9
            else:
                amb_t = st.slider("Design Ambient Dry-Bulb Temperature (°C):", min_value=20, max_value=52, value=40)
        with w_col2:
            amb_rh = st.slider("Design Ambient Relative Humidity (RH %):", min_value=10, max_value=100, value=50)
            
    st.write("---")
    st.markdown("#### 📐 Geometry & Internal Loading Matrix")
    col_x, col_y = st.columns(2)
    
    with col_x:
        if "Scenario 3" not in selected_scenario:
            if "Metric" in unit_system:
                area_sqmt = st.number_input("Net Structural Floor Area (Square Meters):", min_value=10.0, value=250.0, step=10.0)
            else:
                area_in = st.number_input("Net Structural Floor Area (Square Feet):", min_value=100.0, value=2700.0, step=100.0)
                area_sqmt = area_in * 0.092903 
        
        if "Scenario 1" in selected_scenario:
            if "Metric" in unit_system:
                wizard_params["glass_area_sqmt"] = st.number_input("Exposed Glass Facade Elements (Sq. Meters):", min_value=0.0, value=40.0)
            else:
                glass_in = st.number_input("Exposed Glass Facade Elements (Sq. Feet):", min_value=0.0, value=430.0)
                wizard_params["glass_area_sqmt"] = glass_in * 0.092903
                
            wizard_params["appliances_kw"] = st.number_input("Internal Appliance Thermal Load Contribution (kW):", min_value=0.0, value=8.0)
            
        elif "Scenario 2" in selected_scenario:
            wizard_params["floors"] = st.number_input("Building Levels / Floor Multiplex Count:", min_value=1, value=2, step=1)
            wizard_params["occupancy"] = st.number_input("Design Occupancy Density (Per Floor Level):", min_value=1, value=40)
            wizard_params["equipment_kw"] = st.number_input("Server / IT Equipment Heat Dissipation Vectors (kW):", min_value=0.0, value=15.0)
            
        elif "Scenario 3" in selected_scenario:
            if "English" in unit_system:
                flow_in = st.number_input("Process Fluid Loop Rate (GPM):", min_value=1.0, value=50.0)
                wizard_params["water_flow_lpm"] = flow_in * 3.78541
                t_in = st.number_input("Circuit Hot Fluid Return Temperature (°F):", min_value=32.0, value=90.0)
                t_out = st.number_input("Circuit Cold Fluid Supply Temperature (°F):", min_value=32.0, value=54.0)
                wizard_params["temp_in"] = (t_in - 32) * 5/9
                wizard_params["temp_out"] = (t_out - 32) * 5/9
            else:
                wizard_params["water_flow_lpm"] = st.number_input("Process Fluid Loop Rate (LPM):", min_value=1.0, value=200.0)
                wizard_params["temp_in"] = st.number_input("Circuit Hot Fluid Return Temperature (°C):", min_value=0.0, value=32.0)
                wizard_params["temp_out"] = st.number_input("Circuit Cold Fluid Supply Temperature (°C):", min_value=0.0, value=12.0)

    with col_y:
        st.info("⚙️ **Conformity Check Engine Ingress Rules:**\n\n"
                "Data entry elements auto-convert across localization parameters to match core thermodynamic mass flow formulations, ensuring absolute integrity for regulatory compliance sign-offs.")

    # Calculations execution
    engine = HVACValidatorEngine(location=city_location, area_sqmt=area_sqmt)
    target_tr, derat, lat_multi, tech = engine.calculate_manual_scenario(selected_scenario, wizard_params, amb_t, amb_rh)
    boq_data = engine.generate_wizard_boq(target_tr, selected_scenario)

    if "Metric" in unit_system:
        display_cap = f"{target_tr} TR ({round(target_tr * 3.517, 1)} kW cooling)"
    elif "English" in unit_system:
        display_cap = f"{round(target_tr * 12000, 0):,} BTU/hr ({target_tr} Tons)"
    else:
         display_cap = f"{target_tr} TR (Net Tons)"

    st.write("---")
    st.markdown('### 🏢 Analytical Output & Sizing Synthesis', unsafe_allow_html=True)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Validated Net Capacity", display_cap)
    m_col2.metric("Condenser Deration", f"{derat}")
    m_col3.metric("Latent Mult Variance", f"+{int((lat_multi-1)*100)}%" if lat_multi > 1 else "Baseline")
    m_col4.metric("Conforming Equipment", tech.split(" (")[0])
    
    st.write("---")
    st.markdown("### 📋 Compliant Bill of Quantities (BoQ) Specifications")
    st.table(boq_data)

    # PREMIUM RE-ENGINEERED COMPACT CORPORATE PDF COMPLIANCE FORMATTING REPORT
    def build_wizard_pdf(cust, ref, eng, city, sc, tr_str, tech, derat, lat, boq):
        pdf = FPDF()
        pdf.add_page()
        
        # Premium Deep Teal Top Decorative Bar (Matching website palette layout style)
        pdf.set_fill_color(0, 125, 163) # #007da3
        pdf.rect(0, 0, 210, 24, 'F')
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 5, "AEROVANGUARD SCIENCES | CONFORMITY.AI AUDIT", ln=True, align="C")
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # Trust statement inside print documentation
        pdf.set_font("Helvetica", "I", 8)
        pdf.multi_cell(0, 4, "System Assurance: Trusted globally by leading architects, consultants, contractors, and engineers to verify, validate, ensure conformity, and provide structural design guidance.")
        pdf.ln(4)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Client Profile Entity: {cust if cust else 'N/A'} | Jurisdiction Region: {city}", ln=True)
        pdf.cell(0, 6, f"Verification Audit Reference ID: {ref if ref else 'N/A'} | Reviewing Authority: {eng if eng else 'N/A'}", ln=True)
        pdf.cell(0, 6, f"Evaluated Target Profile: {sc}", ln=True)
        pdf.cell(0, 6, f"Validated Plant Tonnage Design: {tr_str} (Derat: {derat} | Psychrometric Mult: {lat})", ln=True)
        pdf.cell(0, 6, f"Approved Conforming Architecture: {tech}", ln=True)
        pdf.ln(6)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, "Itemized Bill of Materials & Equipment Compliance Specs:", ln=True)
        
        # Fine accent line inside printed PDF
        pdf.set_draw_color(0, 125, 163)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        
        for i, r in enumerate(boq):
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, f"[{i+1}] Approved Core Unit: {r['Item']} | Qty Requirement: {r['Qty']}", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(8)
            pdf.cell(0, 5, f"Structural Specs Matrix: {r['Specification']}", ln=True)
            pdf.ln(1.5)
            
        name_f = "Conformity_AI_Engineering_Report.pdf"
        pdf.output(name_f)
        return name_f

    pdf_file = build_wizard_pdf(cust_name, project_ref, contact_person, city_location, selected_scenario, display_cap, tech, derat, lat_multi, boq_data)
    
    st.write("---")
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Download Certified Conformity Report (PDF)", data=f, file_name="Conformity_AI_Verification_Report.pdf", mime="application/pdf")

else:
    st.subheader("📁 Drag & Drop Document Verification Hub")
    uploaded_files = st.file_uploader("Upload engineering blueprints / schedules:", accept_multiple_files=True)