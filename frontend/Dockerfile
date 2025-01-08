# Użyj oficjalnego obrazu Node.js jako obrazu bazowego
FROM node:22

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Kopiuj pliki package.json i package-lock.json (jeśli istnieje)
COPY package*.json ./

# Zainstaluj zależności projektu
RUN npm install --legacy-peer-deps

# Kopiuj resztę kodu do katalogu roboczego
COPY . .

# Uruchom aplikację React
CMD ["npm", "run", "dev"]