import re
import os

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from app.gemini_pro import generate_story
from app.image_generator import generate_image

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form("Free"),
    setting: str = Form("Forest"),
    tone: str = Form("Dramatic"),
    style: str = Form("Comic Book")
):

    combined_prompt = (
        f"Character Name: {character_name}, "
        f"Setting: {setting}, "
        f"Tone: {tone}, "
        f"Style: {style}. "
        f"Story Idea: {prompt}"
    )

    # Generate story
    story_result = generate_story([combined_prompt])

    panels = []

    if isinstance(story_result, str):

        # Panel 1, Panel 2, Panel 3... split
        panel_parts = re.split(
            r'(?i)(?=Panel\s*\d+\s*:)',
            story_result
        )

        for part in panel_parts:

            part = part.strip()

            if not part:
                continue

            match = re.match(
                r'(?i)Panel\s*(\d+)\s*:\s*(.*)',
                part,
                re.DOTALL
            )

            if match:

                panel_number = match.group(1)
                panel_text = match.group(2).strip()

                filename = f"panel_{panel_number}.png"

                image_path = generate_image(
                    panel_text,
                    filename=filename
                )

                image_url = "/" + image_path.replace("\\", "/")

                panels.append({
                    "number": panel_number,
                    "text": panel_text,
                    "image": image_url
                })

    # Create PDF
    pdf_path = create_comic_pdf(panels)

    # Extract title
    title = "My Comic"

    if isinstance(story_result, str):

        lines = [
            line.strip()
            for line in story_result.splitlines()
            if line.strip()
        ]

        if lines:
            first_line = lines[0]

            if not re.match(
                r'(?i)^Panel\s*\d+\s*:',
                first_line
            ):
                title = first_line

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": story_result,
            "title": title,
            "panels": panels,
            "download_url": "/download-comic",
            "prompt": prompt,
            "character_name": character_name,
            "setting": setting,
            "tone": tone,
            "style": style
        }
    )


def create_comic_pdf(panels):

    os.makedirs("static/comics", exist_ok=True)

    pdf_path = "static/comics/generated_comic.pdf"

    page_width, page_height = A4

    pdf = canvas.Canvas(
        pdf_path,
        pagesize=A4
    )

    for panel in panels:

        image_url = panel["image"]

        image_path = image_url.lstrip("/").replace(
            "/",
            os.sep
        )

        if not os.path.exists(image_path):
            continue

        # Panel number
        pdf.setFont(
            "Helvetica-Bold",
            20
        )

        pdf.drawCentredString(
            page_width / 2,
            page_height - 40,
            f"Panel {panel['number']}"
        )

        # Panel description
        pdf.setFont(
            "Helvetica",
            11
        )

        text = pdf.beginText(
            40,
            page_height - 65
        )

        text.setLeading(14)

        # Keep description short enough for PDF
        words = panel["text"].split()

        line = ""

        for word in words:

            test_line = line + " " + word

            if pdf.stringWidth(
                test_line,
                "Helvetica",
                11
            ) < page_width - 80:

                line = test_line

            else:

                text.textLine(line.strip())

                line = word

        if line:
            text.textLine(line.strip())

        pdf.drawText(text)

        # Image
        image = ImageReader(image_path)

        image_width, image_height = image.getSize()

        margin = 40

        max_width = page_width - (margin * 2)

        max_height = page_height - 180

        scale = min(
            max_width / image_width,
            max_height / image_height
        )

        final_width = image_width * scale
        final_height = image_height * scale

        x = (page_width - final_width) / 2

        y = 60

        pdf.drawImage(
            image,
            x,
            y,
            width=final_width,
            height=final_height,
            preserveAspectRatio=True,
            mask="auto"
        )

        pdf.showPage()

    pdf.save()

    return pdf_path


@router.get("/download-comic")
async def download_comic():

    pdf_path = "static/comics/generated_comic.pdf"

    if not os.path.exists(pdf_path):

        return {
            "error": "Please generate the comic first."
        }

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="ComicCraft_Comic.pdf"
    )