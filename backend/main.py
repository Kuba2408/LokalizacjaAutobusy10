from fastapi import FastAPI, HTTPException
import redis
import asyncio
import warsaw_data_api
from math import radians, cos, sin, asin, sqrt

# Konfiguracja aplikacji i Redis
app = FastAPI()
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
ztm_API_key = "b4754db8-835f-4359-85a1-eae1229e54b9"
ztm = warsaw_data_api.ztm(apikey=ztm_API_key)

# Funkcja pomocnicza do obliczania odległości
def haversine(lat1, lon1, lat2, lon2):
    # Konwersja stopni na radiany
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Wzór haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Promień Ziemi w kilometrach
    return c * r

# Funkcja do aktualizacji lokalizacji w Redis
async def update_bus_location_in_background():
    while True:
        try:
            buses = ztm.get_buses_location()
            if not buses:
                print("No buses data received.")
                await asyncio.sleep(10)
                continue

            for bus in buses:
                bus_key = bus.brigade
                bus_line = int(bus.lines)
                # Zapisz dane autobusu w Redis
                await redis_client.hset(bus_key, mapping={
                    "line": bus_line,
                    "latitude": bus.location.latitude,
                    "longitude": bus.location.longitude,
                })
                await redis_client.expire(bus_key, 20)  # Ustaw TTL na 20 sekund

                # Dodaj klucz autobusu do zestawu linii
                await redis_client.sadd(bus_line, bus_key)
                await redis_client.expire(bus_line, 20)
        except Exception as e:
            print(f"An error occurred while updating bus locations: {e}")
        print("Data updated successfully.")
        await asyncio.sleep(10)  # Czekaj 10 sekund przed następną aktualizacją

# Uruchomienie funkcji aktualizującej podczas startu aplikacji
@app.on_event("startup")
async def startup_event():
    await asyncio.create_task(update_bus_location_in_background())

# Endpoint testowy
@app.get("/test")
def read_root():
    return {"message": "Hello, TrackMyBus!"}

# Endpoint do pobierania wszystkich lokalizacji autobusów danej linii
@app.get("/get_locations_line/{bus_line}")
def get_locations_line(bus_line):
    line_key = bus_line
    bus_keys = redis_client.smembers(line_key)
    buses = []
    if bus_keys:
        for bus_key in bus_keys:
            bus_data = redis_client.hgetall(bus_key)
            buses.append(bus_data)
        return bus_keys
    else:
        raise HTTPException(status_code=404, detail="Bus line not found or no buses available.")

# Endpoint do pobierania autobusów w zasięgu użytkownika
@app.get("/get_locations/")
async def get_location(
    bus_line: str,
    user_lat: float,
    user_lng: float,
    user_range: float
):
    line_key = bus_line
    bus_keys = redis_client.smembers(line_key)
    buses_in_range = []
    if bus_keys:
        for bus_key in bus_keys:
            bus_data = redis_client.hgetall(bus_key)
            bus_lat = float(bus_data['latitude'])
            bus_lng = float(bus_data['longitude'])
            distance = haversine(user_lat, user_lng, bus_lat, bus_lng)
            if distance <= user_range:
                buses_in_range.append(bus_data)
        if buses_in_range:
            return buses_in_range
        else:
            raise HTTPException(status_code=404, detail="No buses in range.")
    else:
        raise HTTPException(status_code=404, detail="Bus line not found.")

@app.get("/get_all_data")
def get_all_data():
    keys = redis_client.keys('*')
    data = {}
    for key in keys:
        key_type = redis_client.type(key)
        if key_type == 'string':
            data[key] = redis_client.get(key)
        elif key_type == 'hash':
            data[key] = redis_client.hgetall(key)
        elif key_type == 'set':
            data[key] = list(redis_client.smembers(key))
        else:
            data[key] = f"Unsupported type: {key_type}"
    return data
