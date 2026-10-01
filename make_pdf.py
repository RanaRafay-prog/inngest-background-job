from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

doc = SimpleDocTemplate("explain_it_like_you_built_it.pdf", pagesize=letter)
story = []
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'TitleStyle',
    parent=styles['Heading1'],
    fontSize=18,
    spaceAfter=15,
    textColor='#2c3e50'
)

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['Normal'],
    fontSize=11,
    leading=16,
    spaceAfter=10,
    textColor='#333333'
)

story.append(Paragraph("Explain It Like You Built It: Idempotency in Our Report Pipeline", title_style))
story.append(Spacer(1, 10))

text = """
Imagine you and a friend are ordering food at a restaurant, and the app is a bit laggy. You tap the "Place Order" button twice by accident. If the system isn't careful, it might charge your card twice and send two identical meals to your table.<br/><br/>
In our FastAPI and Inngest background job pipeline, we solved this exact problem using something called <b>Idempotency</b>.<br/><br/>
Here is how it actually works under the hood in plain English:<br/><br/>
1. <b>Checking Today's Date First:</b> When someone sends a POST request to /reports, the server doesn't immediately start building a brand-new report. Instead, it first looks into our SQLite database and asks: 'Did anyone already generate a report today?'<br/><br/>
2. <b>The Database Query:</b> It runs a quick check looking at the creation timestamp matched against today's date.<br/><br/>
3. <b>Smart Decision Making:</b><br/>
- If <b>no report exists</b> for today, the server goes ahead, triggers the background job, generates the PDF, and saves a new record (201 Created).<br/>
- If <b>a report already exists</b> for today, the server stops right there, skips running the heavy PDF generator again, and immediately sends back the exact same existing report link and a message saying: 'Returned existing report for today (Idempotent)' (200 OK).<br/><br/>
Why is this cool? It saves server CPU power, prevents redundant file clutter on the hard drive, and ensures that hitting the endpoint multiple times behaves safely without duplication. It’s like the system saying, 'I got your request, but since I already did this for you today, here is the exact same receipt.'
"""

story.append(Paragraph(text, body_style))
doc.build(story)
print("PDF generated successfully!")