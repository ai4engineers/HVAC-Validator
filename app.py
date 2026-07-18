import streamlit as st
import PyPDF2
import re
import os
from fpdf import FPDF
from hvac_engine import HVACValidatorEngine

# ==========================================
# SECURE CONFIGURATION & ARCHITECTURE
# ==========================================
st.set_page_config(
    page_title="HVAC Engineering Validator",
    page_icon="❄️",
    layout="wide"
)

st.title("❄️ Advanced HVAC Design & Compliance Validator")
st.markdown("### National Building Code (NBC), ISHRAE, ECBC, and ASHRAE Audit Pipeline")
st.write("---")

with st.sidebar:
    st.header("🔒 Enterprise Security Gate")
    st.success("Running in FREE Local Engine Mode. No API key required.")
    st.write("---")
    st.markdown("#### Standards Verified:")
    st.caption("• ISHRAE Comfort Cooling Standard\n• Energy Conservation Building Code (ECBC 2017)\n• NBC 2016 Part 4 & Part 8\n• ASHRAE 62.1 Ventilation")

# ==========================================
# FREE LOCAL PARSER ENGINE
# ==========================================
def extract_text_from_file(uploaded_file):
    filename = uploaded_file.name.lower()
    if filename.endswith('.txt'):
        try:
            return uploaded_file.read().decode("utf-8")
        except:
            return ""
    elif filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            return extracted_text
        except:
            return ""
    return ""

def local_regex_parser(text):
    data = {
        "location": "Delhi",
        "space_type": "Office",
        "area_sqmt": 100.0,
        "design_tr": 10.0,
        "actual_wall_u": 0.60,
        "current_occupancy": 10,
        "equipment_cop": 3.0
    }
    area_match = re.search(r'(?:Area|Footprint)[:\s]+(\d+)', text, re.IGNORECASE)
    if area_match:
        data["area_sqmt"] = float(area_match.group(1))
    tr_match = re.search(r'(?:design_tr|Capacity|Total Specified)[:\s=]+(\d+\.?\d*)', text, re.IGNORECASE)
    if tr_match:
        data["design_tr"] = float(tr_match.group(1))
    u_match = re.search(r'(?:actual_wall_u|U-value)[:\s=]+(\d+\.?\d*)', text, re.IGNORECASE)
    if u_match:
        data["actual_wall_u"] = float(u_match.group(1))
    occ_match = re.search(r'(?:Occupants|Personnel|People)[:\s]+(\d+)', text, re.IGNORECASE)
    if occ_match:
        data["current_occupancy"] = int(occ_match.group(1))
    cop_match = re.search(r'(?:equipment_cop|COP)[:\s=]+(\d+\.?\d*)', text, re.IGNORECASE)
    if cop_match:
        data["equipment_cop"] = float(cop_match.group(1))
    return data

# ==========================================
# FPDF2 REPORT GENERATOR MODULE (PURE PYTHON)
# ==========================================
class HVACPDFReport(FPDF):
    def header(self):
        # Top banner styling
        self.set_fill_color(26, 37, 47) # Dark Blue/Grey
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, -5, 'HVAC ENGINEERING VALIDATION REPORT', ln=True, align='L')
        self.set_font('Helvetica', 'I', 9)
        self.cell(0, 15, 'Automated ISHRAE / ECBC / NBC Compliance Audit System', ln=True, align='L')
        self.ln(12)

    def footer(self):
        # Position at 2.5 cm from bottom
        self.set_y(-25)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(100, 116, 139)
        disclaimer = (
            "REGULATORY COMPLIANCE DISCLAIMER: This validation analysis has been executed through automated "
            "programmatic scripts utilizing mathematical algorithms mapping to ISHRAE, ASHRAE, and Indian Building Codes. "
            "This output is structured as a structural engineering design peer-check. Complete professional liability, signing, "
            "and physical installation oversight remain explicitly under the direct purview of the licensed, emplaned engineer or "
            "architect of record representing the structural project."
        )
        self.multi_cell(0, 3, disclaimer, align='J')

