import os
import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging

logger = logging.getLogger(__name__)

# Blue theme palette
COLOR_PRIMARY = colors.HexColor("#1E3A8A")   # Navy
COLOR_SECONDARY = colors.HexColor("#3B82F6") # Vibrant Blue
COLOR_ACCENT = colors.HexColor("#DBEAFE")    # Light Blue Accent
COLOR_DARK = colors.HexColor("#1F2937")      # Dark Grey
COLOR_LIGHT = colors.HexColor("#F9FAFB")     # Very Light Grey
COLOR_BORDER = colors.HexColor("#E5E7EB")    # Border Grey
COLOR_GREEN = colors.HexColor("#10B981")     # Success Green

def generate_pdf_report(parsed_data: dict, ats_results: dict, jd_results: dict = None) -> bytes:
    """
    Generates a professional, print-ready PDF analysis report using ReportLab.
    
    Args:
        parsed_data (dict): Parsed resume data.
        ats_results (dict): Computed ATS results.
        jd_results (dict, optional): Job description match details.
        
    Returns:
        bytes: The compiled PDF as a byte string.
    """
    # Create an in-memory buffer
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.white,
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=COLOR_DARK,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=COLOR_PRIMARY
    )
    
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=COLOR_DARK
    )
    
    score_style = ParagraphStyle(
        'ScoreStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=30,
        textColor=COLOR_PRIMARY,
        alignment=1 # Centered
    )
    
    story = []
    
    # --- HEADER BLOCK (Navy Banner) ---
    banner_data = [
        [Paragraph("RESUME ANALYSIS REPORT", title_style)],
        [Paragraph(f"Generated on {datetime.date.today().strftime('%B %d, %Y')} | Powered by AI Analyzer", ParagraphStyle('Sub', parent=title_style, fontSize=10, textColor=COLOR_ACCENT))]
    ]
    banner_table = Table(banner_data, colWidths=[doc.width])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY),
        ('PADDING', (0,0), (-1,-1), 18),
        ('BOTTOMPADDING', (0,1), (-1,1), 12),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))
    
    # --- CANDIDATE INFO SECTION ---
    info_data = [
        [
            Paragraph("Candidate Name:", meta_label), Paragraph(parsed_data.get("name", "Unknown"), meta_val),
            Paragraph("Email Address:", meta_label), Paragraph(parsed_data.get("email", "Not Found"), meta_val)
        ],
        [
            Paragraph("Phone Number:", meta_label), Paragraph(parsed_data.get("phone", "Not Found"), meta_val),
            Paragraph("LinkedIn Profile:", meta_label), Paragraph(parsed_data.get("linkedin", "Not Found") or "Not Found", meta_val)
        ],
        [
            Paragraph("GitHub Profile:", meta_label), Paragraph(parsed_data.get("github", "Not Found") or "Not Found", meta_val),
            Paragraph("File Checked:", meta_label), Paragraph(parsed_data.get("filename", "N/A"), meta_val)
        ]
    ]
    info_table = Table(info_data, colWidths=[110, 150, 110, doc.width - 370])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # --- ATS SCORE BOX ---
    score = ats_results.get("total_score", 0)
    
    # Define a custom progress bar using Table blocks
    filled_bars = int(round(score / 10))
    bar_cells = []
    for i in range(10):
        if i < filled_bars:
            bar_cells.append(("", COLOR_SECONDARY))
        else:
            bar_cells.append(("", colors.white))
            
    bar_table_data = [[cell[0] for cell in bar_cells]]
    bar_table = Table(bar_table_data, colWidths=[20]*10, rowHeights=[12])
    
    t_style = [
        ('BOX', (0,0), (-1,-1), 1, COLOR_PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]
    for idx, cell in enumerate(bar_cells):
        t_style.append(('BACKGROUND', (idx, 0), (idx, 0), cell[1]))
    bar_table.setStyle(TableStyle(t_style))
    
    score_box_data = [
        [
            Paragraph(f"<b>{score}</b><font size=12>/100</font><br/><font size=8>ATS SCORE</font>", score_style),
            [
                Paragraph("<b>ATS Optimization Summary</b>", ParagraphStyle('H', parent=body_style, fontName='Helvetica-Bold', fontSize=11, textColor=COLOR_PRIMARY)),
                Spacer(1, 4),
                Paragraph("This score reflects the overall formatting, section coverage, keyword density, and action verbs detected in your resume. Check recommendations to boost your rating.", ParagraphStyle('D', parent=body_style, fontSize=9, leading=12)),
                Spacer(1, 4),
                bar_table
            ]
        ]
    ]
    
    score_box_table = Table(score_box_data, colWidths=[140, doc.width - 140])
    score_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_ACCENT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_SECONDARY),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
    ]))
    story.append(score_box_table)
    story.append(Spacer(1, 15))
    
    # --- EXECUTIVE SUMMARY ---
    # We will generate summary on the fly if not provided, or extract it
    from utils.summary import generate_summary
    resume_summary_text = generate_summary(parsed_data.get("raw_text", ""), parsed_data.get("skills", {}))
    
    story.append(Paragraph("Executive Summary", section_heading))
    story.append(Paragraph(resume_summary_text, body_style))
    story.append(Spacer(1, 10))
    
    # --- SKILLS INVENTORY ---
    story.append(Paragraph("Extracted Key Skills Profile", section_heading))
    skills = parsed_data.get("skills", {})
    skills_table_data = []
    
    for category, skill_list in skills.items():
        if skill_list:
            skills_table_data.append([
                Paragraph(f"<b>{category}</b>", meta_label),
                Paragraph(", ".join(skill_list), body_style)
            ])
            
    if not skills_table_data:
        skills_table_data.append([Paragraph("Skills", meta_label), Paragraph("No specific skills identified.", body_style)])
        
    skills_table = Table(skills_table_data, colWidths=[140, doc.width - 140])
    skills_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 15))
    
    # --- JOB DESCRIPTION MATCHING (If JD exists) ---
    if jd_results and jd_results.get("match_percentage", 0) > 0:
        jd_score = jd_results["match_percentage"]
        matched_sk = jd_results.get("matched_skills", [])
        missing_sk = jd_results.get("missing_skills", [])
        
        story.append(Paragraph("Job Description Matching Analysis", section_heading))
        
        # Color match score based on compatibility
        match_color = COLOR_GREEN if jd_score >= 70 else COLOR_SECONDARY
        jd_match_style = ParagraphStyle(
            'JDMatchStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=match_color
        )
        
        jd_match_intro = f"<b>Match Percentage:</b> <font color='{match_color.hexval()}'>{jd_score}%</font>"
        story.append(Paragraph(jd_match_intro, jd_match_style))
        story.append(Spacer(1, 6))
        
        jd_data = []
        if matched_sk:
            jd_data.append([Paragraph("<b>Matched Skills:</b>", meta_label), Paragraph(", ".join(matched_sk), body_style)])
        if missing_sk:
            jd_data.append([Paragraph("<b>Missing Skills (Recommended):</b>", ParagraphStyle('M', parent=meta_label, textColor=colors.HexColor("#B91C1C"))), Paragraph(", ".join(missing_sk), body_style)])
            
        if jd_data:
            jd_table = Table(jd_data, colWidths=[140, doc.width - 140])
            jd_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 5),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ]))
            story.append(jd_table)
            story.append(Spacer(1, 15))
            
    # --- RECOMMENDATIONS ---
    story.append(Paragraph("Actionable Recommendations for Improvement", section_heading))
    from utils.recommendations import generate_recommendations
    recs = generate_recommendations(parsed_data, ats_results, jd_results)
    
    # Add formatting suggestions
    if recs["formatting"]:
        story.append(Paragraph("<b>Resume Formatting & Layout</b>", ParagraphStyle('SubH', parent=body_style, fontName='Helvetica-Bold', textColor=COLOR_PRIMARY)))
        for rec in recs["formatting"][:3]:
            story.append(Paragraph(f"• {rec}", bullet_style))
        story.append(Spacer(1, 4))
        
    # Add content suggestions
    if recs["content_strength"]:
        story.append(Paragraph("<b>Content Strength & Bullet Points</b>", ParagraphStyle('SubH', parent=body_style, fontName='Helvetica-Bold', textColor=COLOR_PRIMARY)))
        for rec in recs["content_strength"][:3]:
            story.append(Paragraph(f"• {rec}", bullet_style))
        story.append(Spacer(1, 4))
        
    # Add skill additions
    if recs["skills_certs"]:
        story.append(Paragraph("<b>Skills & Professional Certifications</b>", ParagraphStyle('SubH', parent=body_style, fontName='Helvetica-Bold', textColor=COLOR_PRIMARY)))
        for rec in recs["skills_certs"][:3]:
            story.append(Paragraph(f"• {rec}", bullet_style))
        story.append(Spacer(1, 4))
        
    # Add general ATS hacks
    story.append(Paragraph("<b>General ATS Core Optimization</b>", ParagraphStyle('SubH', parent=body_style, fontName='Helvetica-Bold', textColor=COLOR_PRIMARY)))
    for rec in recs["ats_hacks"][:3]:
        story.append(Paragraph(f"• {rec}", bullet_style))
        
    # Build Document
    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()
    except Exception as e:
        logger.error(f"ReportLab compilation error: {str(e)}")
        raise RuntimeError(f"Could not build PDF: {str(e)}")
    finally:
        buffer.close()
        
    return pdf_bytes
