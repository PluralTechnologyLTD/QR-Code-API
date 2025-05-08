from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from uuid import uuid4
from io import BytesIO
import qrcode
import base64

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simulated in-memory database (use real DB for production)
qr_store = {}

# Replace this with your actual Render app URL after deploying
PUBLIC_BASE_URL = "https://yourappname.onrender.com"


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse(
        "form.html", {"request": request, "qr_code": None}
    )


@app.post("/generate_qr/", response_class=HTMLResponse)
async def generate_qr(
    request: Request, project_name: str = Form(...), fov: int = Form(...)
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate unique QR ID and store info
    qr_id = str(uuid4())
    qr_store[qr_id] = {"project_name": project_name, "fov": fov, "datetime": now}

    # Public URL stored in QR code
    qr_url = f"{PUBLIC_BASE_URL}/qr_info/{qr_id}"

    # Create QR code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for embedding in HTML
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return templates.TemplateResponse(
        "form.html", {"request": request, "qr_code": qr_base64}
    )


@app.get("/qr_info/{qr_id}", response_class=HTMLResponse)
async def show_qr_info(request: Request, qr_id: str):
    data = qr_store.get(qr_id)
    if not data:
        return HTMLResponse("<h2>QR Info not found.</h2>", status_code=404)

    return templates.TemplateResponse(
        "qr_info.html", {"request": request, "data": data}
    )
