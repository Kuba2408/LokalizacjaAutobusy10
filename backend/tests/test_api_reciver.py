#komenda do uruchamiania testow: python -m unittest discover -s tests

import unittest
from unittest.mock import patch, MagicMock
from api_wrapper.api_receiver import ApiReceiver

class TestApiReceiver(unittest.TestCase):
    def setUp(self):
        # Ustawienie testowego klucza API i instancji ApiReceiver
        self.apikey = "test_apikey"
        self.api_receiver = ApiReceiver(self.apikey)
        print(f"\nRunning test: {self._testMethodName}")  # Logowanie nazwy testu

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_success(self, mock_ztm):
        # Testowanie poprawnego zwracania lokalizacji autobusow
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": 1, "line": "123", "latitude": 52.2296756, "longitude": 21.0122287},
            {"id": 2, "line": "456", "latitude": 52.2296756, "longitude": 21.0122287},
        ]
        mock_ztm.return_value = mock_ztm_instance

        buses = self.api_receiver.bus_location()

        self.assertEqual(len(buses), 2)
        self.assertEqual(buses[0]["line"], "123")
        self.assertEqual(buses[1]["id"], 2)

        mock_ztm.assert_called_once_with(self.apikey)
        mock_ztm_instance.get_buses_location.assert_called_once()

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_empty(self, mock_ztm):
        # Testowanie sytuacji, gdy API zwraca pusta liste autobusow
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = []
        mock_ztm.return_value = mock_ztm_instance

        buses = self.api_receiver.bus_location()

        self.assertEqual(len(buses), 0)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_exception(self, mock_ztm):
        # Testowanie obslugi wyjatku w przypadku bledu API
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.side_effect = Exception("API error")
        mock_ztm.return_value = mock_ztm_instance

        with self.assertRaises(Exception) as context:
            self.api_receiver.bus_location()
        self.assertEqual(str(context.exception), "API error")

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_invalid_data(self, mock_ztm):
        # Testowanie obslugi nieprawidlowych danych
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": 1, "line": "123", "latitude": 52.2296756},
            {"id": 2, "line": "456", "longitude": 21.0122287},
        ]
        mock_ztm.return_value = mock_ztm_instance

        buses = self.api_receiver.bus_location()

        self.assertEqual(len(buses), 2)
        self.assertTrue("latitude" in buses[0] or "longitude" in buses[0])

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_large_data(self, mock_ztm):
        # Testowanie dzialania na duzej liczbie danych
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": i, "line": str(i), "latitude": 52.2296756, "longitude": 21.0122287} for i in range(1, 1001)
        ]
        mock_ztm.return_value = mock_ztm_instance

        buses = self.api_receiver.bus_location()

        self.assertEqual(len(buses), 1000)
        self.assertEqual(buses[999]["id"], 1000)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_no_buses(self, mock_ztm):
        # Testowanie sytuacji, gdy nie ma autobusow
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = []
        mock_ztm.return_value = mock_ztm_instance

        buses = self.api_receiver.bus_location()

        self.assertEqual(len(buses), 0)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_multiple_calls(self, mock_ztm):
        # Testowanie wielokrotnego wywolania metody pobierajacej lokalizacje
        mock_ztm_instance = MagicMock()
        mock_ztm_instance.get_buses_location.return_value = [
            {"id": 1, "line": "123", "latitude": 52.2296756, "longitude": 21.0122287},
            {"id": 2, "line": "456", "latitude": 52.2296756, "longitude": 21.0122287},
        ]
        mock_ztm.return_value = mock_ztm_instance

        buses_1 = self.api_receiver.bus_location()
        buses_2 = self.api_receiver.bus_location()

        self.assertEqual(len(buses_1), 2)
        self.assertEqual(buses_1, buses_2)  
        self.assertEqual(mock_ztm_instance.get_buses_location.call_count, 2)

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_logging(self, mock_ztm):
        # Testowanie logowania informacji o powodzeniu
        mock_ztm_instance = MagicMock()
        mock_ztm.return_value = mock_ztm_instance
        mock_ztm_instance.get_buses_location.return_value = [{'bus_id': 1}, {'bus_id': 2}]
        
        api_receiver = ApiReceiver('fake_apikey')
        
        with self.assertLogs('api_wrapper.api_receiver', level='INFO') as log:
            buses = api_receiver.bus_location()

        self.assertEqual(len(buses), 2)
        self.assertIn('INFO:api_wrapper.api_receiver:Successfully retrieved bus locations: 2 buses found', log.output)
        print(f"{self._testMethodName}: Log output - {log.output}")

    @patch("api_wrapper.api_receiver.warsaw_data_api.ztm")
    def test_bus_location_failure_logging(self, mock_ztm):
        # Test sprawdza logowanie bledu podczas niepowodzenia w pobieraniu lokalizacji autobusow
        mock_ztm_instance = MagicMock()
        mock_ztm.return_value = mock_ztm_instance
        mock_ztm_instance.get_buses_location.side_effect = Exception('API error')
        
        api_receiver = ApiReceiver('fake_apikey')
        
        with self.assertLogs('api_wrapper.api_receiver', level='ERROR') as log:
            with self.assertRaises(Exception):
                api_receiver.bus_location()

        self.assertIn('ERROR:api_wrapper.api_receiver:Failed to fetch bus locations: API error', log.output)
        print(f"{self._testMethodName}: Log output - {log.output}")

if __name__ == "__main__":
    unittest.main()
