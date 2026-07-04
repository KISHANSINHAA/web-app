from fpdf import FPDF
from datetime import datetime

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Map common unicode characters to their Latin-1 equivalents
    replacements = {
        "\u2022": "-", # bullet point
        "•": "-",      # bullet point
        "\u201c": '"', # left double quote
        "\u201d": '"', # right double quote
        "“": '"',
        "”": '"',
        "\u2018": "'", # left single quote
        "\u2019": "'", # right single quote
        "‘": "'",
        "’": "'",
        "\u2013": "-", # en dash
        "\u2014": "-", # em dash
        "–": "-",
        "—": "-",
        "\u2026": "...", # ellipsis
        "…": "...",
        "\xa0": " ",   # non-breaking space
    }
    for src, dest in replacements.items():
        text = text.replace(src, dest)
    # Encode to latin-1, replacing unsupported characters with '?'
    return text.encode("latin-1", errors="replace").decode("latin-1")

class ReportPDF(FPDF):
    def __init__(self, applicant_name=None, applicant_email=None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.applicant_name = clean_text(applicant_name) if applicant_name else None
        self.applicant_email = clean_text(applicant_email) if applicant_email else None
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        # Draw top colored banner on first page, or standard small header on subsequent pages
        if self.page_no() == 1:
            # Deep Indigo Banner Fill
            self.set_fill_color(30, 27, 75)
            self.rect(0, 0, 210, 42, "F")
            
            # Title
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 20)
            self.text(15, 20, "COMPANY RESEARCH REPORT")
            
            self.set_text_color(199, 210, 254)
            self.set_font("Helvetica", "", 10)
            self.text(15, 28, f"Generated on {datetime.now().strftime('%Y-%m-%d')}")
            
            # Applicant Meta details (Top right)
            if self.applicant_name or self.applicant_email:
                self.set_text_color(255, 255, 255)
                self.set_font("Helvetica", "B", 9)
                self.text(145, 18, "SUBMITTED BY:")
                
                self.set_text_color(199, 210, 254)
                self.set_font("Helvetica", "", 8.5)
                y_offset = 24
                if self.applicant_name:
                    self.text(145, y_offset, self.applicant_name)
                    y_offset += 5
                if self.applicant_email:
                    self.text(145, y_offset, self.applicant_email)
            self.ln(35) # Spacing after banner
        else:
            # Small standard header on subsequent pages
            self.set_text_color(107, 114, 128)
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 10, "Company Research Report - Generated via Intelligence Agent", ln=1, align="L")
            self.stroke_color = (229, 231, 235)
            self.line(15, 22, 195, 22)
            self.ln(8)

    def footer(self):
        # Position footer at 15 mm from bottom
        self.set_y(-15)
        self.stroke_color = (229, 231, 235)
        self.line(15, self.get_y(), 195, self.get_y())
        
        self.set_text_color(107, 114, 128)
        self.set_font("Helvetica", "", 8)
        self.cell(100, 10, "CONFIDENTIAL - FOR EVALUATION PURPOSES ONLY", align="L")
        self.cell(80, 10, f"Page {self.page_no()}", align="R")

