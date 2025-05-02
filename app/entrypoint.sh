#! /bin/bash

# Controllo delle variabili d'ambiente
if [ -z "$SPIDER_NAME" ]; then
  echo "Errore: devi impostare la variabile SPIDER_NAME."
  exit 1
fi

if [ -z "$SCRAPE_INTERVAL" ]; then
  echo "Errore: devi impostare la variabile SCRAPE_INTERVAL."
  exit 1
fi

# Esegui in loop infinito
while true
do
  echo "Avvio dello spider: $SPIDER_NAME"
  
  # Lancia lo spider
  scrapy crawl "$SPIDER_NAME"
  
  echo "Spider completato. Aspetto $SCRAPE_INTERVAL secondi..."
  sleep "$SCRAPE_INTERVAL"
done