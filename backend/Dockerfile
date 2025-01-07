# Użyj oficjalnego obrazu Pythona jako obrazu bazowego
FROM python:3.9

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Kopiuj plik requirements.txt do katalogu roboczego
COPY requirements.txt ./

# Zainstaluj wszystkie zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj resztę kodu do katalogu roboczego
COPY . .

# Uruchom aplikację FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]