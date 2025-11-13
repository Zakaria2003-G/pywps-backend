# ================================
#  IMAGE DE BASE AVEC GDAL / PROJ
# ================================
FROM osgeo/gdal:ubuntu-small-3.7.0

# Mettre à jour
RUN apt-get update -y && apt-get install -y \
    python3 python3-pip python3-dev \
    libgdal-dev gdal-bin \
    libproj-dev proj-data proj-bin \
    libgeos-dev \
    && apt-get clean

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copier tout le projet
COPY . /app/

# Donner les droits pour start.sh
RUN chmod +x start.sh

# Exposer le port WPS
EXPOSE 5000

# Commande de démarrage
CMD ["bash", "start.sh"]
