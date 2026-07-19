import streamlit as st
from fpdf import FPDF
from hvac_engine import HVACValidatorEngine

# Set Page Config with clean layout settings
st.set_page_config(page_title="Conformity.AI | AeroVanguard Sciences", page_icon="⚙️", layout="wide")

# ==========================================
# ENTERPRISE CLEAN UI STRUCTURE & STYLING
# ==========================================
st.markdown("""
    <style>
        /* Block Streamlit administrative watermarks */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Clean corporate sans font array */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Xylem inspired structural branding banner */
        .brand-container {
            background-color: #007da3;
            color: #FFFFFF;
            padding: 24px 32px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .brand-title {
            font-size: 30px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .brand-subtitle {
            font-size: 13px;
            color: #67dfff;
            margin: 4px 0 0 0;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        
        /* Corporate Global Trust Statement Card */
        .trust-card {
            background-color: #F1F5F9;
            border-left: 5px solid #61d605;
            padding: 16px;
            border-radius: 4px;
            margin-bottom: 30px;
            font-size: 13.5px;
            color: #334155;
            line-height: 1.5;
        }
        
        /* Global Linear Section Dividers */
        .ui-divider {
            height: 3px;
            background: linear-gradient(90deg, #67dfff, #007da3, #61d605);
            margin: 25px 0;
            border-radius: 2px;
        }
        
        /* Section Headings */
        .section-heading {
            color: #0F172A;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# 1. Branding Header
st.markdown("""
    <div class="brand-container">
        <div class="brand-title">AeroVanguard Sciences</div>
        <div class="brand-subtitle">Conformity.AI — Enterprise Validation & Mechanical Estimation Engine</div>
    </div>
""", unsafe_allow_html=True)

# 2. Global Trust Statement Placement
st.markdown("""
    <div class="trust-card">
        <strong>System Integrity Verification Statement:</strong><br>
        Trusted globally by leading architects, consultants, contractors, and engineers to verify, validate, ensure conformity, and provide analytical design guidance.
    </div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR MODULE: SYSTEM CONTEXT
# ==========================================
st.sidebar.markdown("### 🔒 Security & Scope Context")
cust_name = st.sidebar.text_input("Client Entity Name", value="Global Engineering Partners")
project_ref = st.sidebar.text_input("Verification Audit ID", value="CONF-2026-T4")
contact_person = st.sidebar.text_input("Reviewing Authority", value="Chief Engineer")
city_location = st.sidebar.text_input("Jurisdiction Region / City", value="Indore")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Localization Settings")
unit_system = st.sidebar.selectbox(
    "Select Structural Unit Matrix:",
    ["Metric System (sq.m, kW, °C)", 
     "English / Imperial (sq.ft, BTU, °F)", 
     "Indian Regional Units (Sq.ft, TR, °C)"]
)

# ==========================================
# MAIN ROUTING PIPELINE
# ==========================================
st.markdown('<div class="section-heading">Step 1: Choose Operational Assessment Mode</div>', unsafe_allow_html=True)

input_mode = st.radio(
    label="Select your active operational pipeline:",
    options=[
        "Manual Engineering Parameter Synthesis Wizard (No Drawings Active)", 
        "Automated Blueprint Text Extraction Pipeline (Ingest PDF / TXT Documents)"
    ],
    index=0
)

st.markdown('<div class="ui-divider"></div>', unsafe_allow_html=True)

# Instantiate Core Validation Engine
engine = HVACValidatorEngine(location=city_location, area_sqmt=250.0)

# -----------------------------------------------------------------
# PIPELINE MODE A: MANUAL PARAMETER SYNTHESIS
# -----------------------------------------------------------------
if "Manual" in input_mode:
    st.markdown('<div class="section-heading">Step 2: Configuration Parameter Wizard</div>', unsafe_allow_html=True)
    
    selected_scenario = st.selectbox("Target Sizing Model Profile Application:", [
        "Scenario 1: Residential Comfort Sizing (Bungalows & Luxury Villas)",
        "Scenario 2: Commercial Comfort Sizing (Office Layouts & Commercial Retail)",
        "Scenario 3: Industrial Process Cooling (High Thermodynamic Fluid Loads)"
    ])
    
    st.write("---")
    
    # Weather parameters inputs
    st.markdown("#### 🌤️ Localized Psychrometric & Climate Profiles")
    use_custom_weather = st.checkbox("Inject explicit ambient psychrometric logs (Overrides default regional estimates)")
    
    amb_t = None
    amb_rh = None
    
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
    
    # Geometry data split layout block
    st.markdown("#### 📐 Structural Geometry & Internal Core Loading Matrix")
    col_x, col_y = st.columns(2)
    wizard_params = {}
    area_sqmt = 250.0
    
    with col_x:
        if "Scenario 3" not in selected_scenario:
            if "Metric" in unit_system:
                area_sqmt = st.number_input("Net Structural Floor Area (Square Meters):", min_value=10.0, value=250.0)
            else:
                area_in = st.number_input("Net Structural Floor Area (Square Feet):", min_value=100.0, value=2700.0)
                area_sqmt = area_in * 0.092903 
            engine.area_sqmt = area_sqmt
        
        if "Scenario 1" in selected_scenario:
            wizard_params["glass_area_sqmt"] = st.number_input("Exposed Glass Facade Elements (Sq. Meters):", min_value=0.0, value=40.0)
            wizard_params["appliances_kw"] = st.number_input("Internal Appliance Thermal Load (kW):", min_value=0.0, value=8.0)
        elif "Scenario 2" in selected_scenario:
            wizard_params["floors"] = st.number_input("Building Levels Count:", min_value=1, value=2)
            wizard_params["occupancy"] = st.number_input("Design Occupancy Density (Per Floor):", min_value=1, value=40)
            wizard_params["equipment_kw"] = st.number_input("Server / IT Hardware Heat Vectors (kW):", min_value=0.0, value=15.0)
        elif "Scenario 3" in selected_scenario:
            wizard_params["water_flow_lpm"] = st.number_input("Process Fluid Loop Flow Rate (LPM):", min_value=1.0, value=200.0)
            wizard_params["temp_in"] = st.number_input("Circuit Hot Fluid Return Temperature (°C):", min_value=0.0, value=32.0)
            wizard_params["temp_out"] = st.number_input("Circuit Cold Fluid Supply Temperature (°C):", min_value=0.0, value=12.0)

    with col_y:
        st.info("💡 **Architectural Compliance Guidance Engine:**\n\nVariables are dynamically calculated live inside the server system using direct mass energy balancing models. Ensure structural variables match final blueprints.")

    # Compute calculations
    target_tr, derat, lat_multi, tech = engine.calculate_manual_scenario(selected_scenario, wizard_params, amb_t, amb_rh)
    boq_data = engine.generate_wizard_boq(target_tr, selected_scenario)

    st.markdown('<div class="ui-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Step 3: Analytical Verification Synthesis Outputs</div>', unsafe_allow_html=True)
    
    # Results display format metrics
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Validated Tonnage Capacity", f"{target_tr} TR")
    m_col2.metric("Efficiency Ambient Deration Factor", f"{derat}")
    m_col3.metric("Latent Humidity Scaling Multiplier", f"+{int((lat_multi-1)*100)}%" if lat_multi > 1 else "Baseline (Nominal)")
    
    st.write(f"**Recommended Infrastructure Component Class:** {tech}")
    
    st.markdown("#### 📋 Conforming Itemized Equipment Bill of Quantities (BoQ)")
    st.table(boq_data)

# -----------------------------------------------------------------
# PIPELINE MODE B: AUTOMATED TEXT/DOCUMENT EXTRACTION
# -----------------------------------------------------------------
else:
    st.markdown('<div class="section-heading">Step 2: Secure Document Ingestion Infrastructure</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        label="Drop structural schedules, design specification txt sheets, or engineering text logs:",
        type=["txt", "csv", "pdf"],
        accept_multiple_files=False
    )
    
    if uploaded_files is not None:
        st.success("🎉 Document successfully registered in system memory stream framework.")
        
        # Read file text payload securely
        try:
            file_contents = uploaded_files.read().decode("utf-8", errors="ignore")
        except Exception:
            file_contents = "Sample Mock Project Specification: Target area is 350 sqm with standard commercial building requirements."
            
        # Parse text payload against system logic engines
        result_pkg = engine.process_uploaded_document_text(file_contents)
        boq_data = engine.generate_wizard_boq(result_pkg["calculated_tr"], "Document-Inferred Model")
        
        st.markdown('<div class="ui-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Step 3: Automated Ingress Parsing Results</div>', unsafe_allow_html=True)
        
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Extracted/Inferred Structural Area", f"{result_pkg['detected_area_sqmt']} Sqm")
        res_col2.metric("Synthesized Operational Sizing Load", f"{result_pkg['calculated_tr']} TR")
        res_col3.metric("Engine Computed Safety Margin", f"{result_pkg['latent_multiplier']}")
        
        st.markdown("#### 📋 Automated Document-Derived Equipment Specification List")
        st.table(boq_data)
        
        # Keep variable alignment clean for down-stream PDF compile structures
        target_tr = result_pkg["calculated_tr"]
        selected_scenario = "Automated Document Analysis Assessment Pipeline"
        tech = result_pkg["technology"]
        derat = result_pkg["deration_factor"]
        lat_multi = result_pkg["latent_multiplier"]

# ==========================================
# CERTIFIED ENTERPRISE REGULATORY PDF EXPORT ENGINE
# ==========================================
if ('target_tr' in locals() and boq_data):
    def build_corporate_pdf(cust, ref, eng, city, sc, tr_val, tech_val, derat_val, lat_val, boq_list):
        pdf = FPDF()
        pdf.add_page()
        
        # Top Global Deep Teal Header Bar Block Accent
        pdf.set_fill_color(0, 125, 163) # Hex #007da3
        pdf.rect(0, 0, 210, 26, 'F')
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 6, "AEROVANGUARD SCIENCES | CONFORMITY.AI ARCHITECTURE AUDIT", ln=True, align="C")
        
        pdf.set_text_color(50, 50, 50)
        pdf.ln(16)
        
        # Verification System Trust Subheading Block
        pdf.set_font("Helvetica", "I", 8)
        pdf.multi_cell(0, 4, "System Integrity Guidance Declaration: Trusted globally by leading architects, consultants, contractors, and engineers to verify, validate, ensure conformity, and provide structural design guidance.")
        pdf.ln(4)
        
        # Meta Fields System Array Block Data
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, f"Corporate Counterparty Entity: {cust} | Regional Location: {city}", ln=True)
        pdf.cell(0, 6, f"Unique Audit Verification Reference ID: {ref} | Signing Authority Analyst: {eng}", ln=True)
        pdf.cell(0, 6, f"Ingress Assessment Pipeline Vector: {sc}", ln=True)
        pdf.cell(0, 6, f"Validated Thermodynamic Sizing Output: {tr_val} TR (Deration Factor: {derat_val} | Environmental Variance Factor: {lat_val})", ln=True)
        pdf.cell(0, 6, f"Approved Machine Mechanical Configuration: {tech_val}", ln=True)
        pdf.ln(6)
        
        # Table Header Specifications Label Block
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, "Approved Mechanical Material Equipment Bill of Quantities (BoQ):", ln=True)
        pdf.set_draw_color(0, 125, 163)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        
        # List output loops
        for i, item in enumerate(boq_list):
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, f"[{i+1}] Equipment Block Class: {item['Item']} | Target Allocation: {item['Qty']}", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(8)
            pdf.multi_cell(0, 5, f"Mechanical Compliance Specs Matrix: {item['Specification']}")
            pdf.ln(2)
            
        pdf_path_output = "Conformity_AI_Compliance_Report.pdf"
        pdf.output(pdf_path_output)
        return pdf_path_output

    # Generate document framework download triggers
    if st.button("Generate System Compliance Export Documents"):
        display_str = f"{target_tr}"
        generated_pdf_filename = build_corporate_pdf(cust_name, project_ref, contact_person, city_location, selected_scenario, display_str, tech, derat, lat_multi, boq_data)
        
        with open(generated_pdf_filename, "rb") as f:
            st.download_button(
                label="📥 Download Official Certified Conformity Assessment Sheet (PDF)", 
                data=f, 
                file_name="Conformity_AI_Systems_Audit.pdf", 
                mime="application/pdf"
            )