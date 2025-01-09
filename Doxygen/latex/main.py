from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import asyncio
import warsaw_data_api
from math import radians, cos, sin, asin, sqrt
from datetime import datetime, timedelta

# ===========================
# Zmienne aplikacji
# ===========================

## @var allow_credentials
# Określa, czy ciasteczka i dane uwierzytelniające mogą być wysyłane w odpowiedzi.
allow_credentials = True  # Wartość domyślna: True

## @var allow_headers
# Określa, jakie nagłówki mogą być przesyłane w żądaniu.
allow_headers = ["*"]  # Wartość domyślna: Wszystkie nagłówki

## @var allow_methods
# Określa, które metody HTTP są dozwolone.
allow_methods = ["*"]  # Wartość domyślna: Wszystkie metody

## @var allow_origins
# Określa, które domeny mogą uzyskać dostęp do aplikacji (CORS).
allow_origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8080",
]

## @var app
# Główna instancja aplikacji FastAPI
# Tworzenie instancji aplikacji FastAPI, która będzie obsługiwać żądania HTTP.
app = FastAPI()

## @var origins
# Lista dozwolonych źródeł (domen), które mogą komunikować się z aplikacją przez CORS.
origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8080",
]

## @var redis_client
# Połączenie z serwerem Redis w celu przechowywania danych aplikacji
# Redis jest używany do przechowywania informacji o lokalizacji autobusów.
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

## @var ztm_API_key
# Klucz API do ZTM, używany do autoryzacji przy pobieraniu danych o autobusach
ztm_API_key = "b4754db8-835f-4359-85a1-eae1229e54b9"

## @var ztm
# Instancja API ZTM do pobierania danych o warszawskich autobusach.
ztm = warsaw_data_api.ztm(apikey=ztm_API_key)

# ===========================
# Funkcje aplikacji
# ===========================

def haversine(lat1, lon1, lat2, lon2):
    """
    Funkcja pomocnicza do obliczania odległości na podstawie wzoru Haversine.

    Ta funkcja oblicza odległość w kilometrach pomiędzy dwoma punktami na powierzchni Ziemi,
    podając ich współrzędne geograficzne (szerokość i długość geograficzną).

    :param lat1: Szerokość geograficzna pierwszego punktu w stopniach.
    :param lon1: Długość geograficzna pierwszego punktu w stopniach.
    :param lat2: Szerokość geograficzna drugiego punktu w stopniach.
    :param lon2: Długość geograficzna drugiego punktu w stopniach.
    :return: Odległość pomiędzy dwoma punktami w kilometrach.
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Promień Ziemi w kilometrach
    return c * r


async def update_bus_location_in_background():
    """
    Funkcja asynchroniczna do aktualizacji lokalizacji autobusów w Redis.

    Funkcja ta pobiera dane o autobusach z API i zapisuje je w bazie danych Redis co 10 sekund.
    Każdy autobus jest zapisany w osobnym kluczu, a także dodawany do zestawu linii autobusowej.

    Funkcja działa w tle aplikacji i działa w nieskończonej pętli.
    """
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

            # Ignoruj autobusy, które nie zostały odświeżone w ciągu ostatnich 4 godzin
            if datetime.now() - bus.time > timedelta(hours=4):
                continue

            # Sprawdź, czy klucz istnieje w Redis, aby uniknąć błędów
            if await redis_client.exists(bus_key):
                current_type = await redis_client.type(bus_key)
                if current_type != "hash":
                    print(f"Key {bus_key} has wrong type ({current_type}). Deleting it.")
                    await redis_client.delete(bus_key)

            # Zapisz dane autobusu w Redis
            try:
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
    """
    Funkcja uruchamiana podczas startu aplikacji.

    Funkcja ta uruchamia zadanie aktualizacji lokalizacji autobusów w tle.
    """
    asyncio.create_task(update_bus_location_in_background())


@app.get("/get_locations_line/{bus_line}")
async def get_locations_line(bus_line: str):
    """
    Endpoint do pobierania wszystkich lokalizacji autobusów danej linii.

    :param bus_line: Numer linii autobusowej.
    :return: JSON zawierający listę autobusów i ich lokalizacje.
    :raises HTTPException: Jeśli linia autobusowa nie istnieje lub nie ma dostępnych autobusów.
    """
    line_key = f'line:{bus_line}'  # Klucz w Redis dla danej linii
    bus_keys = await redis_client.smembers(line_key)  # Pobierz zestaw kluczy dla tej linii
    buses = []

    # Jeśli nie znaleziono autobusów w danej linii
    if not bus_keys:
        raise HTTPException(status_code=404, detail=f"Bus line {bus_line} not found or no buses available.")

    # Przechodzimy przez listę kluczy autobusów, pobieramy dane każdego autobusu
    for bus_key in bus_keys:
        try:
            bus_data = await redis_client.hgetall(bus_key)
            if bus_data.get('line') != bus_line:
                continue
            if isinstance(bus_data, dict):  # Upewnij się, że bus_data to słownik
                buses.append(bus_data)
            else:
                print(f"Invalid data format for bus {bus_key}: {bus_data}")
        except Exception as e:
            print(f"Error fetching data for bus {bus_key}: {str(e)}")
    
    return {"buses": buses}


@app.get("/get_locations/")
async def get_location(
    bus_line: str,
    user_lat: float,
    user_lng: float,
    user_range: float
):
    """
    Endpoint do pobierania autobusów w zasięgu użytkownika.

    :param bus_line: Numer linii autobusowej.
    :param user_lat: Szerokość geograficzna użytkownika.
    :param user_lng: Długość geograficzna użytkownika.
    :param user_range: Zasięg w kilometrach.
    :return: JSON zawierający listę autobusów w zasięgu użytkownika.
    :raises HTTPException: Jeśli brak autobusów w zasięgu.
    """
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
    """
    Endpoint do pobierania wszystkich danych z Redis.

    Pobiera wszystkie dane przechowywane w Redis, niezależnie od typu (string, hash, set).

    :return: JSON zawierający wszystkie dane z Redis.
    """
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
