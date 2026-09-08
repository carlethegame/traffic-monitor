# config.py
# Configurazione della tratta e degli orari di monitoraggio

# Coordinate di partenza e arrivo (lat, lon)
ORIGIN = {"lat": 45.771857, "lon": 9.287788}
DESTINATION = {"lat": 45.594825, "lon": 9.243242}

# Nomi descrittivi (solo per il CSV, comodi da leggere)
ORIGIN_LABEL = "Partenza"
DESTINATION_LABEL = "Arrivo"

# File di output
CSV_PATH = "data/traffic_log.csv"

# TomTom Routing API
TOMTOM_ROUTING_URL = (
    "https://api.tomtom.com/routing/1/calculateRoute/"
    "{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json"
)
