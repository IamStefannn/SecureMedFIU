import sqlite3
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
from cryptography.fernet import Fernet
import os
import io
from PIL import Image, ImageDraw, ImageFont

# Encryption setup
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "qIkBRr-hIef_oyohOmekF3N_lvAmNmo0xceLQqDO-AQ=")
cipher = Fernet(ENCRYPTION_KEY.encode())

def fetch_hipaa_violations(db_path='securemed.db'):
    """Fetch HIPAA violations (nurse violations only, not technical scanner issues)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get only nurse violations, not technical scanner findings
    cursor.execute("""
        SELECT id, type, severity, timestamp, details, recommendation, 
               hipaa_section, source, status, nurse_username
        FROM audit_results 
        WHERE source != 'scanner'
        ORDER BY timestamp DESC
    """)
    
    violations = []
    for row in cursor.fetchall():
        try:
            # Decrypt the details
            decrypted_details = cipher.decrypt(row[4].encode()).decode()
        except:
            decrypted_details = "Unable to decrypt details"
        
        violations.append({
            'id': row[0],
            'type': row[1],
            'severity': row[2],
            'timestamp': row[3],
            'details': decrypted_details,
            'recommendation': row[5] or "No recommendation available",
            'hipaa_section': row[6] or "N/A",
            'source': row[7],
            'status': row[8] or "Unresolved",
            'nurse_username': row[9] or "Unknown"
        })
    
    conn.close()
    return violations

def create_bar_chart(data_dict, title, width=400, height=250):
    """Create a bar chart image and return as ImageReader"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw title
    draw.text((width//2 - 50, 10), title, fill='black', font=title_font)
    
    # Chart area
    chart_x, chart_y = 50, 50
    chart_width, chart_height = width - 100, height - 100
    
    # Draw axes
    draw.line([(chart_x, chart_y + chart_height), (chart_x + chart_width, chart_y + chart_height)], fill='black', width=2)
    draw.line([(chart_x, chart_y), (chart_x, chart_y + chart_height)], fill='black', width=2)
    
    if not data_dict:
        draw.text((chart_x + 50, chart_y + 50), "No data", fill='gray', font=font)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return ImageReader(buf)
    
    # Calculate bar dimensions
    max_value = max(data_dict.values()) if data_dict.values() else 1
    num_bars = len(data_dict)
    bar_width = (chart_width // num_bars) - 20
    
    colors_list = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
    
    # Draw bars
    for i, (label, value) in enumerate(data_dict.items()):
        bar_height = (value / max_value) * chart_height if max_value > 0 else 0
        x_pos = chart_x + (i * (chart_width // num_bars)) + 10
        y_pos = chart_y + chart_height - bar_height
        
        # Draw bar
        color = colors_list[i % len(colors_list)]
        draw.rectangle(
            [(x_pos, y_pos), (x_pos + bar_width, chart_y + chart_height)],
            fill=color
        )
        
        # Draw value on top of bar
        draw.text((x_pos + bar_width//2 - 5, y_pos - 15), str(value), fill='black', font=font)
        
        # Draw label
        label_short = label[:8] if len(label) > 8 else label
        draw.text((x_pos, chart_y + chart_height + 5), label_short, fill='black', font=font)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ImageReader(buf)

def create_pie_chart(data_dict, title, width=300, height=300):
    """Create a pie chart image and return as ImageReader"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw title
    draw.text((width//2 - 50, 10), title, fill='black', font=title_font)
    
    if not data_dict or sum(data_dict.values()) == 0:
        draw.text((width//2 - 30, height//2), "No data", fill='gray', font=font)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return ImageReader(buf)
    
    # Pie chart parameters
    center_x, center_y = width // 2, height // 2 + 20
    radius = min(width, height) // 3
    
    colors_list = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6']
    total = sum(data_dict.values())
    start_angle = 0
    
    # Draw slices
    for i, (label, value) in enumerate(data_dict.items()):
        extent = (value / total) * 360
        color = colors_list[i % len(colors_list)]
        
        # Draw pie slice
        bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
        draw.pieslice(bbox, start=start_angle, end=start_angle + extent, fill=color)
        
        # Draw legend
        legend_y = 40 + (i * 20)
        draw.rectangle([(20, legend_y), (35, legend_y + 12)], fill=color)
        label_text = f"{label}: {value}"
        draw.text((40, legend_y), label_text, fill='black', font=font)
        
        start_angle += extent
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ImageReader(buf)

def generate_pdf_report(output_path="HIPAA_Violations_Report.pdf", violations=None):
    """Generate comprehensive HIPAA violations PDF report with charts"""
    if violations is None:
        violations = fetch_hipaa_violations()
    
    if not violations:
        print("âš ï¸  No HIPAA violations found.")
        return
    
    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = LETTER
    
    # ========== COVER PAGE ==========
    c.setFillColor(colors.HexColor('#667eea'))
    c.rect(0, height - 150, width, 150, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 80, "HIPAA VIOLATIONS REPORT")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 110, "SecureMed Healthcare System")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 200, f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, height - 230, "CONFIDENTIAL - INTERNAL USE ONLY")
    
    c.setFont("Helvetica", 11)
    c.drawString(100, height - 300, f"Total HIPAA Violations Detected: {len(violations)}")
    
    # Count statistics
    unresolved = sum(1 for v in violations if v['status'] == 'Unresolved')
    resolved = len(violations) - unresolved
    c.drawString(100, height - 320, f"Unresolved Violations: {unresolved}")
    c.drawString(100, height - 340, f"Resolved Violations: {resolved}")
    
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 50, "This report contains Protected Health Information (PHI) - Handle according to HIPAA guidelines")
    
    c.showPage()
    
    # ========== EXECUTIVE SUMMARY ==========
    c.setFont("Helvetica-Bold", 20)
    c.drawString(80, height - 60, "Executive Summary")
    
    c.setFont("Helvetica", 11)
    y = height - 100
    
    # Severity breakdown
    severity_counts = {}
    for v in violations:
        sev = v['severity']
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, "Violation Severity Breakdown:")
    y -= 20
    
    c.setFont("Helvetica", 11)
    for severity, count in sorted(severity_counts.items(), key=lambda x: x[1], reverse=True):
        c.drawString(100, y, f"{severity}: {count} violations")
        y -= 15
    
    y -= 20
    
    # HIPAA sections affected
    hipaa_sections = {}
    for v in violations:
        section = v['hipaa_section']
        hipaa_sections[section] = hipaa_sections.get(section, 0) + 1
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, "HIPAA Sections Affected:")
    y -= 20

    c.setFont("Helvetica", 10)
    for section, count in sorted(hipaa_sections.items(), key=lambda x: x[1], reverse=True):
        # Check if we need a new page
        if y < 100:
            c.showPage()
            c.setFont("Helvetica-Bold", 20)
            c.drawString(80, height - 60, "Executive Summary (continued)")
            y = height - 100
            c.setFont("Helvetica", 10)
        c.drawString(100, y, f"{section}: {count} violations")
        y -= 15
    
    c.showPage()
    
    # ========== CHARTS PAGE ==========
    c.setFont("Helvetica-Bold", 20)
    c.drawString(80, height - 60, "Violations Analysis")
    
    # Create and insert severity chart
    severity_chart = create_bar_chart(severity_counts, "Violations by Severity")
    c.drawImage(severity_chart, 80, height - 350, width=400, height=250)
    
    # Create and insert status pie chart
    status_counts = {'Unresolved': unresolved, 'Resolved': resolved}
    status_chart = create_pie_chart(status_counts, "Resolution Status")
    c.drawImage(status_chart, 150, height - 650, width=300, height=250)
    
    c.showPage()
    
    # ========== DETAILED VIOLATIONS ==========
    c.setFont("Helvetica-Bold", 18)
    c.drawString(80, height - 60, "Detailed Violation Records")
    
    y = height - 100
    
    for idx, v in enumerate(violations, 1):
        # Check if we need a new page
        if y < 200:
            c.showPage()
            c.setFont("Helvetica-Bold", 18)
            c.drawString(80, height - 60, "Detailed Violation Records (continued)")
            y = height - 100
        
        # Violation header
        c.setFont("Helvetica-Bold", 13)
        severity_color = {
            'Critical': colors.red,
            'High': colors.orange,
            'Medium': colors.yellow,
            'Low': colors.green
        }.get(v['severity'], colors.black)
        
        c.setFillColor(severity_color)
        c.drawString(80, y, f"Violation #{idx}: [{v['severity']}] {v['type']}")
        c.setFillColor(colors.black)
        y -= 20
        
        # Details
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y, f"Timestamp: ")
        c.setFont("Helvetica", 10)
        c.drawString(165, y, v['timestamp'])
        y -= 15
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y, f"User Involved: ")
        c.setFont("Helvetica", 10)
        c.drawString(180, y, v['nurse_username'])
        y -= 15
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y, f"HIPAA Section: ")
        c.setFont("Helvetica", 10)
        c.drawString(190, y, v['hipaa_section'])
        y -= 15
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y, f"Status: ")
        c.setFont("Helvetica", 10)
        status_color = colors.green if v['status'] == 'Resolved' else colors.red
        c.setFillColor(status_color)
        c.drawString(145, y, v['status'])
        c.setFillColor(colors.black)
        y -= 20
        
        # Violation details
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y, "What Happened:")
        y -= 15
        c.setFont("Helvetica", 9)
        
        # Word wrap details
        details_words = v['details'].split()
        line = ""
        for word in details_words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 9) < 430:
                line = test_line
            else:
                c.drawString(120, y, line.strip())
                y -= 12
                line = word + " "
        if line:
            c.drawString(120, y, line.strip())
            y -= 20
        
        # Remediation
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y, "How to Remediate:")
        y -= 15
        c.setFont("Helvetica", 9)
        
        # Word wrap recommendation
        rec_words = v['recommendation'].split()
        line = ""
        for word in rec_words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 9) < 430:
                line = test_line
            else:
                c.drawString(120, y, line.strip())
                y -= 12
                line = word + " "
        if line:
            c.drawString(120, y, line.strip())
            y -= 20
        
        # Separator
        c.line(80, y - 5, width - 80, y - 5)
        y -= 25
    
    c.showPage()
    
    # ========== HIPAA COMPLIANCE GUIDE ==========
    c.setFont("Helvetica-Bold", 18)
    c.drawString(80, height - 60, "HIPAA Compliance Requirements")
    
    y = height - 100
    c.setFont("Helvetica", 10)
    
    hipaa_info = {
        "164.308(a)(1)(ii)(A)": "Risk Analysis - Conduct accurate assessment of potential risks to ePHI",
        "164.308(a)(3)(ii)(B)": "Access Authorization - Implement procedures for granting access to ePHI",
        "164.308(a)(5)": "Security Awareness Training - Implement security awareness and training program",
        "164.312(a)(2)(iv)": "Encryption and Decryption - Implement mechanism to encrypt/decrypt ePHI",
        "164.312(b)": "Audit Controls - Implement hardware, software to record and examine access",
        "164.312(e)(1)": "Transmission Security - Implement technical security measures to guard ePHI"
    }
    
    for section, description in hipaa_info.items():
        if y < 150:
            c.showPage()
            c.setFont("Helvetica-Bold", 18)
            c.drawString(80, height - 60, "HIPAA Compliance Requirements (continued)")
            y = height - 100
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(80, y, section)
        y -= 15
        c.setFont("Helvetica", 9)
        
        # Word wrap
        words = description.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 9) < 450:
                line = test_line
            else:
                c.drawString(100, y, line.strip())
                y -= 12
                line = word + " "
        if line:
            c.drawString(100, y, line.strip())
            y -= 25
    
    c.showPage()
    
    # ========== RECOMMENDATIONS PAGE ==========
    c.setFont("Helvetica-Bold", 18)
    c.drawString(80, height - 60, "Immediate Action Items")
    
    y = height - 100
    c.setFont("Helvetica", 11)
    
    actions = [
        "1. Review all unresolved violations with department heads within 48 hours",
        "2. Implement mandatory HIPAA refresher training for all staff involved in violations",
        "3. Establish additional monitoring controls for high-risk access patterns",
        "4. Update access control policies to prevent unauthorized PHI disclosure",
        "5. Conduct weekly compliance audits for the next 30 days",
        "6. Review and update incident response procedures",
        "7. Implement data loss prevention (DLP) tools where applicable",
        "8. Schedule follow-up compliance assessment in 60 days"
    ]
    
    for action in actions:
        c.drawString(80, y, action)
        y -= 20
    
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, y, "Contact Information:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(80, y, "For questions regarding this report, contact:")
    y -= 15
    c.drawString(80, y, "Compliance Officer: compliance@securemed.internal")
    y -= 15
    c.drawString(80, y, "Security Team: security@securemed.internal")
    
    c.save()
    print(f"âœ… HIPAA Violations Report generated: {output_path}")

if __name__ == "__main__":
    print("Generating HIPAA Violations Report...")
    violations = fetch_hipaa_violations()
    generate_pdf_report(violations=violations)
    print("\nâœ… Report generation complete!")