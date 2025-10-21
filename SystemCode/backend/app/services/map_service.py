from fastapi.responses import HTMLResponse
from app.models import PropertyLocation


def fetch_map_page(location: PropertyLocation) -> HTMLResponse:
    pass