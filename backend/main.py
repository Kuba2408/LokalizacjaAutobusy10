import requests

def get_public_ip():
    response = requests.get('https://ipinfo.io/ip')
    return response.text.strip()

def get_geolocation(ip_address):
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

ip = get_public_ip()
location = get_geolocation(ip)

if location:
    print(f"IP: {location.get('ip')}")
    print(f"Miasto: {location.get('city')}")
    print(f"Region: {location.get('region')}")
    print(f"Kraj: {location.get('country')}")
    print(f"Lokalizacja: {location.get('loc')}")
else:
    print("Nie udało się uzyskać danych o lokalizacji.")
