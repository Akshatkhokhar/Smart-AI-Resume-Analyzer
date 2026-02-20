import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import tempfile
import requests
import json
import math
import re


class AIResumeAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configure Google Gemini AI
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF using pdfplumber and OCR if needed"""
        text = ""
        
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            if hasattr(pdf_file, 'getbuffer'):
                temp_file.write(pdf_file.getbuffer())
            elif hasattr(pdf_file, 'read'):
                temp_file.write(pdf_file.read())
                pdf_file.seek(0)  # Reset file pointer
            else:
                # If it's already bytes
                temp_file.write(pdf_file)
            temp_path = temp_file.name
        
        try:
            # Try direct text extraction with pdfplumber
            try:
                with pdfplumber.open(temp_path) as pdf:
                    for page in pdf.pages:
                        try:
                            # Suppress specific warnings about PDFColorSpace conversion
                            import warnings
                            with warnings.catch_warnings():
                                warnings.filterwarnings("ignore", message=".*PDFColorSpace.*")
                                warnings.filterwarnings("ignore", message=".*Cannot convert.*")
                                page_text = page.extract_text()
                                if page_text:
                                    text += page_text + "\n"
                        except Exception as e:
                            # Don't show these specific errors to the user
                            if "PDFColorSpace" not in str(e) and "Cannot convert" not in str(e):
                                st.warning(f"Error extracting text from page with pdfplumber: {e}")
            except Exception as e:
                st.warning(f"pdfplumber extraction failed: {e}")
            
            # If pdfplumber extraction worked, return the text
            if text.strip():
                os.unlink(temp_path)  # Clean up the temp file
                return text.strip()
            
            # Try PyPDF2 as a fallback
            st.info("Trying PyPDF2 extraction method...")
            try:
                import pypdf
                pdf_text = ""
                with open(temp_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += page_text + "\n"
                
                if pdf_text.strip():
                    os.unlink(temp_path)  # Clean up the temp file
                    return pdf_text.strip()
            except Exception as e:
                st.warning(f"PyPDF2 extraction failed: {e}")
            
            # If we got here, both extraction methods failed
            st.warning("Standard text extraction methods failed. Your PDF might be image-based or scanned.")
            
            # Try OCR as a last resort
            try:
                # Check if we can import the required OCR libraries
                import pytesseract
                from pdf2image import convert_from_path
                
                st.info("Attempting OCR for image-based PDF. This may take a moment...")
                
                # Check if poppler is installed
                poppler_path = None
                if os.name == 'nt':  # Windows
                    # Try to find poppler in common locations
                    possible_paths = [
                        r'C:\poppler\Library\bin',
                        r'C:\Program Files\poppler\bin',
                        r'C:\Program Files (x86)\poppler\bin',
                        r'C:\poppler\bin'
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            poppler_path = path
                            st.success(f"Found Poppler at: {path}")
                            break
                    
                    if not poppler_path:
                        st.warning("Poppler not found in common locations. Using default path: C:\\poppler\\Library\\bin")
                        poppler_path = r'C:\poppler\Library\bin'
                
                # Try to convert PDF to images
                try:
                    if poppler_path and os.name == 'nt':
                        images = convert_from_path(temp_path, poppler_path=poppler_path)
                    else:
                        images = convert_from_path(temp_path)
                    
                    # Process each image with OCR
                    ocr_text = ""
                    for i, image in enumerate(images):
                        st.info(f"Processing page {i+1} with OCR...")
                        page_text = pytesseract.image_to_string(image)
                        ocr_text += page_text + "\n"
                    
                    if ocr_text.strip():
                        os.unlink(temp_path)  # Clean up the temp file
                        return ocr_text.strip()
                    else:
                        st.error("OCR extraction yielded no text. Please check if the PDF contains actual text content.")
                except Exception as e:
                    st.error(f"PDF to image conversion failed: {e}")
                    st.info("If you're on Windows, make sure Poppler is installed and in your PATH.")
                    st.info("Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/")
            except ImportError as e:
                st.error(f"OCR libraries not available: {e}")
                st.info("Please install the required OCR libraries:")
                st.code("pip install pytesseract pdf2image")
                st.info("For Windows, also download and install:")
                st.info("1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
                st.info("2. Poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
            except Exception as e:
                st.error(f"OCR processing failed: {e}")
        
        except Exception as e:
            st.error(f"PDF processing failed: {e}")
        
        # Clean up the temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        # If all extraction methods failed, return an empty string
        st.error("All text extraction methods failed. Please try a different PDF or manually extract the text.")
        return ""
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX file"""
        from docx import Document
        
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(docx_file.getbuffer())
            temp_path = temp_file.name
        
        text = ""
        try:
            doc = Document(temp_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            st.error(f"Error extracting text from DOCX: {e}")
        
        os.unlink(temp_path)  # Clean up the temp file
        return text
    
    def analyze_resume_with_gemini(self, resume_text, job_description=None, job_role=None):
        """Analyze resume using Google Gemini AI"""
        if not resume_text:
            return {"error": "Resume text is required for analysis."}
        
        if not self.google_api_key:
            return {"error": "Google API key is not configured. Please add it to your .env file."}
        
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            base_prompt = f"""
            You are an expert resume analyst and career coach.
            Your task is to analyze the resume content AND its structure/formatting to provide a structured JSON response.
            
            IMPORTANT: 
            1. Return ONLY valid JSON.
            2. Evaluate strictly. Do NOT give high scores to poorly formatted resumes even if they have keywords.
            3. A resume with poor formatting (e.g., long paragraphs, no bullet points, typos, lack of sections) should NOT score above 60, regardless of content match.
            4. Detect typos (e.g. "Micro-soft") and penalize accordingly.

            Structure the JSON exactly like this:
            {{
                "candidate_info": {{
                    "name": "Extracted Name",
                    "role": "Detected Role",
                    "experience": "Total Experience (e.g. 2 years)",
                    "education": "Highest Degree"
                }},
                "match_score": 0-100 (integer, penalize for poor format),
                "match_status": "Excellent/Good/Moderate/Poor",
                "formatting_score": 0-100 (integer),
                "formatting_issues": ["Issue 1", "Issue 2"],
                "matched_skills": ["Skill1", "Skill2", ...],
                "missing_skills": ["Skill1", "Skill2", ...],
                "job_context": {{
                    "title": "Job Title Used",
                    "requirements_summary": "Brief summary of key requirements"
                }},
                "recommendations": ["Recommendation 1", "Recommendation 2", ...],
                "overall_assessment": "Analysis summary including formatting critique (2-3 sentences)",
                "ats_score": 0-100 (integer),
                "ats_keywords_missing": ["Keyword1", "Keyword2"]
            }}

            Resume Text (Analyze structure from this text representation too):
            {resume_text}
            """
            
            if job_role:
                base_prompt += f"""
                
                Target Job Role: {job_role}
                """
            
            if job_description:
                base_prompt += f"""
                
                Job Description to compare against:
                {job_description}
                """
            
            # Generate content
            response = model.generate_content(base_prompt)
            data = response.text.strip()
            
            # Clean up potential markdown formatting from the response
            if data.startswith("```json"):
                data = data.replace("```json", "", 1)
            if data.startswith("```"):
                data = data.replace("```", "", 1)
            if data.endswith("```"):
                data = data.rsplit("```", 1)[0]
            
            data = data.strip()
            
            # Parse JSON
            try:
                analysis = json.loads(data)
                
                # Ensure all keys exist
                required_keys = ["match_score", "ats_score", "matched_skills", "missing_skills", "recommendations", "overall_assessment"]
                for key in required_keys:
                    if key not in analysis:
                        if key == "match_score" or key == "ats_score":
                            analysis[key] = 0
                        elif key == "matched_skills" or key == "missing_skills" or key == "recommendations":
                            analysis[key] = []
                        elif key == "overall_assessment":
                            analysis[key] = "Analysis failed to generate assessment."
                
                return {
                    "structured_data": analysis,
                    "resume_score": analysis.get("match_score", 0),
                    "ats_score": analysis.get("ats_score", 0),
                    # Keep raw analysis for backward compatibility if needed, but we should rely on structured_data
                    "analysis": json.dumps(analysis, indent=2) 
                }
                
            except json.JSONDecodeError as e:
                return {"error": f"Failed to parse AI response as JSON: {str(e)}. Response was: {data[:100]}..."}
        
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    
    def generate_pdf_report(self, analysis_result, candidate_name, job_role):
        """Generate a PDF report of the analysis using structured data"""
        try:
            # Import required libraries
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable, KeepTogether, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
            import io
            import datetime
            import math
            
            # Helper function to clean markdown formatting
            def clean_text(text):
                if not text: return ""
                return str(text).replace("**", "").replace("*", "").replace("##", "").strip()

            if not analysis_result:
                st.error("No analysis result provided for PDF generation")
                return None
                
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                   leftMargin=0.5*inch, rightMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.darkblue, spaceAfter=20, alignment=1)
            heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=16, textColor=colors.white, backColor=colors.darkblue, borderPadding=8, borderRadius=4, spaceAfter=12, alignment=1)
            subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=13, textColor=colors.darkblue, spaceAfter=8)
            normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=14)
            list_style = ParagraphStyle('ListItem', parent=normal_style, leftIndent=20, firstLineIndent=-10)

            # --- Gauge Chart Class ---
            class GaugeChart(Drawing):
                def __init__(self, width, height, score, label="Match Score"):
                    Drawing.__init__(self, width, height)
                    self.width = width
                    self.height = height
                    self.score = int(score) if score else 0
                    self.label = label
                    
                    if self.score >= 80: color = colors.green; status = "Excellent"
                    elif self.score >= 60: color = colors.orange; status = "Good"
                    elif self.score >= 40: color = colors.orange; status = "Moderate"
                    else: color = colors.red; status = "Poor"
                    
                    # Draw
                    cx, cy = width/2, height/2 - 10
                    bg_radius = min(cx, cy) - 10
                    
                    # Background Arc (Grey)
                    for i in range(0, 101, 2):
                        angle = math.radians(180 - (i * 1.8))
                        x1 = cx + (bg_radius - 5) * math.cos(angle)
                        y1 = cy + (bg_radius - 5) * math.sin(angle)
                        x2 = cx + (bg_radius + 5) * math.cos(angle)
                        y2 = cy + (bg_radius + 5) * math.sin(angle)
                        self.add(Line(x1, y1, x2, y2, strokeColor=colors.lightgrey, strokeWidth=2))

                    # Score Arc (Colored)
                    score_steps = int(self.score)
                    for i in range(0, score_steps + 1, 2):
                        angle = math.radians(180 - (i * 1.8))
                        x1 = cx + (bg_radius - 5) * math.cos(angle)
                        y1 = cy + (bg_radius - 5) * math.sin(angle)
                        x2 = cx + (bg_radius + 5) * math.cos(angle)
                        y2 = cy + (bg_radius + 5) * math.sin(angle)
                        self.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=3))

                    # Text
                    self.add(String(cx, cy - 20, f"{self.score}%", fontSize=28, fillColor=color, textAnchor='middle', fontName='Helvetica-Bold'))
                    self.add(String(cx, cy - 40, status, fontSize=12, fillColor=colors.black, textAnchor='middle'))
                    self.add(String(cx, 10, self.label, fontSize=14, fillColor=colors.darkblue, textAnchor='middle', fontName='Helvetica-Bold'))
            
            # --- Build Content ---
            content = []
            
            # 1. Header
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            content.append(Paragraph("Resume Analysis Report", title_style))
            content.append(Paragraph(f"Generated on {current_date}", normal_style))
            content.append(Spacer(1, 0.2*inch))
            
            # 2. Candidate Info & Resume Summary (Extracted Info)
            # Try to get structured candidate info, otherwise fallback
            structured_data = analysis_result.get("structured_data", {})
            candidate_info = structured_data.get("candidate_info", {})
            
            c_name = candidate_info.get("name", candidate_name)
            c_role = candidate_info.get("role", "Not Detected")
            c_exp = candidate_info.get("experience", "Not Detected")
            c_edu = candidate_info.get("education", "Not Detected")
            
            info_data = [
                ["Candidate Name:", c_name, "Detected Role:", c_role],
                ["Target Job Role:", job_role, "Experience:", c_exp],
                ["Analysis Model:", analysis_result.get("model_used", "AI"), "Education:", c_edu]
            ]
            
            info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2.5*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            content.append(info_table)
            content.append(Spacer(1, 0.3*inch))
            
            # 3. Match Score (Gauge)
            resume_score = analysis_result.get("score", 0)
            content.append(Paragraph("Overall Match Score", heading_style))
            content.append(GaugeChart(width=400, height=200, score=resume_score))
            content.append(Spacer(1, 0.2*inch))
            
            # 4. Overall Assessment
            assessment = analysis_result.get("overall_assessment", "")
            if not assessment and "full_response" in analysis_result:
                 # Fallback extraction if structured data is missing
                 text = analysis_result["full_response"]
                 if "## Overall Assessment" in text:
                     assessment = text.split("## Overall Assessment")[1].split("##")[0].strip()
            
            if assessment:
                content.append(Paragraph("Executive Summary", subheading_style))
                content.append(Paragraph(clean_text(assessment), normal_style))
                content.append(Spacer(1, 0.2*inch))
            
            # 5. Skills Analysis (Matched vs Missing) - SKILL GAP
            matched_skills = analysis_result.get("matched_skills", [])
            missing_skills = analysis_result.get("missing_skills", [])
            
            # Fallback to older keys if new ones empty
            if not matched_skills: matched_skills = analysis_result.get("strengths", [])
            if not missing_skills: missing_skills = analysis_result.get("weaknesses", []) # Approximate mapping
            
            if matched_skills or missing_skills:
                content.append(Paragraph("Skill Gap Analysis", heading_style))
                
                # Format into paragraphs
                matched_paras = [Paragraph(f"• {clean_text(s)}", list_style) for s in matched_skills]
                missing_paras = [Paragraph(f"• {clean_text(s)}", list_style) for s in missing_skills]
                
                # Balance length
                max_len = max(len(matched_paras), len(missing_paras))
                matched_paras += [Paragraph("", normal_style)] * (max_len - len(matched_paras))
                missing_paras += [Paragraph("", normal_style)] * (max_len - len(missing_paras))
                
                data = [["Matched Skills (Strengths)", "Missing Skills (Gap)"]]
                for i in range(max_len):
                    data.append([matched_paras[i], missing_paras[i]])
                
                skill_table = Table(data, colWidths=[3.5*inch, 3.5*inch])
                skill_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (0,0), colors.lightgreen), # Header Matched
                    ('BACKGROUND', (1,0), (1,0), colors.salmon),     # Header Missing
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                content.append(skill_table)
                content.append(Spacer(1, 0.3*inch))
            
            # 6. Job Context
            job_context = structured_data.get("job_context", {})
            if job_context and job_context.get("requirements_summary"):
                content.append(Paragraph("Job Role Context", subheading_style))
                content.append(Paragraph(f"<b>Title:</b> {job_context.get('title', 'N/A')}", normal_style))
                content.append(Paragraph(f"<b>Requirements Summary:</b> {clean_text(job_context.get('requirements_summary'))}", normal_style))
                content.append(Spacer(1, 0.2*inch))

            # 7. Formatting & Structure Analysis (New Section)
            formatting_score = structured_data.get("formatting_score", 0)
            formatting_issues = structured_data.get("formatting_issues", [])
            
            if formatting_score > 0 or formatting_issues:
                content.append(Paragraph("Formatting & Structure", heading_style))
                
                # Score
                f_color = colors.green if formatting_score >= 80 else (colors.orange if formatting_score >= 60 else colors.red)
                content.append(Paragraph(f"<b>Formatting Score:</b> <font color={f_color}>{formatting_score}/100</font>", normal_style))
                
                # Issues
                if formatting_issues:
                    content.append(Spacer(1, 0.05*inch))
                    content.append(Paragraph("<b>Identified Issues:</b>", normal_style))
                    for issue in formatting_issues:
                        content.append(Paragraph(f"• {clean_text(issue)}", list_style))
                else:
                     content.append(Paragraph("• No major formatting issues detected.", list_style))
                
                content.append(Spacer(1, 0.2*inch))

            # 7. Recommendations
            recommendations = analysis_result.get("suggestions", [])
            if recommendations:
                content.append(Paragraph("Recommended Learning Path", heading_style))
                for rec in recommendations:
                    content.append(Paragraph(f"• {clean_text(rec)}", list_style))
                content.append(Spacer(1, 0.2*inch))
                
            # 8. ATS Score (Mini section)
            ats_score = analysis_result.get("ats_score", 0)
            ats_missing = structured_data.get("ats_keywords_missing", [])
            
            content.append(Paragraph("ATS Optimization", heading_style))
            content.append(Paragraph(f"<b>ATS Score:</b> {ats_score}/100", normal_style))
            if ats_missing:
                content.append(Paragraph("<b>Missing Keywords:</b> " + ", ".join([clean_text(k) for k in ats_missing]), normal_style))

            # Build
            doc.build(content, onFirstPage=self.add_page_number, onLaterPages=self.add_page_number)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            import traceback
            st.error(f"Error generating PDF: {str(e)}")
            print(traceback.format_exc())
            return None

            
    def extract_skills_from_analysis(self, analysis_text):
        """Extract skills from the analysis text"""
        skills = []
        
        try:
            # Check for "Key Skills" (new format) or "Current Skills" (old format)
            if "Key Skills" in analysis_text:
                skills_section = analysis_text.split("Key Skills")[1]
            elif "Current Skills" in analysis_text:
                skills_section = analysis_text.split("Current Skills")[1]
            else:
                return skills

            if "##" in skills_section:
                skills_section = skills_section.split("##")[0]
            
            # Stop at "Missing Skills" if present
            if "Missing Skills" in skills_section:
                skills_section = skills_section.split("Missing Skills")[0]
            
            for line in skills_section.split("\n"):
                if line.strip() and ("-" in line or "*" in line or "•" in line):
                    skill = line.replace("-", "").replace("*", "").replace("•", "").strip()
                    # Remove markdown bold if present
                    skill = skill.replace("**", "").replace("__", "")
                    if skill:
                        skills.append(skill)
        except Exception as e:
            pass # Silently fail
        
        return skills
        
    def extract_missing_skills_from_analysis(self, analysis_text):
        """Extract missing skills from the analysis text"""
        missing_skills = []
        
        try:
            if "Missing Skills" in analysis_text:
                missing_section = analysis_text.split("Missing Skills")[1]
                if "##" in missing_section:
                    missing_section = missing_section.split("##")[0]
                
                for line in missing_section.split("\n"):
                    if line.strip() and ("-" in line or "*" in line or "•" in line):
                        skill = line.replace("-", "").replace("*", "").replace("•", "").strip()
                        # Remove markdown bold if present
                        skill = skill.replace("**", "").replace("__", "")
                        if skill:
                            missing_skills.append(skill)
        except Exception as e:
            pass
        
        return missing_skills
    
    def _extract_score_from_text(self, analysis_text):
        """Extract the resume score from the analysis text"""
        try:
            # Look for the Resume Score section
            if "## Resume Score" in analysis_text:
                score_section = analysis_text.split("## Resume Score")[1].strip()
                # Extract the first number found
                score_match = re.search(r'Resume Score:\s*(\d{1,3})', score_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
            
            # If no score found in Resume Score section, try to find it elsewhere
            score_match = re.search(r'Resume Score:\s*(\d{1,3})', analysis_text)
            if score_match:
                score = int(score_match.group(1))
                return max(0, min(score, 100))
                
            return 0
        except Exception as e:
            return 0
            
    def _extract_ats_score_from_text(self, analysis_text):
        """Extract the ATS score from the analysis text"""
        try:
            # Look for the ATS Score in the ATS Optimization section
            if "## ATS Optimization" in analysis_text:
                ats_section = analysis_text.split("## ATS Optimization")[1].split("##")[0].strip()
                # Extract the score using regex
                score_match = re.search(r'ATS Score:\s*(\d{1,3})', ats_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
            return 0
        except Exception as e:
            print(f"Error extracting ATS score: {str(e)}")
            return 0
            
    def analyze_resume(self, resume_text, job_role=None, role_info=None, model="Google Gemini"):
        """
        Analyze a resume using the specified AI model
        
        Parameters:
        - resume_text: The text content of the resume
        - job_role: The target job role
        - role_info: Additional information about the job role
        - model: The AI model to use ("Google Gemini" or "Anthropic Claude")
        
        Returns:
        - Dictionary containing analysis results
        """
        import traceback
        
        try:
            job_description = None
            if role_info:
                job_description = f"""
                Role: {job_role}
                Description: {role_info.get('description', '')}
                Required Skills: {', '.join(role_info.get('required_skills', []))}
                """
            
            # Choose the appropriate model for analysis
            if model == "Google Gemini":
                result = self.analyze_resume_with_gemini(resume_text, job_description, job_role)
                model_used = "Google Gemini"
            elif model == "Anthropic Claude":
                # Assuming this might still return text-based result, or not implemented
                # For safety, if it returns text, we might need the old parsing logic or just fail gracefully 
                # for now, as we are focusing on Gemini
                result = self.analyze_resume_with_anthropic(resume_text, job_description, job_role)
                model_used = result.get("model_used", "Anthropic Claude")
            else:
                result = self.analyze_resume_with_gemini(resume_text, job_description, job_role)
                model_used = "Google Gemini"
            
            # Process the result
            # If we have structured data (from new Gemini implementation), use it directly
            if "structured_data" in result:
                data = result["structured_data"]
                return {
                    "score": data.get("match_score", 0),
                    "ats_score": data.get("ats_score", 0),
                    "strengths": data.get("matched_skills", []), # Mapping matched skills to strengths for now, or use actual recommendations
                    "weaknesses": data.get("missing_skills", []), # Mapping missing skills to weaknesses
                    "suggestions": data.get("recommendations", []),
                    "candidate_info": data.get("candidate_info", {}),
                    "matched_skills": data.get("matched_skills", []),
                    "missing_skills": data.get("missing_skills", []),
                    "job_context": data.get("job_context", {}),
                    "overall_assessment": data.get("overall_assessment", ""),
                    "full_response": result.get("analysis", ""), # Start keeping raw JSON string as full_response
                    "structured_data": data, # Pass full object
                    "model_used": model_used
                }

            # Fallback for text-based results (e.g. old Claude implementation or error)
            analysis_text = result.get("analysis", "")
            
            # Extract strengths
            strengths = []
            if "## Key Strengths" in analysis_text:
                strengths_section = analysis_text.split("## Key Strengths")[1].split("##")[0].strip()
                strengths = [clean_markdown(s.strip().replace("- ", "").replace("* ", "").replace("• ", "")) 
                            for s in strengths_section.split("\n") 
                            if s.strip() and (s.strip().startswith("-") or s.strip().startswith("*") or s.strip().startswith("•"))]
            
            # Extract weaknesses/areas for improvement
            weaknesses = []
            if "## Areas for Improvement" in analysis_text:
                weaknesses_section = analysis_text.split("## Areas for Improvement")[1].split("##")[0].strip()
                weaknesses = [clean_markdown(w.strip().replace("- ", "").replace("* ", "").replace("• ", "")) 
                             for w in weaknesses_section.split("\n") 
                             if w.strip() and (w.strip().startswith("-") or w.strip().startswith("*") or w.strip().startswith("•"))]
            
            # Extract suggestions/recommendations
            suggestions = []
            if "## Recommended Courses" in analysis_text:
                suggestions_section = analysis_text.split("## Recommended Courses")[1].split("##")[0].strip()
                suggestions = [clean_markdown(s.strip().replace("- ", "").replace("* ", "").replace("• ", "")) 
                                 for s in suggestions_section.split("\n") 
                                 if s.strip() and (s.strip().startswith("-") or s.strip().startswith("*") or s.strip().startswith("•"))]
            
            # Extract score
            score = result.get("resume_score", 0)
            if not score:
                score = self._extract_score_from_text(analysis_text)
            
            # Extract ATS score
            ats_score = self._extract_ats_score_from_text(analysis_text)
            
            return {
                "score": score,
                "ats_score": ats_score,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions,
                "full_response": analysis_text,
                "model_used": model_used
            }
            
        except Exception as e:
            print(f"Error in analyze_resume: {str(e)}")
            print(traceback.format_exc())
            return {
                "error": f"Analysis failed: {str(e)}",
                "score": 0,
                "ats_score": 0,
                "strengths": ["Unable to analyze resume due to an error."],
                "weaknesses": ["Unable to analyze resume due to an error."],
                "suggestions": ["Try again with a different model or check your resume format."],
                "full_response": f"Error: {str(e)}",
                "model_used": "Error"
            } 

    def simple_generate_pdf_report(self, analysis_result, candidate_name, job_role):
        """Generate a simple PDF report without complex charts as a fallback"""
        try:
            # Import required libraries
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable, KeepTogether
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.graphics.shapes import Drawing, Rect, String, Line
                from reportlab.graphics.charts.piecharts import Pie
                from reportlab.graphics.charts.barcharts import VerticalBarChart
                from reportlab.graphics.charts.linecharts import HorizontalLineChart
                from reportlab.graphics.charts.legends import Legend
                import io
                import datetime
                import math
            except ImportError as e:
                st.error(f"Error importing PDF libraries: {str(e)}")
                st.info("Please make sure reportlab is installed: pip install reportlab")
                return None
            
            # Helper function to clean markdown formatting
            def clean_markdown(text):
                if not text:
                    return ""
                
                # Remove markdown formatting for bold and italic
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove ** for bold
                text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove * for italic
                text = re.sub(r'__(.*?)__', r'\1', text)      # Remove __ for bold
                text = re.sub(r'_(.*?)_', r'\1', text)        # Remove _ for italic
                
                # Remove markdown formatting for headers
                text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
                
                # Remove markdown formatting for links
                text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
                
                return text.strip()
            
            # Validate input data
            if not analysis_result:
                st.error("No analysis result provided for PDF generation")
                return None
                
            # Create a buffer for the PDF
            buffer = io.BytesIO()
            
            # Create the PDF document
            doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                   leftMargin=0.5*inch, rightMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.darkblue,
                spaceAfter=12,
                alignment=1  # Center alignment
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.darkblue,
                spaceAfter=12,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.white,
                spaceAfter=6,
                backColor=colors.darkblue,
                borderWidth=1,
                borderColor=colors.grey,
                borderPadding=5,
                borderRadius=5,
                alignment=1  # Center alignment
            )
            
            subheading_style = ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.darkblue,
                spaceAfter=6
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                leading=14  # Line spacing
            )
            
            list_item_style = ParagraphStyle(
                'ListItem',
                parent=normal_style,
                leftIndent=20,
                firstLineIndent=-15,
                spaceBefore=2,
                spaceAfter=2
            )
            
            # Create a simple gauge chart class
            class SimpleGaugeChart(Flowable):
                def __init__(self, score, width=300, height=200, label="Resume Score"):
                    Flowable.__init__(self)
                    self.score = int(score) if score is not None else 0  # Ensure score is an integer
                    self.width = width
                    self.height = height
                    self.label = label
                    
                    # Determine color based on score percentage
                    if self.score >= 80:
                        self.color = colors.green
                        self.status = "Excellent"
                    elif self.score >= 60:
                        self.color = colors.orange
                        self.status = "Good"
                    else:
                        self.color = colors.red
                        self.status = "Needs Improvement"
                
                def draw(self):
                    # Draw the gauge
                    canvas = self.canv
                    canvas.saveState()
                    
                    # Draw gauge background (semi-circle)
                    center_x = self.width / 2
                    center_y = self.height / 2
                    radius = min(center_x, center_y) - 30
                    
                    # Draw the gauge background
                    canvas.setFillColor(colors.lightgrey)
                    canvas.setStrokeColor(colors.grey)
                    canvas.setLineWidth(1)
                    
                    # Draw the semi-circle background
                    p = canvas.beginPath()
                    p.moveTo(center_x, center_y)
                    p.arcTo(center_x - radius, center_y - radius, center_x + radius, center_y + radius, 0, 180)
                    p.lineTo(center_x, center_y)
                    p.close()
                    canvas.drawPath(p, fill=1, stroke=1)
                    
                    # Draw the colored arc for the score
                    if self.score > 0:  # Only draw if score > 0
                        angle = 180 * self.score / 100
                        p = canvas.beginPath()
                        p.moveTo(center_x, center_y)
                        p.arcTo(center_x - radius, center_y - radius, center_x + radius, center_y + radius, 180, 180-angle)
                        p.lineTo(center_x, center_y)
                        p.close()
                        canvas.setFillColor(self.color)
                        canvas.drawPath(p, fill=1, stroke=0)
                    
                    # Draw score text
                    canvas.setFillColor(self.color)
                    canvas.setFont("Helvetica-Bold", 24)
                    canvas.drawCentredString(center_x, center_y - 15, f"{self.score}")
                    
                    # Draw status text
                    canvas.setFillColor(self.color)
                    canvas.setFont("Helvetica", 12)
                    canvas.drawCentredString(center_x, center_y - 35, self.status)
                    
                    # Draw "Resume Score" label
                    canvas.setFillColor(colors.darkblue)
                    canvas.setFont("Helvetica-Bold", 14)
                    canvas.drawCentredString(center_x, self.height - 20, self.label)
                    
                    # Draw scale markers
                    canvas.setStrokeColor(colors.black)
                    canvas.setLineWidth(1)
                    for i in range(0, 101, 20):
                        angle_rad = math.radians(180 - (i * 1.8))
                        x = center_x + radius * math.cos(angle_rad)
                        y = center_y + radius * math.sin(angle_rad)
                        
                        # Draw tick marks
                        x2 = center_x + (radius - 5) * math.cos(angle_rad)
                        y2 = center_y + (radius - 5) * math.sin(angle_rad)
                        canvas.line(x, y, x2, y2)
                        
                        # Draw numbers
                        canvas.setFont("Helvetica", 8)
                        num_x = center_x + (radius - 15) * math.cos(angle_rad)
                        num_y = center_y + (radius - 15) * math.sin(angle_rad)
                        canvas.drawCentredString(num_x, num_y, str(i))
                    
                    canvas.restoreState()
                
                def wrap(self, availWidth, availHeight):
                    return (self.width, self.height)
            
            # Create the content
            content = []
            
            # Add a header with date
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            content.append(Paragraph(f"Resume Analysis Report", title_style))
            content.append(Paragraph(f"Generated on {current_date}", subtitle_style))
            content.append(Spacer(1, 0.25*inch))
            
            # Format candidate name - if it's just "Candidate", add a number
            if not candidate_name or candidate_name.lower() == "candidate" or candidate_name.strip() == "":
                import random
                candidate_name = f"Candidate_{random.randint(1000, 9999)}"
            
            # Add candidate name and job role in a table
            info_data = [
                ["Candidate:", candidate_name],
                ["Target Role:", job_role if job_role else "Not specified"]
            ]
            
            info_table = Table(info_data, colWidths=[1.5*inch, 5*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            content.append(info_table)
            content.append(Spacer(1, 0.25*inch))
            
            # Add model used information with proper spacing
            model_used = analysis_result.get("model_used", "AI")
            model_data = [["Analysis performed by:\u2003\u2003\u2003", "", model_used]]
            model_table = Table(model_data, colWidths=[3.5*inch, 1*inch, 5*inch])
            model_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ]))
            
            content.append(model_table)
            content.append(Spacer(1, 0.25*inch))
            
            # Add Resume Evaluation section
            content.append(Paragraph("Resume Evaluation", heading_style))
            content.append(Spacer(1, 0.1*inch))
            
            # Extract scores
            resume_score = analysis_result.get("score", 0)
            if resume_score == 0:
                # Try to get from resume_score
                resume_score = analysis_result.get("resume_score", 0)
                
                # If still 0, try to extract from the analysis text
                if resume_score == 0 and "Resume Score:" in analysis_text:
                    score_match = re.search(r'Resume Score:\s*(\d{1,3})/100', analysis_text)
                    if score_match:
                        resume_score = int(score_match.group(1))
                    else:
                        # Try another pattern
                        score_match = re.search(r'\bResume Score:\s*(\d{1,3})\b', analysis_text)
                        if score_match:
                            resume_score = int(score_match.group(1))
                        else:
                            # Try to find any number after "Resume Score:"
                            score_section = analysis_text.split("Resume Score:")[1].split("\n")[0].strip()
                            score_match = re.search(r'\b(\d{1,3})\b', score_section)
                            if score_match:
                                resume_score = int(score_match.group(1))

            # Ensure resume_score is a valid integer
            resume_score = int(resume_score) if resume_score else 0
            resume_score = max(0, min(resume_score, 100))  # Ensure it's between 0 and 100

            # Create a table with the simple gauge
            score_table_data = [
                ["Resume Score"],
                [SimpleGaugeChart(score=resume_score, width=300, height=200, label="Resume Score")]
            ]
            
            score_table = Table(score_table_data, colWidths=[6*inch])
            score_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, 0), 14),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.darkblue),
                ('BOTTOMPADDING', (0, 0), (0, 0), 10),
            ]))
            
            content.append(score_table)
            content.append(Spacer(1, 0.25*inch))
            
            # Add Executive Summary section
            content.append(Paragraph("Executive Summary", heading_style))
            content.append(Spacer(1, 0.1*inch))
            
            # Extract overall assessment
            analysis_text = analysis_result.get("full_response", "")
            if not analysis_text:
                analysis_text = analysis_result.get("analysis", "")
                
            overall_assessment = ""
            if "## Overall Assessment" in analysis_text:
                overall_section = analysis_text.split("## Overall Assessment")[1].split("##")[0].strip()
                overall_assessment = clean_markdown(overall_section)
            
            content.append(Paragraph(overall_assessment, normal_style))
            content.append(Spacer(1, 0.2*inch))
            
            # Key Strengths and Areas for Improvement section
            content.append(Paragraph("Key Strengths and Areas for Improvement", subheading_style))
            content.append(Spacer(1, 0.1*inch))

            if strengths or weaknesses:
                # Create data for strengths and weaknesses
                sw_data = [["Key Strengths", "Areas for Improvement"]]
                
                # Get max length of strengths and weaknesses
                max_len = max(len(strengths), len(weaknesses), 1)
                
                for i in range(max_len):
                    strength = f"• {clean_markdown(strengths[i])}" if i < len(strengths) else ""
                    weakness = f"• {clean_markdown(weaknesses[i])}" if i < len(weaknesses) else ""
                    sw_data.append([
                        Paragraph(strength, list_item_style) if strength else "",
                        Paragraph(weakness, list_item_style) if weakness else ""
                    ])
                
                sw_table = Table(sw_data, colWidths=[3*inch, 3*inch])
                sw_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.lightgreen),
                    ('BACKGROUND', (1, 0), (1, 0), colors.salmon),
                    ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (1, 0), 10),
                    ('GRID', (0, 0), (1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                content.append(sw_table)
            else:
                # Add empty strengths and weaknesses with a message
                empty_data = [
                    ["Key Strengths", "Areas for Improvement"],
                    [
                        Paragraph("No specific strengths identified in the analysis.", normal_style),
                        Paragraph("No specific areas for improvement identified in the analysis.", normal_style)
                    ]
                ]
                empty_table = Table(empty_data, colWidths=[3*inch, 3*inch])
                empty_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.lightgreen),
                    ('BACKGROUND', (1, 0), (1, 0), colors.salmon),
                    ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (1, 0), 10),
                    ('GRID', (0, 0), (1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                content.append(empty_table)

            content.append(Spacer(1, 0.25*inch))
            
            # Use the process_sections method to handle detailed analysis
            content = self.process_sections(analysis_text, content, normal_style, list_item_style, subheading_style, heading_style, clean_markdown)
            
            # Add course recommendations
            course_recommendations = []
            
            # Try to get course recommendations from different sources
            if "suggestions" in analysis_result:
                course_recommendations = analysis_result.get("suggestions", [])
            
            # If still no recommendations, try to extract from text
            if not course_recommendations and "## Recommended Courses" in analysis_text:
                recommendations_section = analysis_text.split("## Recommended Courses")[1].split("##")[0].strip()
                course_recommendations = [clean_markdown(r.strip().replace("- ", "").replace("* ", "").replace("• ", "")) 
                              for r in recommendations_section.split("\n") 
                              if r.strip() and (r.strip().startswith("-") or r.strip().startswith("*") or r.strip().startswith("•"))]
            
            # Try another pattern for course recommendations
            if not course_recommendations and "Recommended Courses" in analysis_text:
                recommendations_section = analysis_text.split("Recommended Courses")[1]
                if "##" in recommendations_section:
                    recommendations_section = recommendations_section.split("##")[0]
                
                # Extract lines that look like list items
                for line in recommendations_section.split("\n"):
                    line = line.strip()
                    if line and ":" in line and not line.startswith("#"):
                        course_recommendations.append(clean_markdown(line))
            
            content.append(Paragraph("Recommended Courses & Certifications", subheading_style))
            
            if course_recommendations:
                # Create a table for course recommendations with better formatting
                course_data = [["Recommended Courses & Certifications"]]  # Add header row
                
                for course in course_recommendations:
                    # Clean the course text and ensure it doesn't have any markdown formatting
                    cleaned_course = clean_markdown(course)
                    course_data.append([Paragraph(f"• {cleaned_course}", list_item_style)])
                
                course_table = Table(course_data, colWidths=[6*inch])
                course_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Center the header
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Left-align the content
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (0, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (0, 0), 10),
                    ('GRID', (0, 0), (0, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (0, -1), 'TOP'),
                ]))
                
                content.append(course_table)
            else:
                # If still no recommendations, add a text section instead of generic courses
                content.append(Paragraph("Based on your resume and target role, consider the following types of courses and certifications:", normal_style))
                content.append(Spacer(1, 0.1*inch))
                
                # Add role-specific recommendations based on job_role
                role_specific_courses = []
                if "data" in job_role.lower() or "scientist" in job_role.lower() or "analyst" in job_role.lower():
                    role_specific_courses = [
                        "Data Science Specialization (Coursera/edX)",
                        "Machine Learning (Coursera/edX)",
                        "Deep Learning Specialization (Coursera)",
                        "Big Data Technologies (Cloud Provider Certifications)",
                        "Statistical Modeling and Inference",
                        "Data Visualization with Tableau/Power BI"
                    ]
                elif "developer" in job_role.lower() or "engineer" in job_role.lower() or "programming" in job_role.lower():
                    role_specific_courses = [
                        "Full Stack Web Development (Udemy/Coursera)",
                        "Cloud Certifications (AWS/Azure/GCP)",
                        "DevOps and CI/CD Pipelines",
                        "Software Architecture and Design Patterns",
                        "Agile and Scrum Methodologies",
                        "Mobile App Development"
                    ]
                elif "security" in job_role.lower() or "cyber" in job_role.lower():
                    role_specific_courses = [
                        "Certified Information Systems Security Professional (CISSP)",
                        "Certified Ethical Hacker (CEH)",
                        "CompTIA Security+",
                        "Offensive Security Certified Professional (OSCP)",
                        "Cloud Security Certifications",
                        "Security Operations and Incident Response"
                    ]
                else:
                    # Generic professional development courses
                    role_specific_courses = [
                        "LinkedIn Learning - Professional Skills Development",
                        "Coursera - Career Development Specialization",
                        "Udemy - Job Interview Skills Training",
                        "Project Management Professional (PMP)",
                        "Leadership and Management Skills",
                        "Technical Writing and Communication"
                    ]
                
                # Create a table for role-specific courses
                course_data = []
                for course in role_specific_courses:
                    course_data.append([Paragraph(f"• {clean_markdown(course)}", list_item_style)])
                
                course_table = Table(course_data, colWidths=[6*inch])
                course_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                content.append(course_table)
            
            content.append(Spacer(1, 0.2*inch))
            
            # Add footer with page numbers
            def add_page_number(canvas, doc):
                canvas.saveState()
                canvas.setFont('Helvetica', 9)
                page_num = canvas.getPageNumber()
                text = f"Page {page_num}"
                canvas.drawRightString(7.5*inch, 0.25*inch, text)
                
                # Add generation date at the bottom
                canvas.setFont('Helvetica', 9)
                date_text = f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y')}"
                canvas.drawString(0.5*inch, 0.25*inch, date_text)
                
                canvas.restoreState()
            
            # Build the PDF
            doc.build(content, onFirstPage=add_page_number, onLaterPages=add_page_number)
            
            # Get the PDF from the buffer
            buffer.seek(0)
            return buffer
        
        except Exception as e:
            st.error(f"Error generating simple PDF report: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return None 

    def process_sections(self, analysis_text, content, normal_style, list_item_style, subheading_style, heading_style, clean_markdown):
        """Process sections of the analysis text with special handling for certain sections"""
        # Parse the markdown-like content
        sections = analysis_text.split("##")
        
        # Define sections to include in detailed analysis
        detailed_sections = [
            "Professional Profile",
            "Skills Analysis",
            "Experience Analysis",
            "Education & Certifications",
            "ATS Optimization",
            "Role Alignment",
            "Job Match"
        ]
        
        # Add Detailed Analysis section
        content.append(Paragraph("Detailed Analysis", heading_style))
        content.append(Spacer(1, 0.1*inch))
        
        for section in sections:
            if not section.strip():
                continue
            
            # Extract section title and content
            lines = section.strip().split("\n")
            section_title = lines[0].strip()
            
            # Skip sections we don't want in the detailed analysis
            if section_title not in detailed_sections and section_title != "Overall Assessment":
                continue
            
            # Skip Overall Assessment as we've already included it
            if section_title == "Overall Assessment":
                continue
            
            section_content = "\n".join(lines[1:]).strip()
            
            # Add section title
            content.append(Paragraph(section_title, subheading_style))
            content.append(Spacer(1, 0.1*inch))
            
            # Process content based on section
            if section_title == "Skills Analysis":
                # Extract current and missing skills
                current_skills = []
                missing_skills = []
                
                # Check for "Key Skills" or "Current Skills"
                if "Key Skills" in section_content:
                    current_part = section_content.split("Key Skills")[1]
                elif "Current Skills" in section_content:
                    current_part = section_content.split("Current Skills")[1]
                else:
                    current_part = ""
                
                if current_part:
                    if "Missing Skills" in current_part:
                        current_part = current_part.split("Missing Skills")[0]
                    
                    for line in current_part.split("\n"):
                        if line.strip() and ("-" in line or "*" in line or "•" in line):
                            skill = clean_markdown(line.replace("-", "").replace("*", "").replace("•", "").strip())
                            # Remove markdown bold if present
                            skill = skill.replace("**", "").replace("__", "")
                            if skill:
                                current_skills.append(skill)
                
                if "Missing Skills" in section_content:
                    missing_part = section_content.split("Missing Skills")[1]
                    for line in missing_part.split("\n"):
                        if line.strip() and ("-" in line or "*" in line or "•" in line):
                            skill = clean_markdown(line.replace("-", "").replace("*", "").replace("•", "").strip())
                            # Remove markdown bold if present
                            skill = skill.replace("**", "").replace("__", "")
                            if skill:
                                missing_skills.append(skill)
                
                # Create skills table with better formatting
                if current_skills or missing_skills:
                    # Create paragraphs for each skill to ensure proper wrapping
                    current_skill_paragraphs = [Paragraph(skill, normal_style) for skill in current_skills]
                    missing_skill_paragraphs = [Paragraph(skill, normal_style) for skill in missing_skills]
                    
                    # Make sure both lists have the same length
                    max_len = max(len(current_skill_paragraphs), len(missing_skill_paragraphs))
                    current_skill_paragraphs.extend([Paragraph("", normal_style)] * (max_len - len(current_skill_paragraphs)))
                    missing_skill_paragraphs.extend([Paragraph("", normal_style)] * (max_len - len(missing_skill_paragraphs)))
                    
                    # Create data for the table
                    data = [["Key Skills", "Missing Skills"]]
                    for i in range(max_len):
                        data.append([current_skill_paragraphs[i], missing_skill_paragraphs[i]])
                    
                    # Create the table with fixed column widths
                    table = Table(data, colWidths=[3*inch, 3*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
                        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ]))
                    
                    content.append(table)
                
            elif section_title == "ATS Optimization" or section_title == "ATS Optimization Assessment":
                # Special handling for ATS Optimization Assessment
                ats_score_line = ""
                ats_content = []
                
                # Extract ATS score if present
                for line in section_content.split("\n"):
                    if "ATS Score:" in line:
                        ats_score_line = clean_markdown(line)
                    elif line.strip():
                        # Check if it's a list item
                        if line.strip().startswith("-") or line.strip().startswith("*") or line.strip().startswith("•"):
                            ats_content.append("• " + clean_markdown(line.strip()[1:].strip()))
                        else:
                            ats_content.append(clean_markdown(line))
                
                # Add ATS score line if found
                if ats_score_line:
                    content.append(Paragraph(ats_score_line, normal_style))
                    content.append(Spacer(1, 0.1*inch))
                
                # Add the rest of the ATS content
                for para in ats_content:
                    if para.startswith("• "):
                        content.append(Paragraph(para, list_item_style))
                    else:
                        content.append(Paragraph(para, normal_style))
            else:
                # Process regular paragraphs
                paragraphs = section_content.split("\n")
                for para in paragraphs:
                    if para.strip():
                        # Check if it's a list item
                        if para.strip().startswith("-") or para.strip().startswith("*") or para.strip().startswith("•"):
                            para = "• " + clean_markdown(para.strip()[1:].strip())
                            content.append(Paragraph(para, list_item_style))
                        else:
                            content.append(Paragraph(clean_markdown(para), normal_style))
            
            content.append(Spacer(1, 0.2*inch))
        
        return content
