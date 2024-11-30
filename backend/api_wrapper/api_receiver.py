import warsaw_data_api


class ApiReceiver:
    def __init__(self, apikey):
        self.apikey = apikey

    def bus_location(self):
        ztm = warsaw_data_api.ztm(self.apikey)
        buses = ztm.get_buses_location()
        return buses