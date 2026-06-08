FROM node:20-alpine

WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm install

# Copiar el resto del código
COPY . .

# Iniciar Vite en modo desarrollo
CMD ["npm", "run", "dev", "--", "--host"]
