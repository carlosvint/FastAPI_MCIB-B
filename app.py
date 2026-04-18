from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import pandas as pd
import time
import googlemaps

app = FastAPI() # definimos la aplicacion

app.mount("/static", StaticFiles(directory="static"), name="static") # montamos la carpeta static para servir archivos estaticos
templates = Jinja2Templates(directory="templates") # definimos la carpeta templates para servir las plantillas HTML

API_KEY = os.getenv("GOOGLE_API_KEY_2") # obtenemos la clave de la API de Google Maps desde las variables de entorno

gmaps = googlemaps.Client(key=API_KEY) # inicializamos el cliente de Google Maps

def get_restaurants():
    location = (-0.159268, -78.464914)
    radius = 1000
    place_type = 'restaurant'

    results_list = []
    MAX_REQUEST = 40
    request_count = 0

    response = gmaps.places_nearby(
        location = location,
        radius = radius,
        type = place_type
    )

    while response:
        for place in response['results']:
            results_list.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating"),
                "users": place.get("user_ratings_total"),
                "price_level": place.get("price_level"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"]
            })

        request_count += 1
        if request_count >= MAX_REQUEST:
            break

        if 'next_page_token' in response and request_count < MAX_REQUEST:
            time.sleep(5)
            response = gmaps.places_nearby(
                page_token = response["next_page_token"]
            )
        else:
            break

@app.get("/api/restaurants")
def restaurants_api():
    return get_restaurants()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )