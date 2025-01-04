from fastapi import FastAPI, HTTPException
import redis.asyncio as redis
import asyncio
import warsaw_data_api
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta

# Konfiguracja aplikacji i Redis
app = FastAPI()
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
ztm_API_key = "b4754db8-835f-4359-85a1-eae1229e54b9"
ztm = warsaw_data_api.ztm(apikey=ztm_API_key)

# Funkcja pomocnicza do obliczania odległości
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Promień Ziemi w kilometrach
    return c * r

# Funkcja do aktualizacji lokalizacji w Redis
async def update_bus_location_in_background():
    while True:
        # Pobieranie danych o autobusach z API
        try:
            buses = ztm.get_buses_location()
        except:
            print('Could not fetch data')
            await asyncio.sleep(1)
            continue
        if not buses:
            print("No buses data received.")
            await asyncio.sleep(10)
            continue

        for bus in buses:
            bus_key = f"bus:{bus.brigade}"  # Dodanie prefiksu dla klucza autobusu
            bus_line = f"line:{bus.lines}"  # Dodanie prefiksu dla linii autobusowej

            # Ignoruj autobusy, ktore nie zostaly odswiezone w ciagu ostatnich 4 godzin
            if datetime.now()- bus.time > timedelta(hours=4):
                continue
            # Sprawdź, czy klucz istnieje w Redis, aby uniknąć błędów
            if await redis_client.exists(bus_key):
                current_type = await redis_client.type(bus_key)
                if current_type != "hash":
                    print(f"Key {bus_key} has wrong type ({current_type}). Deleting it.")
                    await redis_client.delete(bus_key)

            # Zapisz dane autobusu w Redis
            try:
                # Sprawdź, czy dane autobusu są poprawne
                bus_data = {
                    "line": bus.lines,
                    "latitude": bus.location.latitude,
                    "longitude": bus.location.longitude,
                }
                if isinstance(bus_data, dict):  # Upewnij się, że to słownik
                    await redis_client.hset(bus_key, mapping=bus_data)
                    await redis_client.expire(bus_key, 20)  # Ustaw TTL na 20 sekund
                else:
                    print(f"Invalid bus data format for bus {bus_key}: {bus_data}")
            except Exception as e:
                print(f"Error saving bus data to Redis for key {bus_key}: {e}")

            # Dodaj autobus do zestawu linii (set)
            try:
                await redis_client.sadd(bus_line, bus_key)
                await redis_client.expire(bus_line, 20)  # TTL na zestaw linii
            except Exception as e:
                print(f"Error adding bus key to line set in Redis for line {bus_line}: {e}")

        print("Data updated successfully.")

        
        # Czekaj 10 sekund przed następną aktualizacją
        await asyncio.sleep(10)

# Uruchomienie funkcji aktualizującej podczas startu aplikacji
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_bus_location_in_background())

# Endpoint do pobierania wszystkich lokalizacji autobusów danej linii
@app.get("/get_locations_line/{bus_line}")
async def get_locations_line(bus_line: str):
    line_key = f'line:{bus_line}'  # Klucz w Redis dla danej linii
    bus_keys = await redis_client.smembers(line_key)  # Pobierz zestaw kluczy dla tej linii
    buses = []

    # Jeśli nie znaleziono autobusów w danej linii
    if not bus_keys:
        raise HTTPException(status_code=404, detail=f"Bus line {bus_line} not found or no buses available.")

    # Przechodzimy przez listę kluczy autobusów, pobieramy dane każdego autobusu
    for bus_key in bus_keys:
        try:
            # Odczytujemy dane autobusu z hash w Redisie
            bus_data = await redis_client.hgetall(bus_key)
            if(bus_data['line']) != bus_line:
                continue
            if isinstance(bus_data, dict):  # Upewnij się, że bus_data to słownik
                buses.append(bus_data)
            else:
                print(f"Invalid data format for bus {bus_key}: {bus_data}")
        except Exception as e:
            print(f"Error fetching data for bus {bus_key}: {str(e)}")
    
    # Zwracamy dane autobusów w formacie JSON
    return {"buses": buses}

# Endpoint do pobierania autobusów w zasięgu użytkownika
@app.get("/get_locations/")
async def get_location(
    bus_line: str,
    user_lat: float,
    user_lng: float,
    user_range: float
):
    line_key = f'line:{bus_line}'
    bus_keys = await redis_client.smembers(line_key)
    buses_in_range = []

    if not bus_keys:
        raise HTTPException(status_code=404, detail=f"Bus line {bus_line} not found.")

    for bus_key in bus_keys:
        try:
            bus_data = await redis_client.hgetall(bus_key)
            if isinstance(bus_data, dict):  # Upewnij się, że bus_data to słownik
                bus_lat = float(bus_data['latitude'])
                bus_lng = float(bus_data['longitude'])
                distance = haversine(user_lat, user_lng, bus_lat, bus_lng)
                if distance <= user_range:
                    buses_in_range.append(bus_data)
            else:
                print(f"Invalid data format for bus {bus_key}: {bus_data}")
        except Exception as e:
            print(f"Error processing bus {bus_key}: {e}")

    if buses_in_range:
        return {"buses_in_range": buses_in_range}
    else:
        raise HTTPException(status_code=404, detail="No buses in range.")

@app.get("/get_all_data")
async def get_all_data():
    keys = await redis_client.keys('*')
    data = {}
    for key in keys:
        key_type = await redis_client.type(key)
        if key_type == 'string':
            data[key] = await redis_client.get(key)
        elif key_type == 'hash':
            data[key] = await redis_client.hgetall(key)
        elif key_type == 'set':
            data[key] = await redis_client.smembers(key)
        else:
            data[key] = f"Unsupported type: {key_type}"
    return data
