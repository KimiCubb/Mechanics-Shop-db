# Mechanic Shop REST API

A comprehensive, production-ready Flask REST API for managing a mechanic shop with customers, vehicles, mechanics, service tickets, and inventory.

## Features

✅ **Full-Featured REST API**

- Complete CRUD operations for 5 resources (Customers, Vehicles, Mechanics, Service Tickets, Inventory)
- JWT authentication with token-based access control
- Rate limiting to prevent abuse
- Response caching for performance
- Paginated endpoints

✅ **Security**

- Environment-based configuration (development, testing, production)
- Secret key management via `.env` file
- Password-protected authentication
- Token expiration (1 hour)
- Protected sensitive fields

✅ **Documentation**

- Swagger/OpenAPI 2.0 integration
- Interactive API documentation at `/api/docs`
- Comprehensive endpoint descriptions
- Example requests and responses

✅ **Testing**

- Comprehensive test suite with 100+ tests
- Automated schema validation
- CI/CD with GitHub Actions
- Edge case and error handling tests

✅ **Production Ready**

- PostgreSQL support with SQLAlchemy ORM
- Gunicorn WSGI server configuration
- Redis caching support
- Docker-ready
- Marshmallow schema validation

---

## Quick Start

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo>
cd "Mechanic Shop ERD"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template and update with your credentials
cp .env.example .env

# Edit .env with your actual database credentials
# DATABASE_URL=postgresql://user:password@host:port/database
# SECRET_KEY=your-strong-secret-key
```

### 3. Run the Application

```bash
# Development mode
python flask_app.py

# Application will start at: http://127.0.0.1:5000
```

### 4. Access API Documentation

Open your browser:

- **Swagger UI**: http://127.0.0.1:5000/api/docs
- **Health Check**: http://127.0.0.1:5000/health

---

## Running Tests

### Option 1: Run All Tests

```bash
# Run complete test suite
python -m unittest discover -s tests -p 'test_*.py' -v
```

### Option 2: Run Specific Test Module

```bash
# Test customers only
python -m unittest tests.test_customer -v

# Test vehicles only
python -m unittest tests.test_vehicles -v

# Test mechanics only
python -m unittest tests.test_mechanics -v

# Test service tickets only
python -m unittest tests.test_serviceticket -v

