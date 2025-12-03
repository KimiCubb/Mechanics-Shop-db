# 🔧 Mechanic Shop API

A RESTful API for managing a mechanic shop's customers, vehicles, mechanics, and service tickets. Built with Flask, SQLAlchemy, and Marshmallow.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Testing with Postman](#testing-with-postman)

## ✨ Features

- **Customer Management** - Create, read, update, and delete customers
- **Vehicle Management** - Track customer vehicles with VIN validation
- **Mechanic Management** - Manage mechanic profiles and salaries
- **Service Tickets** - Create service tickets and assign/remove mechanics
- **Many-to-Many Relationships** - Multiple mechanics can work on multiple service tickets

## 🛠 Tech Stack

- **Framework:** Flask 3.0+
- **ORM:** SQLAlchemy with Flask-SQLAlchemy
- **Serialization:** Marshmallow with Flask-Marshmallow
- **Database:** MySQL
- **Python:** 3.10+

## 📁 Project Structure

```
Mechanic-Shop-db/
├── app.py                      # Application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── Mechanics Shop API.postman_collection.json  # Postman collection
├── app/
│   ├── __init__.py             # App factory
│   ├── extensions.py           # Flask extensions (Marshmallow)
│   ├── models.py               # SQLAlchemy models
│   └── blueprints/
│       ├── customers/          # Customer routes & schemas
│       ├── vehicles/           # Vehicle routes & schemas
│       ├── mechanics/          # Mechanic routes & schemas
│       └── service_tickets/    # Service ticket routes & schemas
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MySQL Server
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/KimiCubb/Mechanics-Shop-db.git
cd Mechanics-Shop-db
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create MySQL Database

```sql
CREATE DATABASE mechanic_shop_db;
```

### Step 5: Configure Database Connection

Edit `config.py` and update the database URI with your MySQL credentials:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/mechanic_shop_db'
```

### Step 6: Run the Application

```bash
python app.py
```

You should see:

```
✅ Database tables created successfully!
🚀 Starting Mechanic Shop API...
==================================================
📍 Server running at: http://127.0.0.1:5000
==================================================
📌 Available Endpoints:
   • Customers:       http://127.0.0.1:5000/customers
   • Vehicles:        http://127.0.0.1:5000/vehicles
   • Mechanics:       http://127.0.0.1:5000/mechanics
   • Service Tickets: http://127.0.0.1:5000/service-tickets
==================================================
```

## 📚 API Endpoints

### Customers `/customers`

| Method   | Endpoint          | Description         |
| -------- | ----------------- | ------------------- |
| `GET`    | `/customers/`     | Get all customers   |
| `GET`    | `/customers/<id>` | Get customer by ID  |
| `POST`   | `/customers/`     | Create new customer |
| `PUT`    | `/customers/<id>` | Update customer     |
| `DELETE` | `/customers/<id>` | Delete customer     |

**Create Customer Request Body:**

```json
{
  "name": "John Doe",
  "phone": "555-123-4567",
  "email": "johndoe@email.com",
  "address": "123 Main Street, City, ST 12345"
}
```

### Vehicles `/vehicles`

| Method   | Endpoint                  | Description             |
| -------- | ------------------------- | ----------------------- |
| `GET`    | `/vehicles/`              | Get all vehicles        |
| `GET`    | `/vehicles/<id>`          | Get vehicle by ID       |
| `GET`    | `/vehicles/customer/<id>` | Get customer's vehicles |
| `POST`   | `/vehicles/`              | Create new vehicle      |
| `PUT`    | `/vehicles/<id>`          | Update vehicle          |
| `DELETE` | `/vehicles/<id>`          | Delete vehicle          |

**Create Vehicle Request Body:**

```json
{
  "customer_id": 1,
  "make": "Toyota",
  "model": "Camry",
  "year": 2022,
  "vin": "1HGBH41JXMN109186"
}
```

### Mechanics `/mechanics`

| Method   | Endpoint          | Description         |
| -------- | ----------------- | ------------------- |
| `GET`    | `/mechanics/`     | Get all mechanics   |
| `GET`    | `/mechanics/<id>` | Get mechanic by ID  |
| `POST`   | `/mechanics/`     | Create new mechanic |
| `PUT`    | `/mechanics/<id>` | Update mechanic     |
| `DELETE` | `/mechanics/<id>` | Delete mechanic     |

**Create Mechanic Request Body:**

```json
{
  "name": "Mike Johnson",
  "email": "mike.johnson@mechanicshop.com",
  "address": "456 Workshop Lane, City, ST 12345",
  "phone": "555-987-6543",
  "salary": 55000.0
}
```

### Service Tickets `/service-tickets`

| Method   | Endpoint                                              | Description             |
| -------- | ----------------------------------------------------- | ----------------------- |
| `GET`    | `/service-tickets/`                                   | Get all service tickets |
| `GET`    | `/service-tickets/<id>`                               | Get ticket by ID        |
| `POST`   | `/service-tickets/`                                   | Create new ticket       |
| `PUT`    | `/service-tickets/<id>`                               | Update ticket           |
| `PUT`    | `/service-tickets/<id>/assign-mechanic/<mechanic_id>` | Assign mechanic         |
| `PUT`    | `/service-tickets/<id>/remove-mechanic/<mechanic_id>` | Remove mechanic         |
| `DELETE` | `/service-tickets/<id>`                               | Delete ticket           |

**Create Service Ticket Request Body:**

```json
{
  "vehicle_id": 1,
  "description": "Oil change, tire rotation, and brake inspection",
  "status": "Open",
  "total_cost": 150.0
}
```

## 🗄 Database Schema

### Entity Relationship Diagram

```
CUSTOMER 1 ───< VEHICLE 1 ───< SERVICE_TICKET >───< SERVICE_TICKET_MECHANIC >─── MECHANIC
```

### Tables

| Table                     | Primary Key         | Description                       |
| ------------------------- | ------------------- | --------------------------------- |
| `customer`                | `customer_id`       | Customer information              |
| `vehicle`                 | `vehicle_id`        | Vehicle details (FK: customer_id) |
| `service_ticket`          | `service_ticket_id` | Service records (FK: vehicle_id)  |
| `mechanic`                | `mechanic_id`       | Mechanic profiles                 |
| `service_ticket_mechanic` | Composite           | Junction table (many-to-many)     |

## 🧪 Testing with Postman

A Postman collection is included in the repository: `Mechanics Shop API.postman_collection.json`

### Import Collection:

1. Open Postman
2. Click **Import**
3. Select the `Mechanics Shop API.postman_collection.json` file
4. Start testing the endpoints!

### Test Order Recommendation:

1. Create a Customer
2. Create a Vehicle (requires customer_id)
3. Create a Mechanic
4. Create a Service Ticket (requires vehicle_id)
5. Assign Mechanic to Service Ticket

## 📝 License

This project is for educational purposes.

## 👤 Author

**Kimberly Cirillo**

- GitHub: [@KimiCubb](https://github.com/KimiCubb)
