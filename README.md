This repository will be used for personal tracking of energy data from Amber API.

Amber is an Australian-based electricity retailer that pass through the real-time wholesale price of energy.
Because of Amber's wholesale power prices, you can save hundreds of dollars a year by automating high power devices like air-conditioners, heat pumps and pool pumps.

The main usage for the utils will be to keep track of energy usage as Amber data is only available for 90 days via the API. So, in order to keep a historical record of all my usage while a customer, this pipeline will fetch data everyday and save into a PostgreSQL database hosted in a local server.

In order to practive FrontEnd Skills, this data will eventually be fed into a Website where I can show some stats of my usage.

This is a WIP pipeline where I intend to implement catchup methods when let's say fetching data fails for some reason.

If you're interested in getting to know more about Amber, please check their website here:

https://www.amber.com.au/

And their API Documentation:

https://app.amber.com.au/swagger.json

Library used:
https://github.com/madpilot/amberelectric.py
