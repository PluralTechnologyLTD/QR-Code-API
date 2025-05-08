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

# In-memory database (replace with real DB in production)
qr_store = {}


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

    # Generate a unique ID for this entry
    qr_id = str(uuid4())
    qr_store[qr_id] = {"project_name": project_name, "fov": fov, "datetime": now}

    # Construct a URL to be stored in QR code
    base_url = str(request.base_url).rstrip("/")
    qr_url = f"{base_url}/qr_info/{qr_id}"

    # Generate QR code with URL
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
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
