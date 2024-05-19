#!/bin/sh

cd ~/python-projects/amber_alerts/
echo "Running Amber Alerts Pipeline"
pipenv run python amber_prices.py
echo "Pipeline execution complete."