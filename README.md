The ```get_usage``` method returns a list with your usage summary for every 30 min interval.

This is a list of dictionaries, where each dictionary has the important keys:

channel_type: The type of channel E2 is controlled load, E1 is general load
cost: The total cost of your consumption or generation for this period - includes GST
date: The date of the usage summary
kwh: Number of kWh you consumed or generated. Generated numbers will be negative
per_kwh: Number of cents you will pay per kilowatt-hour (c/kWh) - includes GST
renewables: Percentage of renewables in the grid
spots_per_kwh: NEM spot price (c/kWh). This is the price generators get paid to generate electricity, and what drives the variable component of your perKwh price - includes GST
start_time: The start time of the usage summary in UTC Timezone
end_time: The end time of the usage summary in UTC Timezone
nem_time: The end time of the usage summary in NEM Timezone (UTC + 10)



