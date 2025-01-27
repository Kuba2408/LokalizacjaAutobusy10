
# Aplikacja TrackMyBus

## Przegląd

TrackMyBus to aplikacja do śledzenia autobusów w czasie rzeczywistym, zaprojektowana, aby dostarczać użytkownikom aktualnych informacji o lokalizacjach i liniach autobusowych w Warszawie. Projekt został stworzony przez grupę CW10 w ramach zajęć "Studium przypadku - programowanie w grupie programistycznej" na kierunku Informatyka.

Backend został zbudowany z wykorzystaniem FastAPI oraz wykorzystuje Redis do cachowania danych o lokalizacji autobusów, pobieranych z API Warszawskiego Transportu Publicznego. Frontend został opracowany przy użyciu Reacta z TypeScript, oferując responsywne i interaktywne doświadczenie użytkownika.

Dostępna jest także prezentacja PowerPoint. TrackMyBus10-Prezentacja.pptx

## Wymagania wstępne

Przed uruchomieniem aplikacji upewnij się, że masz zainstalowane następujące składniki:

- Python 3.8+
- FastAPI
- Serwer Redis
lub
- Docker
- Docker-compose
oraz
- Node.js i npm (dla frontendu)

## Konfiguracja

Instrukcje dotyczące konfiguracji i uruchomienia aplikacji znajdują się w pliku setup.md

## Testowanie

Testy dla modułu `api_receiver` zostały napisane z wykorzystaniem biblioteki `unittest` oraz `unittest.mock` do symulacji odpowiedzi z zewnętrznego API. Testy sprawdzają różne scenariusze, w tym poprawne odbieranie danych, obsługę błędów oraz przypadki braku danych.

Aby uruchomić testy, wykonaj poniższą komendę w katalogu głównym aplikacji:

```bash
python -m unittest discover -s tests
```

## Funkcjonalności

- **Aktualizacje w czasie rzeczywistym**: Lokalizacje autobusów są aktualizowane co 10 sekund, aby zapewnić najbardziej aktualne informacje.
- **Obliczenia odległości**: Użytkownicy mogą znaleźć autobusy w określonej odległości od swojej lokalizacji, używając formuły Haversine.
- **Interaktywna mapa**: Frontend w React pokazuje lokalizacje autobusów na interaktywnej mapie, co ułatwia wizualizację tras.

## Punkty końcowe API

- `/get_locations_line/{bus_line}`: Pobierz wszystkie lokalizacje autobusów dla określonej linii.
- `/get_locations/`: Pobierz autobusy w określonym zasięgu od lokalizacji użytkownika.
- `/get_all_data`: Pobierz wszystkie dane z cache, użyteczne do debugowania i administracji.

## Rozwój

Projekt wykorzystuje FastAPI na backendzie, co oferuje wysoką wydajność i łatwość obsługi asynchroniczności, oraz React z TypeScript na frontendzie, zapewniając solidne narzędzia do budowania interfejsów użytkownika.

