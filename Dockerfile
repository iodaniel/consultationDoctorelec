# Dockerfile
FROM python:3.10

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos al contenedor
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación al contenedor
COPY . .

# Copiar wait-for-it script
COPY wait-for-it.sh /app/wait-for-it.sh

# Hacer el script ejecutable
RUN chmod +x /app/wait-for-it.sh

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["./wait-for-it.sh", "db:5433", "--", "flask", "run", "--host=0.0.0.0", "--port=5001"]