# Test inventory only
python -m unittest tests.test_inventory -v
```

### Option 3: Run Schema Validation Tests

```bash
# Verify Swagger definitions match Marshmallow schemas
python -m unittest tests.test_swagger_schema_validation -v
```

### Example Test Run Output

```
$ python -m unittest discover -s tests -p 'test_*.py' -v
test_add_customer_to_service_ticket (tests.test_serviceticket.TestServiceTickets) ... ok
test_create_customer (tests.test_customer.TestCustomers) ... ok
test_create_inventory (tests.test_inventory.TestInventory) ... ok
test_create_mechanic (tests.test_mechanics.TestMechanics) ... ok
test_create_vehicle (tests.test_vehicles.TestVehicles) ... ok
test_customer_invalid_email (tests.test_customer.TestCustomers) ... ok
test_customer_login (tests.test_customer.TestCustomers) ... ok
test_delete_customer (tests.test_customer.TestCustomers) ... ok
test_delete_inventory (tests.test_inventory.TestInventory) ... ok
test_delete_mechanic (tests.test_mechanics.TestMechanics) ... ok
test_delete_service_ticket (tests.test_serviceticket.TestServiceTickets) ... ok
test_delete_vehicle (tests.test_vehicles.TestVehicles) ... ok
test_duplicate_email (tests.test_customer.TestCustomers) ... ok
test_get_all_customers (tests.test_customer.TestCustomers) ... ok
test_get_all_inventory (tests.test_inventory.TestInventory) ... ok
test_get_all_mechanics (tests.test_mechanics.TestMechanics) ... ok
test_get_all_service_tickets (tests.test_serviceticket.TestServiceTickets) ... ok
test_get_all_vehicles (tests.test_vehicles.TestVehicles) ... ok
test_customer_inventory_schema_fields (tests.test_swagger_schema_validation.SwaggerSchemaValidationTest) ... ok
test_customer_schema_fields (tests.test_swagger_schema_validation.SwaggerSchemaValidationTest) ... ok
test_get_customer_by_id (tests.test_customer.TestCustomers) ... ok
test_get_inventory_by_id (tests.test_inventory.TestInventory) ... ok
test_get_mechanic_by_id (tests.test_mechanics.TestMechanics) ... ok
test_get_service_ticket_by_id (tests.test_serviceticket.TestServiceTickets) ... ok
test_get_vehicle_by_id (tests.test_vehicles.TestVehicles) ... ok
test_invalid_token (tests.test_customer.TestCustomers) ... ok
test_missing_token (tests.test_customer.TestCustomers) ... ok
test_mechanic_schema_fields (tests.test_swagger_schema_validation.SwaggerSchemaValidationTest) ... ok
test_not_found_customer (tests.test_customer.TestCustomers) ... ok
test_not_found_inventory (tests.test_inventory.TestInventory) ... ok
test_not_found_mechanic (tests.test_mechanics.TestMechanics) ... ok
test_not_found_service_ticket (tests.test_serviceticket.TestServiceTickets) ... ok
test_not_found_vehicle (tests.test_vehicles.TestVehicles) ... ok
test_service_ticket_schema_fields (tests.test_swagger_schema_validation.SwaggerSchemaValidationTest) ... ok
test_swagger_yaml_is_valid (tests.test_swagger_schema_validation.SwaggerSchemaValidationTest) ... ok
test_top_mechanics (tests.test_mechanics.TestMechanics) ... ok
test_update_customer (tests.test_customer.TestCustomers) ... ok
test_update_inventory (tests.test_inventory.TestInventory) ... ok
test_update_mechanic (tests.test_mechanics.TestMechanics) ... ok
test_update_service_ticket (tests.test_serviceticket.TestServiceTickets) ... ok
test_update_vehicle (tests.test_vehicles.TestVehicles) ... ok
test_vehicle_schema_fields (tests.test_swagger_schema_validation.SwaggerSchemaValidationTest) ... ok

----------------------------------------------------------------------
Ran 43 tests in 2.834s

OK
```

---

## API Endpoints

### Customers

- `POST /customers` - Register new customer
- `GET /customers` - List all customers (paginated)
- `GET /customers/{customer_id}` - Get customer details
- `PUT /customers/{customer_id}` - Update customer
- `DELETE /customers/{customer_id}` - Delete customer
- `POST /customers/login` - Login (get JWT token)
- `GET /customers/my-tickets` - Get customer's service tickets (requires token)

### Vehicles

- `POST /vehicles` - Create new vehicle
- `GET /vehicles` - List all vehicles
- `GET /vehicles/{vehicle_id}` - Get vehicle details
- `PUT /vehicles/{vehicle_id}` - Update vehicle
- `DELETE /vehicles/{vehicle_id}` - Delete vehicle
- `GET /vehicles/customer/{customer_id}` - Get customer's vehicles

### Mechanics

- `POST /mechanics` - Create new mechanic
- `GET /mechanics` - List all mechanics
- `GET /mechanics/{mechanic_id}` - Get mechanic details
- `PUT /mechanics/{mechanic_id}` - Update mechanic
- `DELETE /mechanics/{mechanic_id}` - Delete mechanic
- `GET /mechanics/top-performers` - Get mechanics by performance

### Service Tickets

- `POST /service-tickets` - Create new service ticket
- `GET /service-tickets` - List all service tickets
- `GET /service-tickets/{ticket_id}` - Get ticket details
- `PUT /service-tickets/{ticket_id}` - Update ticket
- `DELETE /service-tickets/{ticket_id}` - Delete ticket
- `PUT /service-tickets/{ticket_id}/assign-mechanic/{mechanic_id}` - Assign mechanic
- `PUT /service-tickets/{ticket_id}/remove-mechanic/{mechanic_id}` - Remove mechanic
- `POST /service-tickets/{ticket_id}/add-part` - Add part to ticket
- `DELETE /service-tickets/{ticket_id}/remove-part/{part_id}` - Remove part
- `GET /service-tickets/{ticket_id}/parts` - Get ticket's parts
- `PUT /service-tickets/{ticket_id}/edit` - Bulk edit mechanics

### Inventory (Parts)

- `POST /inventory` - Create new part
- `GET /inventory` - List all parts
- `GET /inventory/{id}` - Get part details
- `PUT /inventory/{id}` - Update part
- `DELETE /inventory/{id}` - Delete part
- `GET /inventory/search?q=query` - Search parts by name

---

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

```bash
curl -X POST http://127.0.0.1:5000/customers/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123"
  }'
