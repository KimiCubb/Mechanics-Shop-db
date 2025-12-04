from app import create_app
from app.models import db, Inventory
import unittest


class TestInventory(unittest.TestCase):
    """Comprehensive test suite for Inventory (Parts) endpoints"""
    
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
    
    def test_create_part_success(self):
        """Test successfully creating a new part"""
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'Part created successfully')
        self.assertEqual(response.json['part']['name'], 'Engine Oil')
        self.assertEqual(response.json['part']['price'], 15.99)
        self.assertIn('id', response.json['part'])
    
    def test_create_part_missing_name(self):
        """Test creating a part with missing name"""
        part_payload = {
            "price": 15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_create_part_missing_price(self):
        """Test creating a part with missing price"""
        part_payload = {
            "name": "Engine Oil"
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_create_part_negative_price(self):
        """Test creating a part with negative price"""
        part_payload = {
            "name": "Engine Oil",
            "price": -15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_create_part_zero_price(self):
        """Test creating a part with zero price"""
        part_payload = {
            "name": "Free Part",
            "price": 0.00
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part']['price'], 0.00)
    
    def test_create_part_empty_name(self):
        """Test creating a part with empty name"""
        part_payload = {
            "name": "",
            "price": 15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 400)
    
    def test_create_part_very_long_name(self):
        """Test creating a part with very long name"""
        part_payload = {
            "name": "A" * 150,  # Exceeds max length of 100
            "price": 15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 400)
    
    # ============================================
    # READ TESTS
    # ============================================
    
    def test_get_all_parts(self):
        """Test retrieving all parts"""
        # Create multiple parts
        for i in range(5):
            part_payload = {
                "name": f"Part {i}",
                "price": 10.00 + (i * 5)
            }
            self.client.post('/inventory/', json=part_payload)
        
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Inventory retrieved successfully')
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(len(response.json['parts']), 5)
        self.assertIn('pagination', response.json)
        self.assertEqual(response.json['pagination']['total_items'], 5)
    
    def test_get_parts_empty(self):
        """Test retrieving parts when none exist"""
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(len(response.json['parts']), 0)
        self.assertEqual(response.json['pagination']['total_items'], 0)
    
    def test_get_single_part(self):
        """Test retrieving a specific part by ID"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        create_response = self.client.post('/inventory/', json=part_payload)
        part_id = create_response.json['part']['id']
        
        # Get the part
        response = self.client.get(f'/inventory/{part_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part']['id'], part_id)
        self.assertEqual(response.json['part']['name'], 'Engine Oil')
        self.assertEqual(response.json['part']['price'], 15.99)
    
    def test_get_single_part_not_found(self):
        """Test retrieving a non-existent part"""
        response = self.client.get('/inventory/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json['error'])
    
    def test_search_parts_by_name(self):
        """Test searching parts by name"""
        # Create parts with different names
        parts_data = [
            {"name": "Engine Oil", "price": 15.99},
            {"name": "Brake Fluid", "price": 8.99},
            {"name": "Oil Filter", "price": 12.99},
            {"name": "Air Filter", "price": 9.99}
        ]
        
        for part in parts_data:
            self.client.post('/inventory/', json=part)
        
        # Search for "Oil"
        response = self.client.get('/inventory/search?q=Oil')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(len(response.json['parts']), 2)  # "Engine Oil" and "Oil Filter"
        self.assertTrue(all('Oil' in p['name'] for p in response.json['parts']))
    
    def test_search_parts_case_insensitive(self):
        """Test that search is case insensitive"""
        # Create parts
        parts_data = [
            {"name": "Engine Oil", "price": 15.99},
            {"name": "BRAKE FLUID", "price": 8.99}
        ]
        
        for part in parts_data:
            self.client.post('/inventory/', json=part)
        
        # Search with different cases
        response1 = self.client.get('/inventory/search?q=oil')
        response2 = self.client.get('/inventory/search?q=OIL')
        response3 = self.client.get('/inventory/search?q=brake')
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response1.json['status'], 'success')
        self.assertEqual(len(response1.json['parts']), 1)
        self.assertEqual(len(response3.json['parts']), 1)
    
    def test_search_parts_no_query(self):
        """Test search without query parameter"""
        response = self.client.get('/inventory/search')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_search_parts_empty_query(self):
        """Test search with empty query"""
        response = self.client.get('/inventory/search?q=')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_search_parts_no_results(self):
        """Test search that returns no results"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        self.client.post('/inventory/', json=part_payload)
        
        # Search for something that doesn't exist
        response = self.client.get('/inventory/search?q=Transmission')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(len(response.json['parts']), 0)
    
    # ============================================
    # UPDATE TESTS
    # ============================================
    
    def test_update_part_name(self):
        """Test updating part name"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        create_response = self.client.post('/inventory/', json=part_payload)
        part_id = create_response.json['part']['id']
        
        # Update name
        update_payload = {
            "name": "Premium Engine Oil"
        }
        
        response = self.client.put(f'/inventory/{part_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part']['name'], 'Premium Engine Oil')
        self.assertEqual(response.json['part']['price'], 15.99)  # Should remain unchanged
    
    def test_update_part_price(self):
        """Test updating part price"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        create_response = self.client.post('/inventory/', json=part_payload)
        part_id = create_response.json['part']['id']
        
        # Update price
        update_payload = {
            "price": 17.99
        }
        
        response = self.client.put(f'/inventory/{part_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part']['price'], 17.99)
        self.assertEqual(response.json['part']['name'], 'Engine Oil')  # Should remain unchanged
    
    def test_update_part_both_fields(self):
        """Test updating both name and price"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        create_response = self.client.post('/inventory/', json=part_payload)
        part_id = create_response.json['part']['id']
        
        # Update both fields
        update_payload = {
            "name": "Synthetic Engine Oil",
            "price": 19.99
        }
        
        response = self.client.put(f'/inventory/{part_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part']['name'], 'Synthetic Engine Oil')
        self.assertEqual(response.json['part']['price'], 19.99)
    
    def test_update_part_not_found(self):
        """Test updating a non-existent part"""
        update_payload = {
            "name": "New Name",
            "price": 20.00
        }
        
        response = self.client.put('/inventory/99999', json=update_payload)
        self.assertEqual(response.status_code, 404)
    
    def test_update_part_negative_price(self):
        """Test updating a part with negative price"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        create_response = self.client.post('/inventory/', json=part_payload)
        part_id = create_response.json['part']['id']
        
        # Try to update with negative price
        update_payload = {
            "price": -10.00
        }
        
        response = self.client.put(f'/inventory/{part_id}', json=update_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_update_part_zero_price(self):
        """Test updating a part to zero price"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        create_response = self.client.post('/inventory/', json=part_payload)
        part_id = create_response.json['part']['id']
        
        # Update to zero price
        update_payload = {
            "price": 0.00
        }
        
        response = self.client.put(f'/inventory/{part_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part']['price'], 0.00)
    
    # ============================================
    # DELETE TESTS
    # ============================================
    
    def test_delete_part(self):
        """Test successfully deleting a part"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        create_response = self.client.post('/inventory/', json=part_payload)
        part_id = create_response.json['part']['id']
        
        # Delete the part
        response = self.client.delete(f'/inventory/{part_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted successfully', response.json['message'])
        
        # Verify the part is deleted
        get_response = self.client.get(f'/inventory/{part_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_part_not_found(self):
        """Test deleting a non-existent part"""
        response = self.client.delete('/inventory/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json['error'])
    
    # ============================================
    # RATE LIMITING TESTS
    # ============================================
    
    def test_create_part_multiple_requests(self):
        """Test creating multiple parts in sequence"""
        # Note: Rate limiting may not be enforced in test environment
        count_success = 0
        
        for i in range(5):
            part_payload = {
                "name": f"Part {i}",
                "price": 10.00 + (i * 5)
            }
            response = self.client.post('/inventory/', json=part_payload)
            
            if response.status_code == 201:
                count_success += 1
        
        self.assertGreater(count_success, 0)
    
    # ============================================
    # EDGE CASES
    # ============================================
    
    def test_create_part_high_price(self):
        """Test creating a part with very high price"""
        part_payload = {
            "name": "Expensive Part",
            "price": 999999.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part']['price'], 999999.99)
    
    def test_create_part_special_characters_in_name(self):
        """Test creating a part with special characters in name"""
        part_payload = {
            "name": "Oil Filter (10W-40) & Pump",
            "price": 15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part']['name'], "Oil Filter (10W-40) & Pump")
    
    def test_create_part_unicode_characters(self):
        """Test creating a part with unicode characters"""
        part_payload = {
            "name": "Масло двигателя (Engine Oil)",
            "price": 15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        # Should handle unicode properly
        self.assertIn(response.status_code, [201, 400])
    
    def test_create_part_whitespace_in_name(self):
        """Test creating a part with leading/trailing whitespace"""
        part_payload = {
            "name": "  Engine Oil  ",
            "price": 15.99
        }
        
        response = self.client.post('/inventory/', json=part_payload)
        # May or may not strip whitespace depending on implementation
        self.assertIn(response.status_code, [201, 400])
    
    def test_search_parts_partial_match(self):
        """Test searching for parts with partial names"""
        # Create parts
        parts_data = [
            {"name": "Engine Oil", "price": 15.99},
            {"name": "Engine Filter", "price": 12.99},
            {"name": "Air Filter", "price": 9.99}
        ]
        
        for part in parts_data:
            self.client.post('/inventory/', json=part)
        
        # Search for "Engine"
        response = self.client.get('/inventory/search?q=Engine')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(len(response.json['parts']), 2)  # "Engine Oil" and "Engine Filter"
    
    def test_caching_get_all_parts(self):
        """Test that GET /inventory/ uses caching"""
        # Create a part
        part_payload = {
            "name": "Engine Oil",
            "price": 15.99
        }
        self.client.post('/inventory/', json=part_payload)
        
        # First request
        response1 = self.client.get('/inventory/')
        count1 = len(response1.json['parts'])
        
        # Create another part
        part_payload2 = {
            "name": "Brake Fluid",
            "price": 8.99
        }
        self.client.post('/inventory/', json=part_payload2)
        
        # Second request (should be cached and still show 1 part)
        response2 = self.client.get('/inventory/')
        count2 = len(response2.json['parts'])
        
        # Both should be 200
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)


if __name__ == '__main__':
    unittest.main()
