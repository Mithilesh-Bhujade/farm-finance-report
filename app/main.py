from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import tempfile

from app.schemas import FarmerData
from app.pdf_generator import generate_pdf

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def form_ui(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate-pdf")
async def generate(
    request: Request,
    farmer_name: str = Form(...),
    crop_name: str = Form(...),
    season: str = Form(...),
    total_acres: float = Form(...),
    total_production: float | None = Form(None),
    sowing_date: str = Form(...),
    harvest_date: str = Form(...),
    location: str = Form(...),
    expenses_json: str = Form("[]"),
    incomes_json: str = Form("[]"),
):
    try:
        expenses = json.loads(expenses_json)
        incomes = json.loads(incomes_json)
    except json.JSONDecodeError:
        return RedirectResponse(url="/", status_code=303)

    if total_acres is None or total_acres <= 0:
        return RedirectResponse(url="/", status_code=303)

    data = FarmerData(
        farmer_name=farmer_name,
        crop_name=crop_name,
        season=season,
        total_acres=total_acres,
        total_production=total_production,
        sowing_date=sowing_date,
        harvest_date=harvest_date,
        location=location,
        expenses=expenses,
        incomes=incomes,
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = generate_pdf(data, output_path=tmp.name)

    return FileResponse(pdf_path, filename="farm_report.pdf", media_type="application/pdf")
