from app import create_app
from app.models import db, Customer, Vehicle
import unittest


class TestVehicles(unittest.TestCase):
    """Comprehensive test suite for Vehicles endpoints"""
    
    def setUp(self):
        """Initialize test client and database"""
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
        
        # Create a test customer for vehicle creation
        customer_payload = {
            "name": "Test Customer",
            "email": "testcustomer@email.com",
            "phone": "555-1234567",
            "address": "123 Test St",
            "password": "password123"
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.customer_id = response.json['customer']['customer_id']
    
    # CREATE TESTS
    def test_create_vehicle_success(self):
        """Test successfully creating a new vehicle"""
        vehicle_payload = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "12345678901234567"
        }
        response = self.client.post('/vehicles/', json=vehicle_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Vehicle created successfully')
        self.assertEqual(response.json['vehicle']['make'], 'Toyota')
    
    def test_create_vehicle_missing_customer(self):
        """Test creating a vehicle with non-existent customer"""
        vehicle_payload = {
            "customer_id": 99999,
            "make": "Honda",
            "model": "Accord",
            "year": 2021,
            "vin": "98765432109876543"
        }
        response = self.client.post('/vehicles/', json=vehicle_payload)
        self.assertEqual(response.status_code, 404)
    
    def test_create_vehicle_missing_required_fields(self):
        """Test creating a vehicle with missing required fields"""
        vehicle_payload = {
            "customer_id": self.customer_id,
            "make": "Ford"
        }
        response = self.client.post('/vehicles/', json=vehicle_payload)
        self.assertEqual(response.status_code, 400)
    
    def test_create_vehicle_duplicate_vin(self):
        """Test creating a vehicle with duplicate VIN"""
        vehicle_payload_1 = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "11111111111111111"
        }
        self.client.post('/vehicles/', json=vehicle_payload_1)
        
        vehicle_payload_2 = {
            "customer_id": self.customer_id,
            "make": "Honda",
            "model": "Accord",
            "year": 2021,
            "vin": "11111111111111111"
        }
        response = self.client.post('/vehicles/', json=vehicle_payload_2)
        self.assertEqual(response.status_code, 400)
    
    # READ TESTS
    def test_get_all_vehicles(self):
        """Test retrieving all vehicles"""
        for i in range(3):
            vehicle_payload = {
                "customer_id": self.customer_id,
                "make": f"Make{i}",
                "model": f"Model{i}",
                "year": 2020 + i,
                "vin": f"{10000000000000000 + i}"
            }
            self.client.post('/vehicles/', json=vehicle_payload)
        
        response = self.client.get('/vehicles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['count'], 3)
    
    def test_get_vehicles_empty(self):
        """Test retrieving vehicles when none exist"""
        response = self.client.get('/vehicles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['count'], 0)
    
    def test_get_single_vehicle(self):
        """Test retrieving a specific vehicle by ID"""
        vehicle_payload = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "12345678901234567"
        }
        create_response = self.client.post('/vehicles/', json=vehicle_payload)
        vehicle_id = create_response.json['vehicle']['vehicle_id']
        
        response = self.client.get(f'/vehicles/{vehicle_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['vehicle']['vehicle_id'], vehicle_id)
        self.assertEqual(response.json['vehicle']['make'], 'Toyota')
    
    def test_get_single_vehicle_not_found(self):
        """Test retrieving a non-existent vehicle"""
        response = self.client.get('/vehicles/99999')
        self.assertEqual(response.status_code, 404)
    
    def test_get_customer_vehicles(self):
        """Test retrieving all vehicles for a specific customer"""
        for i in range(3):
            vehicle_payload = {
                "customer_id": self.customer_id,
                "make": f"Make{i}",
                "model": f"Model{i}",
                "year": 2020 + i,
                "vin": f"{20000000000000000 + i}"
            }
            self.client.post('/vehicles/', json=vehicle_payload)
        
        response = self.client.get(f'/vehicles/customer/{self.customer_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['count'], 3)
    
    def test_get_customer_vehicles_nonexistent_customer(self):
        """Test retrieving vehicles for a non-existent customer"""
        response = self.client.get('/vehicles/customer/99999')
        self.assertEqual(response.status_code, 404)
    
    # UPDATE TESTS
    def test_update_vehicle_all_fields(self):
        """Test updating all fields of a vehicle"""
        vehicle_payload = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "12345678901234567"
        }
        create_response = self.client.post('/vehicles/', json=vehicle_payload)
        vehicle_id = create_response.json['vehicle']['vehicle_id']
        
        update_payload = {
            "make": "Honda",
            "model": "Accord",
            "year": 2021,
            "vin": "98765432109876543"
        }
        response = self.client.put(f'/vehicles/{vehicle_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['vehicle']['make'], 'Honda')
    
    def test_update_vehicle_partial_fields(self):
        """Test updating only some fields of a vehicle"""
        vehicle_payload = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "12345678901234567"
        }
        create_response = self.client.post('/vehicles/', json=vehicle_payload)
        vehicle_id = create_response.json['vehicle']['vehicle_id']
        
        update_payload = {"make": "Honda"}
        response = self.client.put(f'/vehicles/{vehicle_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['vehicle']['make'], 'Honda')
        self.assertEqual(response.json['vehicle']['model'], 'Camry')
    
    def test_update_vehicle_not_found(self):
        """Test updating a non-existent vehicle"""
        update_payload = {"make": "Ford"}
        response = self.client.put('/vehicles/99999', json=update_payload)
        self.assertEqual(response.status_code, 404)
    
    def test_update_vehicle_duplicate_vin(self):
        """Test updating a vehicle with a VIN that already exists"""
        vehicle1 = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "11111111111111111"
        }
        response1 = self.client.post('/vehicles/', json=vehicle1)
        vehicle_id_1 = response1.json['vehicle']['vehicle_id']
        
        vehicle2 = {
            "customer_id": self.customer_id,
            "make": "Honda",
            "model": "Accord",
            "year": 2021,
            "vin": "22222222222222222"
        }
        response2 = self.client.post('/vehicles/', json=vehicle2)
        vehicle_id_2 = response2.json['vehicle']['vehicle_id']
        
        update_payload = {"vin": "11111111111111111"}
        response = self.client.put(f'/vehicles/{vehicle_id_2}', json=update_payload)
        self.assertEqual(response.status_code, 400)
    
    # DELETE TESTS
    def test_delete_vehicle(self):
        """Test successfully deleting a vehicle"""
        vehicle_payload = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "12345678901234567"
        }
        create_response = self.client.post('/vehicles/', json=vehicle_payload)
        vehicle_id = create_response.json['vehicle']['vehicle_id']
        
        response = self.client.delete(f'/vehicles/{vehicle_id}')
        self.assertEqual(response.status_code, 200)
        
        get_response = self.client.get(f'/vehicles/{vehicle_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_vehicle_not_found(self):
        """Test deleting a non-existent vehicle"""
        response = self.client.delete('/vehicles/99999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
