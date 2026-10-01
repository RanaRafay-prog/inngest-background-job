from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

doc = SimpleDocTemplate("agent_design_document.pdf", pagesize=letter)
story = []
styles = getSampleStyleSheet()

title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, spaceAfter=12, textColor='#2c3e50')
heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=13, spaceBefore=10, spaceAfter=6, textColor='#2980b9')
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8, textColor='#333333')

story.append(Paragraph("Personal AI Agent Design Document: Study Coach & Tracker", title_style))
story.append(Spacer(1, 5))

content = """
<b>1. Job to Be Done:</b><br/>
Personal Study Coach and Academic Progress Tracker. Ingests coursework notes and schedule to answer complex questions, generate quizzes, and track milestones.<br/><br/>
<b>2. User & Usage Frequency:</b><br/>
Undergraduate Software Engineering student; daily active usage (15-30 mins/day).<br/><br/>
<b>3. Tools, Data Needed & Access Plan:</b><br/>
- Data Sources: Local Markdown/PDF lecture notes and university course outlines.<br/>
- Tools: Filesystem Reader Tool & SQLite Database Connector.<br/>
- Access Plan: Local read/write permissions scoped strictly to project directories.<br/><br/>
<b>4. Draft Agent Instructions:</b><br/>
'You are an expert AI Study Coach grounded exclusively in the user's local academic notes. Maintain an encouraging, direct, and academically rigorous tone.'<br/><br/>
<b>5. Pre-Build Eval Cases:</b><br/>
1. Accurate Retrieval from Notes: Verify responses use exact local definitions.<br/>
2. Missing Data Handling: Acknowledge missing files without hallucination.<br/>
3. Quiz Generation: Produce tailored practice questions matching syllabus difficulty.<br/>
4. Schedule Conflict Resolution: Prioritize tasks based on weight and deadlines.<br/>
5. Guardrail Test: Refuse to solve active graded exam questions directly.<br/><br/>
<b>6. Risks, Guardrails & Boundaries:</b><br/>
- Must Confirm: Any automated rescheduling or milestone log modifications.<br/>
- Must Never Do: Output direct solutions to active graded exams or modify system files.<br/><br/>
<b>7. Platform Choice & Justification:</b><br/>
Claude Project with Filesystem Connectors. Chosen over generic GPTs for secure, direct local file access while preserving data privacy over personal university materials.
"""
story.append(Paragraph(content, body_style))
doc.build(story)
print("Agent PDF generated successfully!")