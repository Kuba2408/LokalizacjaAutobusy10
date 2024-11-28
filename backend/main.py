import folium
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="myGeocoder")

adres = "Warszawa, Polska"
location = geolocator.geocode(adres)
if location:
    print(f"Lokalizacja znaleziona: {location.address}")
    print(f"Współrzędne: {location.latitude}, {location.longitude}")
    mapa = folium.Map(location=[location.latitude, location.longitude], zoom_start=12)
    folium.Marker([location.latitude, location.longitude], popup=location.address).add_to(mapa)
    mapa.save("mapa_lokalizacji.html")
    print("Mapa została zapisana jako mapa_lokalizacji.html")
else:
    print("Nie znaleziono lokalizacji.")