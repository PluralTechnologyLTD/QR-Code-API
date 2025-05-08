from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from datetime import datetime
import qrcode
import os


# "Url for the QR code: https://qr-code-api-k1k4.onrender.com"

app = FastAPI()

# Static files for Tailwind CSS and QR images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# In-memory QR code data store
qr_data_store = {}


@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/generate_qr/", response_class=HTMLResponse)
async def generate_qr(
    request: Request, project_name: str = Form(...), fov: int = Form(...)
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qr_id = str(uuid4())

    data = {"project_name": project_name, "fov": fov, "timestamp": timestamp}
    qr_data_store[qr_id] = data

    url = f"{request.base_url}qr_info/{qr_id}"
    img = qrcode.make(url)
    img_path = f"static/qr_{qr_id}.png"
    img.save(img_path)

    return templates.TemplateResponse(
        "qr_display.html",
        {"request": request, "qr_url": f"/{img_path}", "info_url": url},
    )


@app.get("/qr_info/{qr_id}", response_class=HTMLResponse)
async def show_qr_info(request: Request, qr_id: str):
    if qr_id not in qr_data_store:
        return HTMLResponse(content="QR Code not found", status_code=404)

    data = qr_data_store[qr_id]
    return templates.TemplateResponse(
        "qr_info.html", {"request": request, "data": data}
    )
