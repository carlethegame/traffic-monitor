# Traffic Monitor

Monitora il tempo di percorrenza (con traffico reale) su una tratta fissa,
lun-ven, ogni 15 minuti dalle 6:45 alle 8:30, e logga i dati su CSV.

## Setup locale (VS Code)

1. Crea un ambiente virtuale e installa le dipendenze:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
2. Copia `.env.example` in `.env` e incolla la tua TomTom API key
   (registrati su https://developer.tomtom.com se non l'hai ancora fatto).
3. Test manuale:
   ```
   python check_traffic.py
   ```
   Se funziona, vedrai una riga stampata e una nuova riga in `data/traffic_log.csv`.

## Setup GitHub Actions (per farlo girare senza PC acceso)

1. Crea un repo su GitHub e carica questa cartella (`.env` NON va caricato,
   è già escluso da `.gitignore`).
2. Vai su Settings → Secrets and variables → Actions → New repository secret.
   Nome: `TOMTOM_API_KEY`, valore: la tua chiave TomTom.
3. Il workflow in `.github/workflows/traffic-check.yml` partirà da solo
   secondo gli orari configurati. Puoi anche lanciarlo a mano dalla tab
   "Actions" del repo (pulsante "Run workflow").
4. Ogni esecuzione aggiunge una riga a `data/traffic_log.csv` e fa commit
   automatico nel repo.

## Nota importante sugli orari (cambio ora legale/solare)

GitHub Actions usa cron in **UTC fisso**: non sa che l'Italia cambia ora
due volte l'anno. Ho messo *sei* espressioni cron nel workflow — tre
calcolate per l'ora solare (CET, UTC+1, ottobre-marzo) e tre per l'ora
legale (CEST, UTC+2, marzo-ottobre). Il risultato pratico: per metà
dell'anno alcune di queste sei si sovrappongono/sono inutili e vengono
comunque eseguite, quindi **nei giorni intorno al cambio ora avrai o un
buco di un'ora, o rilevazioni doppie** finché non modifichi manualmente
il file YAML togliendo il blocco non più valido. Non è automatizzabile
in modo pulito senza uno script che calcoli il cron dinamicamente — se
ti interessa lo aggiungiamo dopo, ma è un'ottimizzazione successiva, non
bloccante per partire.

## Limite di precisione GitHub Actions

I cron di GitHub non sono garantiti al minuto esatto: soprattutto nei
minuti "tondi" molto trafficati (es. ore 7:00, 7:15...) l'esecuzione può
partire con qualche minuto di ritardo. Per un monitoraggio di tendenza va
bene; se ti serve precisione al minuto, questa non è l'architettura giusta.
