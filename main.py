from fastapi import FastAPI, HTTPException
import requests
from shapely.geometry import LineString

app = FastAPI(title="GTFS Route Length API")

@app.get("/")
def root():
    return {"message": "API para calcular longitud de rutas OSM"}

@app.get("/route_length/{route_id}")
def route_length(route_id: int):
    try:
        query = f"""
        [out:json];
        relation({route_id});
        way(r);
        (._;>;);
        out geom;
        """
        response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
        data = response.json()

        coords = []
        for element in data["elements"]:
            if element["type"] == "way" and "geometry" in element:
                coords += [(pt["lon"], pt["lat"]) for pt in element["geometry"]]

        if not coords:
            raise ValueError("No se encontraron coordenadas.")

        line = LineString(coords)
        length_km = line.length * 111  # Aproximado

        return {"route_id": route_id, "length_km": round(length_km, 3)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
