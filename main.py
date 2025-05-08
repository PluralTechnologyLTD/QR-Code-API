from fastapi import FastAPI, Request, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uuid
from datetime import datetime
import os

app = FastAPI()

# In-memory store for QR data (you can later replace this with a database)
qr_store = {}

# Initialize Jinja2 Templates with the correct path to the templates folder
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)


# Pydantic model to store project info
class QRData(BaseModel):
    project_name: str
    fov: int
    date_time: str


@app.post("/generate_qr/")
async def generate_qr(request: Request, project_name: str, fov: int):
    # Generate unique QR ID
    qr_id = str(uuid.uuid4())
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a QR data object
    qr_data = QRData(project_name=project_name, fov=fov, date_time=date_time)

    # Store QR data in memory (in a real app, use a database)
    qr_store[qr_id] = qr_data

    # Generate a URL to access the data
    qr_url = f"{request.url_for('show_qr_info', qr_id=qr_id)}"

    # Generate QR code (you can integrate a library like `qrcode` here to generate the actual image)
    # Here we simply return the URL for simplicity.
    return {"qr_url": qr_url, "qr_id": qr_id}


@app.get("/qr_info/{qr_id}", response_class=HTMLResponse)
async def show_qr_info(request: Request, qr_id: str):
    data = qr_store.get(qr_id)
    if not data:
        return HTMLResponse(
            "<h2>QR Info not found. Please try scanning a valid QR code.</h2>",
            status_code=404,
        )

    # Render the QR information page with data
    return templates.TemplateResponse(
        "qr_info.html", {"request": request, "data": data}
    )


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})
