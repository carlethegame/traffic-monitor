"""
check_traffic.py

Chiama la TomTom Routing API per ottenere il tempo di percorrenza
REALE (con traffico) tra ORIGIN e DESTINATION, e appende una riga
al CSV di log.

Uso:
    python check_traffic.py

Richiede la variabile d'ambiente TOMTOM_API_KEY (locale: file .env,
su GitHub Actions: Secrets).
"""

import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

import config

# Carica .env solo in locale (su GitHub Actions la env var arriva già settata)
load_dotenv()

ITALY_TZ = ZoneInfo("Europe/Rome")


def get_api_key() -> str:
    key = os.environ.get("TOMTOM_API_KEY")
    if not key:
        print("ERRORE: variabile TOMTOM_API_KEY non trovata. "
              "Controlla il file .env (locale) o i Secrets (GitHub Actions).")
        sys.exit(1)
    return key


def fetch_travel_time() -> dict:
    """Chiama TomTom e restituisce i dati di interesse."""
    url = config.TOMTOM_ROUTING_URL.format(
        origin_lat=config.ORIGIN["lat"],
        origin_lon=config.ORIGIN["lon"],
        dest_lat=config.DESTINATION["lat"],
        dest_lon=config.DESTINATION["lon"],
    )

    params = {
        "key": get_api_key(),
        "traffic": "true",   # tempo REALE con traffico attuale
        "travelMode": "car",
    }

    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    route = data["routes"][0]["summary"]

    travel_time_sec = route["travelTimeInSeconds"]
    length_m = route["lengthInMeters"]
    traffic_delay_sec = route.get("trafficDelayInSeconds", None)

    return {
        "travel_time_sec": travel_time_sec,
        "travel_time_min": round(travel_time_sec / 60, 1),
        "length_km": round(length_m / 1000, 2),
        "traffic_delay_sec": traffic_delay_sec,
    }


def append_to_csv(row: dict) -> None:
    csv_path = Path(config.CSV_PATH)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = csv_path.exists()

    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def main():
    now_utc = datetime.now(timezone.utc)
    now_it = now_utc.astimezone(ITALY_TZ)

    try:
        result = fetch_travel_time()
    except requests.exceptions.RequestException as e:
        print(f"ERRORE chiamata TomTom API: {e}")
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"ERRORE parsing risposta TomTom: {e}")
        sys.exit(1)

    row = {
        "data": now_it.strftime("%Y-%m-%d"),
        "ora": now_it.strftime("%H:%M"),
        "giorno_settimana": now_it.strftime("%A"),
        "tempo_percorrenza_min": result["travel_time_min"],
        "tempo_percorrenza_sec": result["travel_time_sec"],
        "ritardo_traffico_sec": result["traffic_delay_sec"],
        "distanza_km": result["length_km"],
    }

    append_to_csv(row)
    print(f"OK — {row['data']} {row['ora']} — "
          f"{row['tempo_percorrenza_min']} min "
          f"(ritardo traffico: {row['ritardo_traffico_sec']} sec)")


if __name__ == "__main__":
    main()
