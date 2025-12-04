"""
Schema Validation Test
This test validates that the Swagger/OpenAPI definitions match the actual
Marshmallow schemas and models. It prevents documentation drift.
"""

import unittest
import yaml
import json
from pathlib import Path
from app import create_app
from app.blueprints.customers.schemas import CustomerSchema, LoginSchema
from app.blueprints.vehicles.schemas import VehicleSchema
from app.blueprints.mechanics.schemas import MechanicSchema
from app.blueprints.service_tickets.schemas import ServiceTicketSchema
from app.blueprints.inventory.schemas import InventorySchema


class SwaggerSchemaValidationTest(unittest.TestCase):
    """Validate Swagger definitions match Marshmallow schemas"""

    @classmethod
    def setUpClass(cls):
        """Load swagger.yaml once for all tests"""
        swagger_path = Path(__file__).parent.parent / 'app' / 'static' / 'swagger.yaml'
        with open(swagger_path, 'r') as f:
            cls.swagger = yaml.safe_load(f)
        
        cls.app = create_app('TestingConfig')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        """Clean up app context"""
        cls.app_context.pop()

    def get_swagger_definition(self, name):
        """Get a definition from swagger.yaml"""
        return self.swagger.get('definitions', {}).get(name, {})

    def get_schema_fields(self, schema_class):
        """Get all fields from a Marshmallow schema"""
        schema = schema_class()
        return schema.fields

    def test_customer_schema_fields(self):
        """Verify CustomerCreate fields match Swagger CustomerCreate definition"""
        swagger_def = self.get_swagger_definition('CustomerCreate')
        schema = CustomerSchema()
        
        # Check required fields match
        swagger_required = set(swagger_def.get('required', []))
        schema_required = {
            name for name, field in schema.fields.items()
            if field.required and name != 'customer_id'
        }
        
        self.assertEqual(
            swagger_required,
            schema_required,
            f"CustomerCreate required fields mismatch. "
            f"Swagger: {swagger_required}, Schema: {schema_required}"
        )
        
        # Check field names exist in both
        swagger_props = set(swagger_def.get('properties', {}).keys())
        schema_fields = set(schema.fields.keys())
        
        self.assertTrue(
            swagger_props.issubset(schema_fields) or schema_fields.issubset(swagger_props),
            f"CustomerCreate field names don't match. "
            f"Swagger: {swagger_props}, Schema: {schema_fields}"
        )

    def test_vehicle_schema_fields(self):
        """Verify VehicleCreate fields match Swagger VehicleCreate definition"""
        swagger_def = self.get_swagger_definition('VehicleCreate')
        schema = VehicleSchema()
        
        swagger_required = set(swagger_def.get('required', []))
        schema_required = {
            name for name, field in schema.fields.items()
            if field.required and name != 'vehicle_id'
        }
        
        self.assertEqual(
            swagger_required,
            schema_required,
            f"VehicleCreate required fields mismatch. "
            f"Swagger: {swagger_required}, Schema: {schema_required}"
        )

    def test_inventory_identifier_consistency(self):
        """Verify Inventory uses 'id' consistently (not 'part_id')"""
        swagger_part = self.get_swagger_definition('Part')
        schema = InventorySchema()
        
        # Swagger should use 'id'
        self.assertIn('id', swagger_part.get('properties', {}),
                      "Swagger Part definition should have 'id' field")
        self.assertNotIn('part_id', swagger_part.get('properties', {}),
                         "Swagger Part definition should not have 'part_id'")
        
        # Schema should use 'id'
        self.assertIn('id', schema.fields,
                      "InventorySchema should have 'id' field")

    def test_mechanic_schema_fields(self):
        """Verify MechanicCreate fields match Swagger MechanicCreate definition"""
        swagger_def = self.get_swagger_definition('MechanicCreate')
        schema = MechanicSchema()
        
        swagger_required = set(swagger_def.get('required', []))
        schema_required = {
            name for name, field in schema.fields.items()
            if field.required and name != 'mechanic_id'
        }
        
        self.assertEqual(
            swagger_required,
            schema_required,
            f"MechanicCreate required fields mismatch. "
            f"Swagger: {swagger_required}, Schema: {schema_required}"
        )

    def test_service_ticket_schema_fields(self):
        """Verify ServiceTicketCreate fields match Swagger ServiceTicketCreate definition"""
        swagger_def = self.get_swagger_definition('ServiceTicketCreate')
        schema = ServiceTicketSchema()
        
        swagger_required = set(swagger_def.get('required', []))
        schema_required = {
            name for name, field in schema.fields.items()
            if field.required and name not in ['service_ticket_id', 'date_in', 'date_out']
        }
        
        self.assertEqual(
            swagger_required,
            schema_required,
            f"ServiceTicketCreate required fields mismatch. "
            f"Swagger: {swagger_required}, Schema: {schema_required}"
        )

    def test_swagger_yaml_is_valid(self):
        """Verify swagger.yaml is valid YAML and OpenAPI 2.0"""
        self.assertIsNotNone(self.swagger, "Swagger YAML should load successfully")
        self.assertEqual(self.swagger.get('swagger'), '2.0',
                         "Should be OpenAPI 2.0 format")
        self.assertIn('info', self.swagger)
        self.assertIn('paths', self.swagger)
        self.assertIn('definitions', self.swagger)

    def test_all_paths_have_descriptions(self):
        """Verify all API paths have proper documentation"""
        paths = self.swagger.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    self.assertIn('summary', details,
                                  f"Path {path} {method} missing summary")
                    self.assertIn('responses', details,
                                  f"Path {path} {method} missing responses")

    def test_all_definitions_have_properties(self):
        """Verify all definitions have properties documented"""
        definitions = self.swagger.get('definitions', {})
        for def_name, definition in definitions.items():
            # Skip pagination-like objects
            if 'Response' in def_name or 'object' in str(definition):
                self.assertIn('properties', definition,
                              f"Definition {def_name} should have 'properties'")

    def test_customer_id_field_is_dump_only(self):
        """Verify customer_id is dump_only (read-only) in schema"""
        schema = CustomerSchema()
        customer_id_field = schema.fields.get('customer_id')
        self.assertIsNotNone(customer_id_field)
        # dump_only fields should not be loadable
        self.assertTrue(customer_id_field.dump_only,
                        "customer_id should be dump_only (read-only)")


if __name__ == '__main__':
    unittest.main()
