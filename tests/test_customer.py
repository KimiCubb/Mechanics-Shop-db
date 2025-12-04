from app import create_app
from app.models import db
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
            
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "555-1234567",
            "address": "123 Main St, City, State",
            "password": "secure123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['customer']['name'], "John Doe")

    def test_login_customer(self):
        # First, create a customer
        customer_payload = {
            "name": "Test User",
            "email": "test@email.com",
            "phone": "555-9876543",
            "address": "456 Oak Ave",
            "password": "test123"
        }
        self.client.post('/customers/', json=customer_payload)

        # Then test login with correct credentials
        credentials = {
            "email": "test@email.com",
            "password": "test123"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('auth_token', response.json)
        self.auth_token = response.json['auth_token']

    def test_update_customer(self):
        # First, create and login a customer to get customer_id
        customer_payload = {
            "name": "Test User",
            "email": "update@email.com",
            "phone": "555-5555555",
            "address": "789 Update St",
            "password": "update123"
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['customer']['customer_id']

        # Login to get auth token
        credentials = {
            "email": "update@email.com",
            "password": "update123"
        }
        login_response = self.client.post('/customers/login', json=credentials)
        auth_token = login_response.json['auth_token']

        # Update customer with partial data
        update_payload = {
            "name": "Peter",
            "phone": "555-1111111"
        }

        headers = {'Authorization': "Bearer " + auth_token}

        response = self.client.put(f'/customers/{customer_id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customer']['name'], 'Peter')
        self.assertEqual(response.json['customer']['email'], 'update@email.com')

    def test_get_all_customers(self):
        """Test retrieving all customers with pagination"""
        # Create multiple customers
        for i in range(3):
            customer_payload = {
                "name": f"Customer {i}",
                "email": f"customer{i}@email.com",
                "phone": f"555-{1000000 + i}",
                "address": f"{i} Test St",
                "password": "password123"
            }
            self.client.post('/customers/', json=customer_payload)

        # Get all customers
        response = self.client.get('/customers/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['page'], 1)
        self.assertEqual(response.json['per_page'], 10)
        self.assertGreaterEqual(len(response.json['customers']), 3)

    def test_get_single_customer(self):
        """Test retrieving a specific customer by ID"""
        # Create a customer
        customer_payload = {
            "name": "Single Customer",
            "email": "single@email.com",
            "phone": "555-9999999",
            "address": "999 Single St",
            "password": "password123"
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['customer']['customer_id']

        # Get the specific customer
        response = self.client.get(f'/customers/{customer_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customer']['name'], "Single Customer")
        self.assertEqual(response.json['customer']['email'], "single@email.com")

    def test_get_customer_not_found(self):
        """Test retrieving a customer that doesn't exist"""
        response = self.client.get('/customers/99999')
        self.assertEqual(response.status_code, 404)

    def test_create_customer_invalid_email(self):
        """Test creating a customer with invalid email"""
        customer_payload = {
            "name": "Invalid Email",
            "email": "not-an-email",
            "phone": "555-1234567",
            "address": "123 Invalid St",
            "password": "password123"
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)

    def test_create_customer_duplicate_email(self):
        """Test creating a customer with duplicate email"""
        customer_payload = {
            "name": "First Customer",
            "email": "duplicate@email.com",
            "phone": "555-1234567",
            "address": "123 Main St",
            "password": "password123"
        }
        # Create first customer
        self.client.post('/customers/', json=customer_payload)

        # Try to create second customer with same email
        customer_payload['name'] = "Second Customer"
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)

    def test_login_customer_invalid_password(self):
        """Test login with invalid password"""
        # Create a customer
        customer_payload = {
            "name": "Login Test",
            "email": "logintest@email.com",
            "phone": "555-1234567",
            "address": "123 Login St",
            "password": "correct_password"
        }
        self.client.post('/customers/', json=customer_payload)

        # Try login with wrong password
        credentials = {
            "email": "logintest@email.com",
            "password": "wrong_password"
        }
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)

    def test_login_customer_nonexistent(self):
        """Test login with non-existent email"""
        credentials = {
            "email": "nonexistent@email.com",
            "password": "password123"
        }
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)

    def test_delete_customer(self):
        """Test deleting a customer"""
        # Create a customer
        customer_payload = {
            "name": "Delete Test",
            "email": "delete@email.com",
            "phone": "555-1234567",
            "address": "123 Delete St",
            "password": "password123"
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['customer']['customer_id']

        # Login to get auth token
        credentials = {
            "email": "delete@email.com",
            "password": "password123"
        }
        login_response = self.client.post('/customers/login', json=credentials)
        auth_token = login_response.json['auth_token']

        # Delete the customer
        headers = {'Authorization': f"Bearer {auth_token}"}
        response = self.client.delete(f'/customers/{customer_id}', headers=headers)
        self.assertEqual(response.status_code, 200)

        # Verify customer is deleted
        get_response = self.client.get(f'/customers/{customer_id}')
        self.assertEqual(get_response.status_code, 404)

    def test_delete_customer_unauthorized(self):
        """Test deleting another customer (should fail)"""
        # Create two customers
        customer1_payload = {
            "name": "Customer 1",
            "email": "customer1@email.com",
            "phone": "555-1111111",
            "address": "111 Customer St",
            "password": "password123"
        }
        customer1_response = self.client.post('/customers/', json=customer1_payload)
        customer1_id = customer1_response.json['customer']['customer_id']

        customer2_payload = {
            "name": "Customer 2",
            "email": "customer2@email.com",
            "phone": "555-2222222",
            "address": "222 Customer St",
            "password": "password123"
        }
        customer2_response = self.client.post('/customers/', json=customer2_payload)
        customer2_id = customer2_response.json['customer']['customer_id']

        # Login as customer 2
        credentials = {
            "email": "customer2@email.com",
            "password": "password123"
        }
        login_response = self.client.post('/customers/login', json=credentials)
        auth_token = login_response.json['auth_token']

        # Try to delete customer 1 (should fail - unauthorized)
        headers = {'Authorization': f"Bearer {auth_token}"}
        response = self.client.delete(f'/customers/{customer1_id}', headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_update_customer_unauthorized(self):
        """Test updating another customer (should fail)"""
        # Create two customers
        customer1_payload = {
            "name": "Customer 1",
            "email": "cust1@email.com",
            "phone": "555-1111111",
            "address": "111 Cust St",
            "password": "password123"
        }
        customer1_response = self.client.post('/customers/', json=customer1_payload)
        customer1_id = customer1_response.json['customer']['customer_id']

        customer2_payload = {
            "name": "Customer 2",
            "email": "cust2@email.com",
            "phone": "555-2222222",
            "address": "222 Cust St",
            "password": "password123"
        }
        self.client.post('/customers/', json=customer2_payload)

        # Login as customer 2
        credentials = {
            "email": "cust2@email.com",
            "password": "password123"
        }
        login_response = self.client.post('/customers/login', json=credentials)
        auth_token = login_response.json['auth_token']

        # Try to update customer 1 (should fail - unauthorized)
        update_payload = {"name": "Hacked Customer"}
        headers = {'Authorization': f"Bearer {auth_token}"}
        response = self.client.put(f'/customers/{customer1_id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_update_customer_missing_token(self):
        """Test updating customer without authentication token"""
        # Create a customer
        customer_payload = {
            "name": "No Token Test",
            "email": "notoken@email.com",
            "phone": "555-1234567",
            "address": "123 NoToken St",
            "password": "password123"
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['customer']['customer_id']

        # Try to update without token
        update_payload = {"name": "Updated Name"}
        response = self.client.put(f'/customers/{customer_id}', json=update_payload)
        self.assertEqual(response.status_code, 401)

    def test_get_my_tickets(self):
        """Test retrieving authenticated customer's service tickets"""
        # Create a customer
        customer_payload = {
            "name": "Ticket Owner",
            "email": "ticketowner@email.com",
            "phone": "555-1234567",
            "address": "123 Ticket St",
            "password": "password123"
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['customer']['customer_id']

        # Login to get auth token
        credentials = {
            "email": "ticketowner@email.com",
            "password": "password123"
        }
        login_response = self.client.post('/customers/login', json=credentials)
        auth_token = login_response.json['auth_token']

        # Get my tickets
        headers = {'Authorization': f"Bearer {auth_token}"}
        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customer_id'], customer_id)
        self.assertIn('service_tickets', response.json)

    def test_get_my_tickets_unauthorized(self):
        """Test retrieving service tickets without authentication"""
        response = self.client.get('/customers/my-tickets')
        self.assertEqual(response.status_code, 401)

    def test_create_customer_missing_required_fields(self):
        """Test creating customer with missing required fields"""
        # Missing password
        customer_payload = {
            "name": "Incomplete",
            "email": "incomplete@email.com",
            "phone": "555-1234567",
            "address": "123 Incomplete St"
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)

    def test_create_customer_short_password(self):
        """Test creating customer with password too short"""
        customer_payload = {
            "name": "Short Pass",
            "email": "shortpass@email.com",
            "phone": "555-1234567",
            "address": "123 Short St",
            "password": "short"  # Less than 6 characters
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()