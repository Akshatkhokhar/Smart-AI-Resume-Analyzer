from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import io

class ResumeGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='NameHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceBefore=10,
            spaceAfter=5,
            borderPadding=2,
            borderWidth=0,
            borderColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.black,
            spaceBefore=5,
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyDate',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_LEFT,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='Description',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=5
        ))

        self.styles.add(ParagraphStyle(
            name='SkillItem',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            bulletIndent=10,
            leftIndent=20
        ))

    def generate(self, data):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        story = []

        # Header
        if data.get('fullName'):
            story.append(Paragraph(data['fullName'], self.styles['NameHeader']))
        
        # Contact Info
        contact_parts = []
        if data.get('email'): contact_parts.append(data['email'])
        if data.get('phone'): contact_parts.append(data['phone'])
        if data.get('linkedin'): contact_parts.append(f"LinkedIn: {data['linkedin']}")
        if data.get('location'): contact_parts.append(data['location'])
        
        if contact_parts:
            story.append(Paragraph(" | ".join(contact_parts), self.styles['ContactInfo']))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
            story.append(Spacer(1, 0.2*inch))

        # Professional Summary
        if data.get('summary'):
            story.append(Paragraph("Professional Summary", self.styles['SectionHeader']))
            story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey))
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(data['summary'], self.styles['Description']))
            story.append(Spacer(1, 0.2*inch))

        # Experience
        if data.get('experience') and len(data['experience']) > 0:
            story.append(Paragraph("Experience", self.styles['SectionHeader']))
            story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey))
            story.append(Spacer(1, 0.1*inch))
            
            for exp in data['experience']:
                # Title and Date row
                title = exp.get('title', '')
                company = exp.get('company', '')
                date_range = f"{exp.get('startDate', '')} - {exp.get('endDate', 'Present')}"
                
                # Using a table for layout of title/company and date
                header_data = [
                    [Paragraph(f"<b>{title}</b>", self.styles['Normal']), Paragraph(f"<b>{date_range}</b>", ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT))]
                ]
                t = Table(header_data, colWidths=[4.5*inch, 2.5*inch])
                t.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ]))
                story.append(t)
                
                if company:
                    story.append(Paragraph(company, self.styles['CompanyDate']))
                
                if exp.get('description'):
                    # Handle bullet points if present in text, otherwise just paragraph
                    desc = exp['description']
                    for line in desc.split('\n'):
                        if line.strip():
                            story.append(Paragraph(line, self.styles['Description']))
                
                story.append(Spacer(1, 0.15*inch))
            
            story.append(Spacer(1, 0.1*inch))

        # Education
        if data.get('education') and len(data['education']) > 0:
            story.append(Paragraph("Education", self.styles['SectionHeader']))
            story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey))
            story.append(Spacer(1, 0.1*inch))
            
            for edu in data['education']:
                school = edu.get('school', '')
                degree = edu.get('degree', '')
                year = edu.get('year', '')
                
                header_data = [
                    [Paragraph(f"<b>{school}</b>", self.styles['Normal']), Paragraph(f"<b>{year}</b>", ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT))]
                ]
                t = Table(header_data, colWidths=[5.5*inch, 1.5*inch])
                t.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ]))
                story.append(t)
                
                if degree:
                    story.append(Paragraph(degree, self.styles['CompanyDate']))
                
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.1*inch))

        # Skills
        if data.get('skills'):
            story.append(Paragraph("Skills", self.styles['SectionHeader']))
            story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey))
            story.append(Spacer(1, 0.1*inch))
            
            # Check if skills is a string (comma separated) or list
            skills_text = ""
            if isinstance(data['skills'], list):
                skills_text = ", ".join(data['skills'])
            else:
                skills_text = data['skills']
                
            story.append(Paragraph(skills_text, self.styles['Description']))
            story.append(Spacer(1, 0.2*inch))

        # Projects
        if data.get('projects') and len(data['projects']) > 0:
            story.append(Paragraph("Projects", self.styles['SectionHeader']))
            story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey))
            story.append(Spacer(1, 0.1*inch))
            
            for proj in data['projects']:
                name = proj.get('name', '')
                desc = proj.get('description', '')
                
                if name:
                    story.append(Paragraph(f"<b>{name}</b>", self.styles['Normal']))
                if desc:
                    story.append(Paragraph(desc, self.styles['Description']))
                
                story.append(Spacer(1, 0.1*inch))

        doc.build(story)
        buffer.seek(0)
        return buffer
