import unittest
from unittest.mock import patch, MagicMock
from api_wrapper.api_receiver import ApiReceiver

class TestApiReceiver(unittest.TestCase):
    def setUp(self):
        self.apikey = "test_apikey"
        self.api_receiver = ApiReceiver(self.apikey)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_success(self, mock_ztm):
        # Mock preparation
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": 1, "line": "123", "latitude": 52.2296756, "longitude": 21.0122287},
            {"id": 2, "line": "456", "latitude": 52.2296756, "longitude": 21.0122287},
        ]
        mock_ztm.return_value = mock_ztm_instance

        # Call the tested method
        buses = self.api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses), 2)
        self.assertEqual(buses[0]["line"], "123")
        self.assertEqual(buses[1]["id"], 2)

        # Check if the method was called
        mock_ztm.assert_called_once_with(self.apikey)
        mock_ztm_instance.get_buses_location.assert_called_once()

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_empty(self, mock_ztm):
        # Mock preparation
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = []
        mock_ztm.return_value = mock_ztm_instance

        # Call the tested method
        buses = self.api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses), 0)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_exception(self, mock_ztm):
        # Mock preparation
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.side_effect = Exception("API error")
        mock_ztm.return_value = mock_ztm_instance

        # Call the tested method and check for the exception
        with self.assertRaises(Exception) as context:
            self.api_receiver.bus_location()
        self.assertEqual(str(context.exception), "API error")

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_invalid_data(self, mock_ztm):
        # Mock preparation: invalid data format (missing required fields)
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": 1, "line": "123", "latitude": 52.2296756},  # Missing longitude
            {"id": 2, "line": "456", "longitude": 21.0122287},  # Missing latitude
        ]
        mock_ztm.return_value = mock_ztm_instance

        # Call the tested method
        buses = self.api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses), 2)
        # Ensure that the data is not malformed and is still returned even if incomplete
        self.assertTrue("latitude" in buses[0] or "longitude" in buses[0])

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_large_data(self, mock_ztm):
        # Mock preparation: large dataset
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": i, "line": str(i), "latitude": 52.2296756, "longitude": 21.0122287} for i in range(1, 1001)
        ]
        mock_ztm.return_value = mock_ztm_instance

        # Call the tested method
        buses = self.api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses), 1000)
        self.assertEqual(buses[999]["id"], 1000)  # Check the last bus

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_no_buses(self, mock_ztm):
        # Mock preparation: No buses at all (empty response)
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = []
        mock_ztm.return_value = mock_ztm_instance

        # Call the tested method
        buses = self.api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses), 0)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_multiple_calls(self, mock_ztm):
        # Mock preparation: same buses on multiple calls
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": 1, "line": "123", "latitude": 52.2296756, "longitude": 21.0122287},
            {"id": 2, "line": "456", "latitude": 52.2296756, "longitude": 21.0122287},
        ]
        mock_ztm.return_value = mock_ztm_instance

        # First call
        buses_1 = self.api_receiver.bus_location()

        # Second call
        buses_2 = self.api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses_1), 2)
        self.assertEqual(len(buses_2), 2)
        self.assertEqual(buses_1, buses_2)  # Ensure the result is the same for both calls
        
        # Correct assertion for number of calls
        self.assertEqual(mock_ztm_instance.get_buses_location.call_count, 2)
    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_success(self, mock_ztm):
        # Mock preparation: same buses on multiple calls
        mock_ztm_instance = MagicMock()
        mock_ztm.return_value = mock_ztm_instance
        mock_ztm_instance.get_buses_location.return_value = [{'bus_id': 1}, {'bus_id': 2}]
        
        api_receiver = ApiReceiver('fake_apikey')
        
        with self.assertLogs('api_wrapper.api_receiver', level='INFO') as log:  # Poprawienie loggera
            buses = api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses), 2)
        self.assertEqual(buses, [{'bus_id': 1}, {'bus_id': 2}])

        # Sprawdzenie, czy logowanie miało miejsce (porównanie pełnej treści logu)
        self.assertIn('INFO:api_wrapper.api_receiver:Successfully retrieved bus locations: 2 buses found', log.output)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_no_buses(self, mock_ztm):
        # Mock preparation: same buses on multiple calls
        mock_ztm_instance = MagicMock()
        mock_ztm.return_value = mock_ztm_instance
        mock_ztm_instance.get_buses_location.return_value = []  # Brak busów
        
        # Stworzenie instancji ApiReceiver
        api_receiver = ApiReceiver('fake_apikey')
        
        # Testowanie metody bus_location
        with self.assertLogs('api_wrapper.api_receiver', level='INFO') as log:  # Poprawienie loggera
            buses = api_receiver.bus_location()

        # Assertions
        self.assertEqual(len(buses), 0)
        self.assertEqual(buses, [])

        self.assertIn('INFO:api_wrapper.api_receiver:Successfully retrieved bus locations: 0 buses found', log.output)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_failure(self, mock_ztm):
        # Mock preparation: same buses on multiple calls
        mock_ztm_instance = MagicMock()
        mock_ztm.return_value = mock_ztm_instance
        mock_ztm_instance.get_buses_location.side_effect = Exception('API error')  # Symulacja błędu
        
        api_receiver = ApiReceiver('fake_apikey')
        
        with self.assertLogs('api_wrapper.api_receiver', level='ERROR') as log:  # Poprawienie loggera
            with self.assertRaises(Exception):  # Używamy assertRaises do przechwycenia wyjątku
                api_receiver.bus_location()

        # Assertions
        self.assertIn('ERROR:api_wrapper.api_receiver:Failed to fetch bus locations: API error', log.output)

if __name__ == "__main__":
    unittest.main()