def generate_fpdf_report(extracted, audit):
    pdf = HVACPDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)
    
    # Status Alert box
    pdf.ln(5)
    if audit["status"] == "FAIL":
        pdf.set_fill_color(192, 57, 43) # Deep Red
        status_text = "STATUS: NON-COMPLIANCE DETECTED"
    else:
        pdf.set_fill_color(39, 174, 96) # Green
        status_text = "STATUS: COMPLIANT DESIGN"
        
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, status_text, ln=True, align='C', fill=True)
    pdf.ln(5)

    # Section 1
    pdf.set_text_color(44, 62, 80)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "1. Project Profile Context", ln=True)
    pdf.set_font('Helvetica', '', 10)
    
    # Table Grid
    pdf.cell(95, 7, "Location Context Zone:", border=1)
    pdf.cell(85, 7, str(extracted['location']), border=1, ln=True)
    pdf.cell(95, 7, "Space Usage Profiling:", border=1)
    pdf.cell(85, 7, str(extracted['space_type']), border=1, ln=True)
    pdf.cell(95, 7, "Evaluated Net Area:", border=1)
    pdf.cell(85, 7, f"{extracted['area_sqmt']} Sq. Meters", border=1, ln=True)
    pdf.cell(95, 7, "Target Personnel Count:", border=1)
    pdf.cell(85, 7, f"{extracted['current_occupancy']} Occupants", border=1, ln=True)
    pdf.ln(5)

    # Section 2
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "2. Thermodynamic Sizing Matrix", ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(95, 7, "Calculated Scientific Load Requirement:", border=1)
    pdf.cell(85, 7, f"{audit['metrics']['calculated_tr']} TR", border=1, ln=True)
    pdf.cell(95, 7, "User Specified Design Capacity:", border=1)
    pdf.cell(85, 7, f"{audit['metrics']['designed_tr']} TR", border=1, ln=True)
    pdf.cell(95, 7, "Structural Capacity Deviation:", border=1)
    pdf.cell(85, 7, f"{audit['metrics']['deviation_percentage']}%", border=1, ln=True)
    pdf.ln(5)

    # Section 3
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "3. Code & Standard Infractions", ln=True)
    pdf.set_font('Helvetica', '', 10)
    if audit["non_compliances"]:
        for issue in audit["non_compliances"]:
            pdf.multi_cell(0, 5, f"- {issue}")
            pdf.ln(2)
    else:
        pdf.cell(0, 5, "- None. The baseline meets general sizing code rules.", ln=True)
    pdf.ln(3)

    # Section 4
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "4. Value Engineering & Energy Optimization", ln=True)
    pdf.set_font('Helvetica', '', 10)
    if audit["savings_suggestions"]:
        for suggestion in audit["savings_suggestions"]:
            pdf.multi_cell(0, 5, f"- {suggestion}")
            pdf.ln(2)
    else:
        pdf.cell(0, 5, "- No optimization options flagged.", ln=True)

    output_filename = "hvac_compliance_report.pdf"
    pdf.output(output_filename)
    return output_filename

# ==========================================
# MAIN INTERACTION FLOW
# ==========================================
uploaded_file = st.file_uploader("Upload HVAC Design Document or Specification Sheet", type=["pdf", "txt"])

if uploaded_file is not None:
    st.success("File uploaded securely to memory.")
    document_text = extract_text_from_file(uploaded_file)
        
    if document_text:
        extracted_data = local_regex_parser(document_text)
        
        st.subheader("📋 Extracted Project Parameters")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Location", extracted_data.get("location"))
        col2.metric("Space Profile", extracted_data.get("space_type"))
        col3.metric("Floor Area", f"{extracted_data.get('area_sqmt')} m²")
        col4.metric("Designed Capacity", f"{extracted_data.get('design_tr')} TR")
        
        st.write("---")
        st.subheader("🛡️ Automated Compliance Audit Report")
        
        engine = HVACValidatorEngine(
            location=extracted_data.get("location"),
            space_type=extracted_data.get("space_type"),
            area_sqmt=extracted_data.get("area_sqmt"),
            design_tr=extracted_data.get("design_tr")
        )
        
        audit = engine.run_compliance_check(
            actual_wall_u=extracted_data.get("actual_wall_u"),
            current_occupancy=extracted_data.get("current_occupancy"),
            equipment_cop=extracted_data.get("equipment_cop")
        )
        
        if audit["status"] == "FAIL":
            st.error("🚨 AUDIT STATUS: NON-COMPLIANCES IDENTIFIED")
        else:
            st.success("✅ AUDIT STATUS: PASSED COMPLIANCE")
        
        st.write(f"**Calculated Ideal Scientific Load:** {audit['metrics']['calculated_tr']} TR")
        st.write(f"**Your Design Capacity:** {audit['metrics']['designed_tr']} TR")
        st.write(f"**Sizing Deviation:** {audit['metrics']['deviation_percentage']}%")
        
        st.markdown("#### ❌ Critical Infractions & Missing Compliances")
        if audit["non_compliances"]:
            for issue in audit["non_compliances"]:
                st.markdown(f"- {issue}")
        else:
            st.write("No severe code violations detected.")
            
        st.markdown("#### 💡 Value Engineering & Optimization Suggestions")
        if audit["savings_suggestions"]:
            for suggestion in audit["savings_suggestions"]:
                st.info(suggestion)

        # Generate the PDF file via our brand new FPDF2 engine
        pdf_path = generate_fpdf_report(extracted_data, audit)
        
        # Download button
        st.write("---")
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Official Compliance PDF Certificate",
                data=pdf_file,
                file_name="HVAC_Compliance_Audit_Report.pdf",
                mime="application/pdf"
            )