def generate_company_report_pdf(data: dict, applicant_name: str = None, applicant_email: str = None) -> bytes:
    pdf = ReportPDF(applicant_name, applicant_email)
    pdf.add_page()
    
    # Text colors
    primary_color = (30, 27, 75)      # Deep Indigo
    secondary_color = (79, 70, 229)  # Bright Indigo
    text_color = (31, 41, 55)         # Gray-800
    light_text_color = (107, 114, 128) # Gray-500
    
    # 1. Company Profile Section
    pdf.set_text_color(*primary_color)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "1. COMPANY PROFILE", ln=1)
    pdf.ln(2)
    
    # Drawing details grid
    pdf.set_font("Helvetica", "", 10)
    
    # Row: Company Name
    pdf.set_text_color(*light_text_color)
    pdf.cell(40, 7, "Company Name:")
    pdf.set_text_color(*text_color)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, clean_text(data.get("companyName", "Not Available")), ln=1)
    
    # Row: Website
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*light_text_color)
    pdf.cell(40, 7, "Website:")
    pdf.set_text_color(*secondary_color)
    pdf.set_font("Helvetica", "B", 10)
    # create hyperlink in PDF
    website_url = data.get("website", "Not Available")
    pdf.cell(0, 7, clean_text(website_url), ln=1, link=website_url if website_url.startswith("http") else "")
    
    # Row: Phone
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*light_text_color)
    pdf.cell(40, 7, "Phone Number:")
    pdf.set_text_color(*text_color)
    pdf.cell(0, 7, clean_text(data.get("phone", "Not Available")), ln=1)
    
    # Row: Address
    pdf.set_text_color(*light_text_color)
    pdf.cell(40, 7, "HQ Address:")
    pdf.set_text_color(*text_color)
    # Multicell address to handle overflow
    pdf.multi_cell(0, 7, clean_text(data.get("address", "Not Available")))
    pdf.ln(4)
    
    # Executive Summary Box
    pdf.set_fill_color(249, 250, 251) # Light gray
    pdf.set_draw_color(243, 244, 246)
    
    # Draw background rectangle box for executive summary
    # FPDF2 allows multi_cell with border/fill
    pdf.set_text_color(*text_color)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(0, 8, "Executive Summary", fill=True, border="TLR", ln=1)
    pdf.set_font("Helvetica", "I", 9.5)
    summary_text = clean_text(data.get("companySummary", "No summary details generated."))
    pdf.multi_cell(0, 6, summary_text, fill=True, border="BLR")
    
    pdf.ln(10)
    
    # 2. Products & Services Section
    pdf.set_text_color(*primary_color)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "2. PRODUCTS & SERVICES", ln=1)
    pdf.ln(2)
    
    products = data.get("productsServices", [])
    if products:
        for prod in products:
            # Bullet point name
            pdf.set_text_color(*text_color)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, clean_text(f"- {prod.get('name', 'Not Available')}"), ln=1)
            
            # Description
            pdf.set_text_color(*light_text_color)
            pdf.set_font("Helvetica", "", 9.5)
            # Indented multicell
            pdf.set_x(20)
            pdf.multi_cell(0, 5, clean_text(prod.get("description", "")))
            pdf.ln(3)
    else:
        pdf.set_text_color(*light_text_color)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "No product details available.", ln=1)
        pdf.ln(5)
        
    pdf.ln(5)
    
    # 3. AI-Generated Pain Points
    pdf.set_text_color(*primary_color)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "3. AI-GENERATED PAIN POINTS", ln=1)
    pdf.ln(2)
    
    pain_points = data.get("painPoints", [])
    if pain_points:
        for point in pain_points:
            # Warning Bullet
            pdf.set_text_color(185, 28, 28) # Red-700
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, clean_text(f"[!] {point.get('title', 'Not Available')}"), ln=1)
            
            # Details
            pdf.set_text_color(*text_color)
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_x(20)
            pdf.multi_cell(0, 5, clean_text(point.get("description", "")))
            pdf.ln(3)
    else:
        pdf.set_text_color(*light_text_color)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "No pain points details generated.", ln=1)
        pdf.ln(5)
 
    pdf.ln(5)
    
    # 4. Competitor Analysis
    pdf.set_text_color(*primary_color)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "4. COMPETITOR ANALYSIS", ln=1)
    pdf.ln(2)
    
    competitors = data.get("competitors", [])
    if competitors:
        for comp in competitors:
            # Competitor name & Website link
            pdf.set_text_color(*text_color)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(50, 6, clean_text(comp.get("name", "")))
            
            comp_web = comp.get("website", "")
            pdf.set_text_color(*secondary_color)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 6, clean_text(comp_web), ln=1, link=comp_web if comp_web.startswith("http") else "")
            
            # Description
            if comp.get("description"):
                pdf.set_text_color(*light_text_color)
                pdf.set_font("Helvetica", "I", 9.5)
                pdf.set_x(20)
                pdf.multi_cell(0, 5, clean_text(comp.get("description", "")))
                pdf.ln(2)
            pdf.ln(2)
    else:
        pdf.set_text_color(*light_text_color)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "No competitor details found.", ln=1)
        pdf.ln(5)
 
    # Returns the binary buffer bytes of the PDF output
    return pdf.output()
