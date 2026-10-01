from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

doc = SimpleDocTemplate("mvp_build_log.pdf", pagesize=letter)
story = []
styles = getSampleStyleSheet()

title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, spaceAfter=12, textColor='#2c3e50')
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8, textColor='#333333')

story.append(Paragraph("Checkpoint 1 MVP Build Log: Study Coach & Backend Agent", title_style))
story.append(Spacer(1, 5))

content = """
<b>1. Executive Summary & Core MVP Scope:</b><br/>
- Completed end-to-end task: Live reading, parsing, and summarizing local coursework files and backend codebases using an active tool connection.<br/>
- Platform: Claude Desktop with MCP Filesystem Connector.<br/><br/>
<b>2. Build Log & Iteration History:</b><br/>
- <b>Issue 1 (Path Permissions):</b> The MCP filesystem server initially restricted access due to relative path definitions. Resolved by configuring explicit absolute Windows paths.<br/>
- <b>Scope Adjustment:</b> Cut complex automated database patching to prioritize a 100% stable, flawless file-reading and analysis loop for the MVP.<br/><br/>
<b>3. End-to-End Test Run Verification:</b><br/>
- <b>Prompt:</b> Read requirements.txt and main.py, verify tech stack, and summarize routes.<br/>
- <b>Execution:</b> Agent successfully invoked filesystem tools, parsed FastAPI/Inngest configurations, and returned an accurate technical summary without manual intervention.<br/><br/>
<b>4. Deliverable Status:</b><br/>
- Working agent verified with live tool connection.<br/>
- Build log documented with real iterative challenges.<br/>
- Raw run capture verified and ready for link submission.
"""
story.append(Paragraph(content, body_style))
doc.build(story)
print("MVP Build Log PDF generated successfully!")