from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# Extract text from the original PDF
extracted_text = extract_text('example.pdf', laparams=LAParams())

# Write the extracted text into a new PDF with corrected text direction
output_pdf_path = "corrected_example.pdf"
packet = io.BytesIO()
can = canvas.Canvas(packet, pagesize=letter)

# Add the extracted text to the canvas
text_object = can.beginText(40, 750)
text_object.setFont("Helvetica", 10)

for line in extracted_text.split('\n'):
    text_object.textLine(line)

can.drawText(text_object)
can.save()

# Move to the beginning of the StringIO buffer
packet.seek(0)

# Create a new PDF with ReportLab
new_pdf = PdfReader(packet)
existing_pdf = PdfReader(open("example.pdf", "rb"))
output = PdfWriter()

# Add the "watermark" (which is the new pdf) on the existing page
for i in range(len(existing_pdf.pages)):
    page = existing_pdf.pages[i]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

# Finally, write "output" to a real file
with open(output_pdf_path, "wb") as outputStream:
    output.write(outputStream)
