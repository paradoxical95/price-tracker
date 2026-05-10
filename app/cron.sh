#!/bin/bash
# Runs scrape every 6 hours, Flask runs always
python app.py &
while true; do
	sleep 21600
	python -c "import app; app.scrape_prices()"
done
