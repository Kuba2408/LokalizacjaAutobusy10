# Setup
## Wymagania Wstępne
Aby uruchomić projekt, potrzebujesz następujących narzędzi:

### Docker:

- Docker pozwala na konteneryzację aplikacji, co ułatwia ich wdrożenie i zarządzanie. Docker możesz pobrać i zainstalować ze strony Docker Desktop. Upewnij się, że Docker jest uruchomiony na Twoim komputerze po zainstalowaniu.

### Docker Compose:

- Docker Compose jest narzędziem do definicji i uruchamiania aplikacji wielokontenerowych. Jest instalowany razem z Docker Desktop na Windows i Mac, ale na niektórych dystrybucjach Linuxa może wymagać oddzielnej instalacji. Instrukcje znajdziesz na stronie Docker Compose.

## Pobieranie Projektu
Skopiuj repozytorium projektu na swoją maszynę lokalną. Możesz to zrobić za pomocą Git, jeśli projekt jest przechowywany w repozytorium git:

```
git clone https://github.com/Kuba2408/TrackMyBus10.git
cd <nazwa folderu projektu>
```

## Budowanie i Uruchamianie Aplikacji
Aby zbudować i uruchomić aplikację, użyj Docker Compose w miejscu w którym znajduje się plik yaml:


```
docker-compose up --build
```
To polecenie zbuduje obrazy Docker, jeśli nie zostały jeszcze zbudowane, i uruchomi kontenery zdefiniowane w pliku docker-compose.yml. Flagę --build można pominąć, jeśli obrazy zostały już wcześniej zbudowane i nie wymagają ponownego budowania.

## Dostęp do Aplikacji
- Frontend: Aplikacja frontendowa będzie dostępna w przeglądarce pod adresem http://localhost:3000 lub innym porcie zdefiniowanym w pliku konfiguracyjnym Docker Compose.

- Backend/API: Podobnie, backend/API, a konkretnie dokumentacja Swagger UI będzie dostępna pod adresem http://localhost:8080/docs lub innym porcie/ścieżce zdefiniowanej w konfiguracji.

## Kiedy skończysz:
Jeśli chcesz zatrzymać i posprzątać po sobie (usuwanie kontenerów, sieci itp.), wystarczy wpisać:

```
docker-compose down
```

