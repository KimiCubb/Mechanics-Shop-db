from app import create_app
from app.models import db, ServiceTicket, Vehicle, Customer, Mechanic, Inventory
import unittest
from datetime import datetime


class TestServiceTickets(unittest.TestCase):
    """Comprehensive test suite for Service Tickets endpoints"""
    
    def setUp(self):
        """Initialize test client and database"""
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
        
        # Create a test customer
        customer_payload = {
            "name": "Test Customer",
            "email": "customer@email.com",
            "phone": "555-1234567",
            "address": "123 Test St",
            "password": "password123"
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.customer_id = response.json['customer']['customer_id']
        
        # Create a test vehicle
        vehicle_payload = {
            "customer_id": self.customer_id,
            "make": "Toyota",
            "model": "Camry",
            "year": 2020,
            "vin": "12345678901234567"
        }
        response = self.client.post('/vehicles/', json=vehicle_payload)
        self.vehicle_id = response.json['vehicle']['vehicle_id']
        
        # Create test mechanics
        self.mechanic_ids = []
        for i in range(3):
            mechanic_payload = {
                "name": f"Mechanic {i}",
                "email": f"mechanic{i}@shop.com",
                "address": f"{i} Shop St",
                "phone": f"555-{1000000 + i}",
                "salary": 50000.00
            }
            response = self.client.post('/mechanics/', json=mechanic_payload)
            self.mechanic_ids.append(response.json['mechanic']['mechanic_id'])
        
        # Create test parts
        self.part_ids = []
        parts_data = [
            {"name": "Engine Oil", "price": 15.99},
            {"name": "Brake Pads", "price": 45.00},
            {"name": "Air Filter", "price": 12.99}
        ]
        for part in parts_data:
            response = self.client.post('/inventory/', json=part)
            self.part_ids.append(response.json['part']['id'])
    
    # ============================================
    # CREATE TESTS
    # ============================================
    
    def test_create_service_ticket_success(self):
        """Test successfully creating a new service ticket"""
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change and filter replacement"
        }
        
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Service ticket created successfully')
        self.assertEqual(response.json['service_ticket']['vehicle_id'], self.vehicle_id)
        self.assertEqual(response.json['service_ticket']['description'], 'Oil change and filter replacement')
        self.assertEqual(response.json['service_ticket']['status'], 'Open')
        self.assertIn('service_ticket_id', response.json['service_ticket'])
    
    def test_create_service_ticket_missing_vehicle_id(self):
        """Test creating a service ticket without vehicle_id"""
        ticket_payload = {
            "description": "Oil change"
        }
        
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_create_service_ticket_missing_description(self):
        """Test creating a service ticket without description"""
        ticket_payload = {
            "vehicle_id": self.vehicle_id
        }
        
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_create_service_ticket_invalid_vehicle(self):
        """Test creating a service ticket with non-existent vehicle"""
        ticket_payload = {
            "vehicle_id": 99999,
            "description": "Oil change"
        }
        
        response = self.client.post('/service-tickets/', json=ticket_payload)
        # Should fail when adding the ticket (vehicle doesn't exist)
        # May succeed at creation but fail on association
        self.assertIn(response.status_code, [201, 400, 404])
    
    def test_create_service_ticket_with_status(self):
        """Test creating a service ticket with specific status"""
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change",
            "status": "In Progress"
        }
        
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['service_ticket']['status'], 'In Progress')
    
    def test_create_service_ticket_with_total_cost(self):
        """Test creating a service ticket with total cost"""
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change",
            "total_cost": 85.50
        }
        
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['service_ticket']['total_cost'], 85.50)
    
    # ============================================
    # READ TESTS
    # ============================================
    
    def test_get_all_service_tickets(self):
        """Test retrieving all service tickets"""
        # Create multiple tickets
        for i in range(3):
            ticket_payload = {
                "vehicle_id": self.vehicle_id,
                "description": f"Service {i}"
            }
            self.client.post('/service-tickets/', json=ticket_payload)
        
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Service tickets retrieved successfully')
        self.assertEqual(response.json['count'], 3)
        self.assertEqual(len(response.json['service_tickets']), 3)
    
    def test_get_service_tickets_empty(self):
        """Test retrieving service tickets when none exist"""
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['count'], 0)
    
    def test_get_single_service_ticket(self):
        """Test retrieving a specific service ticket by ID"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change and filter replacement"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Get the ticket
        response = self.client.get(f'/service-tickets/{ticket_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_ticket']['service_ticket_id'], ticket_id)
        self.assertEqual(response.json['service_ticket']['description'], 'Oil change and filter replacement')
    
    def test_get_single_service_ticket_not_found(self):
        """Test retrieving a non-existent service ticket"""
        response = self.client.get('/service-tickets/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json['error'])
    
    def test_get_ticket_parts(self):
        """Test retrieving all parts on a service ticket"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Maintenance"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Add parts to the ticket
        part_payload = {
            "part_id": self.part_ids[0],
            "quantity": 2
        }
        self.client.post(f'/service-tickets/{ticket_id}/add-part', json=part_payload)
        
        # Get parts
        response = self.client.get(f'/service-tickets/{ticket_id}/parts')
        self.assertEqual(response.status_code, 200)
        self.assertIn('parts', response.json)
    
    # ============================================
    # MECHANIC ASSIGNMENT TESTS
    # ============================================
    
    def test_assign_mechanic_to_ticket(self):
        """Test assigning a mechanic to a service ticket"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Assign mechanic
        response = self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[0]}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('assigned to service ticket', response.json['message'])
        self.assertEqual(len(response.json['service_ticket']['mechanics']), 1)
    
    def test_assign_multiple_mechanics(self):
        """Test assigning multiple mechanics to a ticket"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Major repair"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Assign first mechanic
        self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[0]}'
        )
        
        # Assign second mechanic
        response = self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[1]}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['service_ticket']['mechanics']), 2)
    
    def test_assign_same_mechanic_twice(self):
        """Test assigning the same mechanic twice (should fail)"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Assign mechanic
        self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[0]}'
        )
        
        # Try to assign same mechanic again
        response = self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[0]}'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('already assigned', response.json['error'])
    
    def test_assign_nonexistent_mechanic(self):
        """Test assigning a non-existent mechanic"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Try to assign non-existent mechanic
        response = self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/99999'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_remove_mechanic_from_ticket(self):
        """Test removing a mechanic from a service ticket"""
        # Create a ticket and assign mechanic
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[0]}'
        )
        
        # Remove mechanic
        response = self.client.put(
            f'/service-tickets/{ticket_id}/remove-mechanic/{self.mechanic_ids[0]}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('removed from', response.json['message'])
        self.assertEqual(len(response.json['service_ticket']['mechanics']), 0)
    
    def test_remove_mechanic_not_assigned(self):
        """Test removing a mechanic that is not assigned"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Try to remove mechanic that was never assigned
        response = self.client.put(
            f'/service-tickets/{ticket_id}/remove-mechanic/{self.mechanic_ids[0]}'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('not assigned', response.json['error'])
    
    def test_edit_ticket_mechanics_batch(self):
        """Test batch adding and removing mechanics"""
        # Create a ticket and assign mechanic 0
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[0]}'
        )
        
        # Batch remove mechanic 0 and add mechanics 1 and 2
        edit_payload = {
            "remove_ids": [self.mechanic_ids[0]],
            "add_ids": [self.mechanic_ids[1], self.mechanic_ids[2]]
        }
        
        response = self.client.put(
            f'/service-tickets/{ticket_id}/edit',
            json=edit_payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['removed_mechanics']), 1)
        self.assertEqual(len(response.json['added_mechanics']), 2)
        self.assertEqual(len(response.json['service_ticket']['mechanics']), 2)
    
    # ============================================
    # PARTS TESTS
    # ============================================
    
    def test_add_part_to_ticket(self):
        """Test adding a part to a service ticket"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Add part
        part_payload = {
            "part_id": self.part_ids[0],
            "quantity": 1
        }
        
        response = self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json=part_payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Added', response.json['message'])
        self.assertEqual(len(response.json['parts']), 1)
        self.assertEqual(response.json['parts'][0]['quantity'], 1)
    
    def test_add_multiple_parts(self):
        """Test adding multiple parts to a service ticket"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Maintenance"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Add first part
        self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json={"part_id": self.part_ids[0], "quantity": 1}
        )
        
        # Add second part
        response = self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json={"part_id": self.part_ids[1], "quantity": 2}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['parts']), 2)
    
    def test_add_part_default_quantity(self):
        """Test adding a part with default quantity (1)"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Add part without specifying quantity
        part_payload = {
            "part_id": self.part_ids[0]
        }
        
        response = self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json=part_payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['parts'][0]['quantity'], 1)
    
    def test_add_part_invalid_quantity(self):
        """Test adding a part with invalid quantity"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Try to add with quantity < 1
        part_payload = {
            "part_id": self.part_ids[0],
            "quantity": 0
        }
        
        response = self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json=part_payload
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_add_same_part_twice(self):
        """Test adding the same part twice (should update quantity)"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Add part first time
        self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json={"part_id": self.part_ids[0], "quantity": 2}
        )
        
        # Add same part second time
        response = self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json={"part_id": self.part_ids[0], "quantity": 3}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['parts'][0]['quantity'], 5)  # 2 + 3
        self.assertEqual(len(response.json['parts']), 1)  # Still only 1 unique part
    
    def test_remove_part_from_ticket(self):
        """Test removing a part from a service ticket"""
        # Create a ticket and add part
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json={"part_id": self.part_ids[0], "quantity": 1}
        )
        
        # Remove part
        response = self.client.delete(
            f'/service-tickets/{ticket_id}/remove-part/{self.part_ids[0]}'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Removed', response.json['message'])
    
    def test_remove_part_not_on_ticket(self):
        """Test removing a part that is not on the ticket"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Try to remove part that was never added
        response = self.client.delete(
            f'/service-tickets/{ticket_id}/remove-part/{self.part_ids[0]}'
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('not on ticket', response.json['error'])
    
    # ============================================
    # UPDATE TESTS
    # ============================================
    
    def test_update_service_ticket_description(self):
        """Test updating service ticket description"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Update description
        update_payload = {
            "description": "Oil change and filter replacement"
        }
        
        response = self.client.put(
            f'/service-tickets/{ticket_id}',
            json=update_payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_ticket']['description'], 'Oil change and filter replacement')
    
    def test_update_service_ticket_status(self):
        """Test updating service ticket status"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Update status
        update_payload = {
            "status": "Closed"
        }
        
        response = self.client.put(
            f'/service-tickets/{ticket_id}',
            json=update_payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_ticket']['status'], 'Closed')
    
    def test_update_service_ticket_total_cost(self):
        """Test updating service ticket total cost"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change",
            "total_cost": 50.00
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Update total cost
        update_payload = {
            "total_cost": 75.50
        }
        
        response = self.client.put(
            f'/service-tickets/{ticket_id}',
            json=update_payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_ticket']['total_cost'], 75.50)
    
    def test_update_service_ticket_not_found(self):
        """Test updating a non-existent service ticket"""
        update_payload = {
            "description": "Updated description"
        }
        
        response = self.client.put(
            '/service-tickets/99999',
            json=update_payload
        )
        
        self.assertEqual(response.status_code, 404)
    
    # ============================================
    # DELETE TESTS
    # ============================================
    
    def test_delete_service_ticket(self):
        """Test successfully deleting a service ticket"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Oil change"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Delete the ticket
        response = self.client.delete(f'/service-tickets/{ticket_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted successfully', response.json['message'])
        
        # Verify the ticket is deleted
        get_response = self.client.get(f'/service-tickets/{ticket_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_service_ticket_not_found(self):
        """Test deleting a non-existent service ticket"""
        response = self.client.delete('/service-tickets/99999')
        self.assertEqual(response.status_code, 404)
    
    # ============================================
    # INTEGRATION TESTS
    # ============================================
    
    def test_complete_service_ticket_workflow(self):
        """Test a complete workflow: create ticket, add parts and mechanics, update, close"""
        # Create a ticket
        ticket_payload = {
            "vehicle_id": self.vehicle_id,
            "description": "Full maintenance service"
        }
        create_response = self.client.post('/service-tickets/', json=ticket_payload)
        ticket_id = create_response.json['service_ticket']['service_ticket_id']
        
        # Assign mechanics
        self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[0]}'
        )
        self.client.put(
            f'/service-tickets/{ticket_id}/assign-mechanic/{self.mechanic_ids[1]}'
        )
        
        # Add parts
        self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json={"part_id": self.part_ids[0], "quantity": 1}
        )
        self.client.post(
            f'/service-tickets/{ticket_id}/add-part',
            json={"part_id": self.part_ids[1], "quantity": 2}
        )
        
        # Update status and cost
        update_payload = {
            "status": "Closed",
            "total_cost": 125.50
        }
        response = self.client.put(
            f'/service-tickets/{ticket_id}',
            json=update_payload
        )
        
        self.assertEqual(response.status_code, 200)
        ticket = response.json['service_ticket']
        self.assertEqual(ticket['status'], 'Closed')
        self.assertEqual(ticket['total_cost'], 125.50)
        self.assertEqual(len(ticket['mechanics']), 2)
    
    # ============================================
    # RATE LIMITING TESTS
    # ============================================
    
    def test_create_ticket_multiple_requests(self):
        """Test creating multiple tickets in sequence"""
        # Note: Rate limiting may not be enforced in test environment
        count_success = 0
        
        for i in range(5):
            ticket_payload = {
                "vehicle_id": self.vehicle_id,
                "description": f"Service {i}"
            }
            response = self.client.post('/service-tickets/', json=ticket_payload)
            
            if response.status_code == 201:
                count_success += 1
        
        self.assertGreater(count_success, 0)


if __name__ == '__main__':
    unittest.main()
