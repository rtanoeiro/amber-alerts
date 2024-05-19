cd ~/python-projects/amber_alerts/
echo "Running Amber Alerts Pipeline"
pipenv shell
echo "Updating Pipfile.lock"
pipenv update --outdated
python amber_prices.py
echo "Pipeline execution complete."