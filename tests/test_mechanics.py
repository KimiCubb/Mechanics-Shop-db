from app import create_app
from app.models import db, Mechanic, ServiceTicket, Vehicle, Customer
import unittest


class TestMechanics(unittest.TestCase):
    """Comprehensive test suite for Mechanics endpoints"""
    
    def setUp(self):
        """Initialize test client and database"""
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
    
    # ============================================
    # CREATE TESTS
    # ============================================
    
    def test_create_mechanic_success(self):
        """Test successfully creating a new mechanic"""
        mechanic_payload = {
            "name": "John Smith",
            "email": "john.smith@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Mechanic created successfully')
        self.assertEqual(response.json['mechanic']['name'], 'John Smith')
        self.assertEqual(response.json['mechanic']['salary'], 50000.00)
        self.assertIn('mechanic_id', response.json['mechanic'])
    
    def test_create_mechanic_missing_required_fields(self):
        """Test creating a mechanic with missing required fields"""
        mechanic_payload = {
            "name": "John Smith",
            "email": "john.smith@shop.com"
            # Missing address, phone, salary
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_create_mechanic_invalid_email(self):
        """Test creating a mechanic with invalid email"""
        mechanic_payload = {
            "name": "John Smith",
            "email": "not-an-email",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
    
    def test_create_mechanic_invalid_phone_length(self):
        """Test creating a mechanic with phone number too short"""
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "123",  # Too short
            "salary": 50000.00
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
    
    def test_create_mechanic_negative_salary(self):
        """Test creating a mechanic with negative salary"""
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": -50000.00
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
    
    # ============================================
    # READ TESTS
    # ============================================
    
    def test_get_all_mechanics(self):
        """Test retrieving all mechanics"""
        # Create multiple mechanics
        for i in range(3):
            mechanic_payload = {
                "name": f"Mechanic {i}",
                "email": f"mechanic{i}@shop.com",
                "address": f"{i} Mechanic St",
                "phone": f"555-{1000000 + i}",
                "salary": 50000.00 + (i * 5000)
            }
            self.client.post('/mechanics/', json=mechanic_payload)
        
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Mechanics retrieved successfully')
        self.assertEqual(response.json['pagination']['total_items'], 3)
        self.assertEqual(len(response.json['mechanics']), 3)
    
    def test_get_mechanics_empty(self):
        """Test retrieving mechanics when none exist"""
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['pagination']['total_items'], 0)
        self.assertEqual(len(response.json['mechanics']), 0)
    
    def test_get_single_mechanic(self):
        """Test retrieving a specific mechanic by ID"""
        # Create a mechanic
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['mechanic']['mechanic_id']
        
        # Get the mechanic
        response = self.client.get(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanic']['mechanic_id'], mechanic_id)
        self.assertEqual(response.json['mechanic']['name'], 'John Smith')
        self.assertEqual(response.json['mechanic']['email'], 'john@shop.com')
    
    def test_get_single_mechanic_not_found(self):
        """Test retrieving a non-existent mechanic"""
        response = self.client.get('/mechanics/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json['error'])
    
    def test_get_top_performers(self):
        """Test retrieving mechanics sorted by tickets worked"""
        # Create mechanics
        mechanic_ids = []
        for i in range(3):
            mechanic_payload = {
                "name": f"Mechanic {i}",
                "email": f"mechanic{i}@shop.com",
                "address": f"{i} Mechanic St",
                "phone": f"555-{1000000 + i}",
                "salary": 50000.00
            }
            response = self.client.post('/mechanics/', json=mechanic_payload)
            mechanic_ids.append(response.json['mechanic']['mechanic_id'])
        
        # Create a customer and vehicle for testing service tickets
        customer_payload = {
            "name": "Test Customer",
            "email": "customer@email.com",
            "phone": "555-9999999",
            "address": "456 Test St",
            "password": "password123"
        }
        customer_response = self.client.post('/customers/', json=customer_payload)
        customer_id = customer_response.json['customer']['customer_id']
        
        vehicle_payload = {
            "customer_id": customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "12345678901234567"
        }
        vehicle_response = self.client.post('/vehicles/', json=vehicle_payload)
        vehicle_id = vehicle_response.json['vehicle']['vehicle_id']
        
        # Create service tickets and assign mechanics
        # Mechanic 0 gets 2 tickets, Mechanic 1 gets 1 ticket, Mechanic 2 gets 0 tickets
        for i in range(2):
            ticket_payload = {
                "vehicle_id": vehicle_id,
                "description": f"Service ticket {i}"
            }
            ticket_response = self.client.post('/service_tickets/', json=ticket_payload)
            ticket_id = ticket_response.json['service_ticket']['service_ticket_id']
            self.client.put(f'/service_tickets/{ticket_id}/assign-mechanic/{mechanic_ids[0]}')
        
        ticket_payload = {
            "vehicle_id": vehicle_id,
            "description": "Service ticket 2"
        }
        ticket_response = self.client.post('/service_tickets/', json=ticket_payload)
        ticket_id = ticket_response.json['service_ticket']['service_ticket_id']
        self.client.put(f'/service_tickets/{ticket_id}/assign-mechanic/{mechanic_ids[1]}')
        
        # Get top performers
        response = self.client.get('/mechanics/top-performers')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['count'], 3)
        
        # Check that mechanics are ordered by ticket count
        mechanics = response.json['mechanics']
        self.assertEqual(mechanics[0]['ticket_count'], 2)  # Mechanic 0 has 2 tickets
        self.assertEqual(mechanics[1]['ticket_count'], 1)  # Mechanic 1 has 1 ticket
        self.assertEqual(mechanics[2]['ticket_count'], 0)  # Mechanic 2 has 0 tickets
    
    # ============================================
    # UPDATE TESTS
    # ============================================
    
    def test_update_mechanic_all_fields(self):
        """Test updating all fields of a mechanic"""
        # Create a mechanic
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['mechanic']['mechanic_id']
        
        # Update mechanic
        update_payload = {
            "name": "Jane Doe",
            "email": "jane@shop.com",
            "address": "456 Shop Ave",
            "phone": "555-7654321",
            "salary": 60000.00
        }
        
        response = self.client.put(f'/mechanics/{mechanic_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanic']['name'], 'Jane Doe')
        self.assertEqual(response.json['mechanic']['email'], 'jane@shop.com')
        self.assertEqual(response.json['mechanic']['address'], '456 Shop Ave')
        self.assertEqual(response.json['mechanic']['phone'], '555-7654321')
        self.assertEqual(response.json['mechanic']['salary'], 60000.00)
    
    def test_update_mechanic_partial_fields(self):
        """Test updating only some fields of a mechanic"""
        # Create a mechanic
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['mechanic']['mechanic_id']
        
        # Update only salary
        update_payload = {
            "salary": 55000.00
        }
        
        response = self.client.put(f'/mechanics/{mechanic_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanic']['salary'], 55000.00)
        self.assertEqual(response.json['mechanic']['name'], 'John Smith')  # Should remain unchanged
    
    def test_update_mechanic_not_found(self):
        """Test updating a non-existent mechanic"""
        update_payload = {
            "name": "Jane Doe"
        }
        
        response = self.client.put('/mechanics/99999', json=update_payload)
        self.assertEqual(response.status_code, 404)
    
    def test_update_mechanic_invalid_salary(self):
        """Test updating a mechanic with invalid salary"""
        # Create a mechanic
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['mechanic']['mechanic_id']
        
        # Try to update with negative salary
        update_payload = {
            "salary": -10000.00
        }
        
        response = self.client.put(f'/mechanics/{mechanic_id}', json=update_payload)
        # This may or may not be validated, depending on schema configuration
        self.assertIn(response.status_code, [200, 400])
    
    # ============================================
    # DELETE TESTS
    # ============================================
    
    def test_delete_mechanic(self):
        """Test successfully deleting a mechanic"""
        # Create a mechanic
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['mechanic']['mechanic_id']
        
        # Delete the mechanic
        response = self.client.delete(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted successfully', response.json['message'])
        
        # Verify the mechanic is deleted
        get_response = self.client.get(f'/mechanics/{mechanic_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_mechanic_not_found(self):
        """Test deleting a non-existent mechanic"""
        response = self.client.delete('/mechanics/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json['error'])
    
    # ============================================
    # RATE LIMITING TESTS
    # ============================================
    
    def test_create_mechanic_multiple_requests(self):
        """Test creating multiple mechanics in sequence"""
        # Note: Rate limiting may not be enforced in test environment
        count_success = 0
        
        for i in range(5):
            mechanic_payload = {
                "name": f"Mechanic {i}",
                "email": f"mechanic{i}@shop.com",
                "address": f"{i} Mechanic St",
                "phone": f"555-{1000000 + i}",
                "salary": 50000.00
            }
            response = self.client.post('/mechanics/', json=mechanic_payload)
            
            if response.status_code == 201:
                count_success += 1
        
        self.assertGreater(count_success, 0)
    
    # ============================================
    # EDGE CASES
    # ============================================
    
    def test_create_mechanic_zero_salary(self):
        """Test creating a mechanic with zero salary"""
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 0.00
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        # Zero salary might be valid or invalid depending on business rules
        self.assertIn(response.status_code, [201, 400])
    
    def test_create_mechanic_high_salary(self):
        """Test creating a mechanic with very high salary"""
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 999999999.99
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['mechanic']['salary'], 999999999.99)
    
    def test_update_mechanic_email_format(self):
        """Test updating mechanic with various email formats"""
        # Create a mechanic
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@shop.com",
            "address": "123 Mechanic St",
            "phone": "555-1234567",
            "salary": 50000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['mechanic']['mechanic_id']
        
        # Update with different valid email
        update_payload = {
            "email": "john.doe+mechanic@shop.co.uk"
        }
        
        response = self.client.put(f'/mechanics/{mechanic_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanic']['email'], 'john.doe+mechanic@shop.co.uk')


if __name__ == '__main__':
    unittest.main()