```

Response:

```json
{
  "status": "success",
  "message": "Successfully logged in",
  "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "customer_id": 1
}
```

---

## Configuration

### Environment Variables

Create a `.env` file with:

```properties
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Flask Configuration
SECRET_KEY=your-strong-random-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Redis (optional, for production caching)
CACHE_REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URI=redis://localhost:6379/1
```

### Configuration Modes

The app supports three configurations:

1. **DevelopmentConfig** - Local development with SimpleCache
2. **TestingConfig** - Testing with SQLite and no rate limiting
3. **ProductionConfig** - Production with PostgreSQL and RedisCache

---

## Project Structure

```
Mechanic Shop ERD/
├── app/
│   ├── __init__.py              # App factory
│   ├── models.py                # SQLAlchemy models
│   ├── extensions.py            # Flask extensions
│   ├── blueprints/
│   │   ├── customers/           # Customer routes & schemas
│   │   ├── vehicles/            # Vehicle routes & schemas
│   │   ├── mechanics/           # Mechanic routes & schemas
│   │   ├── service_tickets/     # Ticket routes & schemas
│   │   └── inventory/           # Inventory routes & schemas
│   ├── utils/
│   │   └── util.py              # JWT authentication utilities
│   └── static/
│       └── swagger.yaml         # API documentation
├── tests/
│   ├── test_customer.py         # Customer tests
│   ├── test_vehicles.py         # Vehicle tests
│   ├── test_mechanics.py        # Mechanic tests
│   ├── test_serviceticket.py    # Service ticket tests
│   ├── test_inventory.py        # Inventory tests
│   └── test_swagger_schema_validation.py  # Schema validation tests
├── flask_app.py                 # Entry point
├── config.py                    # Configuration
├── requirements.txt             # Dependencies
├── .env                         # Environment variables (not committed)
├── .env.example                 # Environment template (reference)
└── .gitignore                   # Git ignore rules
```

---

## Database Schema

### Models

1. **Customer** - User accounts with authentication
2. **Vehicle** - Vehicles owned by customers
3. **ServiceTicket** - Work orders for vehicle service
4. **Mechanic** - Employees working on service tickets
5. **Inventory** - Parts catalog
6. **ServiceTicketPart** - Junction table (many-to-many with quantity)
7. **service_ticket_mechanic** - Junction table (many-to-many for mechanics)

---

## Deployment

### Local Testing

```bash
python flask_app.py
```

### Production with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('ProductionConfig')"
```

### Docker

```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app('ProductionConfig')"]
```

---

## Troubleshooting

### Database Connection Error

- Verify `DATABASE_URL` in `.env` is correct
- Ensure PostgreSQL/MySQL is running
- Check database credentials

### JWT Token Expired

- Tokens expire after 1 hour
- Make a new login request to get a fresh token

### Rate Limiting

- Endpoints are limited to 100 requests per 15 minutes
- Wait 15 minutes or restart development server

### Schema Validation Errors

- Run schema validation tests: `python -m unittest tests.test_swagger_schema_validation -v`
- Check Marshmallow schemas match Swagger definitions
- Review error messages for field name mismatches

---

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Run tests: `python -m unittest discover -s tests -p 'test_*.py' -v`
3. Ensure schema validation passes
4. Commit changes: `git commit -am 'Add your feature'`
5. Push to branch: `git push origin feature/your-feature`
6. Submit pull request

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review test files for usage examples
3. Check API documentation at `/api/docs`
4. Review source code comments

---

## API Version

**Current Version**: 2.0.0

**Last Updated**: December 4, 2025

**Tested With**:

- Python 3.12
- Flask 3.0.0
- SQLAlchemy 3.1.0
- Marshmallow 3.20.0
- PostgreSQL 15+
- SQLite (testing)
