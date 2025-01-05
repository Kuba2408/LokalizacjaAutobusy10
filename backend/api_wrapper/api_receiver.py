import warsaw_data_api
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApiReceiver:
    def __init__(self, apikey):
        self.apikey = apikey
        self.logger = logging.getLogger(__name__)

    def bus_location(self):
        self.logger.info(f"Fetching bus locations using API key: {self.apikey}")
        try:
            ztm = warsaw_data_api.ztm(self.apikey)
            buses = ztm.get_buses_location()
            if buses:
                self.logger.info(f"Successfully retrieved bus locations: {len(buses)} buses found")
            else:
                self.logger.info(f"Successfully retrieved bus locations: 0 buses found")
            return buses
        except Exception as e:
            self.logger.error(f"Failed to fetch bus locations: {str(e)}")
            raise