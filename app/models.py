from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Integer, String, Float, DateTime, Text, ForeignKey, Table
from datetime import datetime

class Base(DeclarativeBase):
    pass

# Initialize db without app - it will be initialized in the app factory
db = SQLAlchemy(model_class=Base)

# ============================================
# ASSOCIATION TABLE (Many-to-Many) - Mechanics
# ============================================
service_ticket_mechanic = Table(
    'service_ticket_mechanic',
    db.Model.metadata,
    db.Column('service_ticket_id', Integer, ForeignKey('service_ticket.service_ticket_id'), primary_key=True),
    db.Column('mechanic_id', Integer, ForeignKey('mechanic.mechanic_id'), primary_key=True)
)


# ============================================
# ASSOCIATION MODEL (Many-to-Many with quantity) - Inventory/Parts
# ============================================
class ServiceTicketPart(db.Model):
    """
    Junction table for ServiceTicket and Inventory (Parts).
    Includes quantity field for tracking how many of each part is used.
    """
    __tablename__ = 'service_ticket_part'
    
    service_ticket_id = db.Column(Integer, ForeignKey('service_ticket.service_ticket_id'), primary_key=True)
    part_id = db.Column(Integer, ForeignKey('inventory.id'), primary_key=True)
    quantity = db.Column(Integer, default=1, nullable=False)
    
    # Relationships
    service_ticket = relationship('ServiceTicket', back_populates='parts')
    part = relationship('Inventory', back_populates='service_tickets')
    
    def __repr__(self):
        return f'<ServiceTicketPart ticket={self.service_ticket_id} part={self.part_id} qty={self.quantity}>'


# ============================================
# CUSTOMER MODEL
# ============================================
class Customer(db.Model):
    __tablename__ = 'customer'
    
    customer_id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    phone = db.Column(String(20), nullable=False)
    email = db.Column(String(100), unique=True, nullable=False)
    address = db.Column(String(255), nullable=False)
    password = db.Column(String(255), nullable=False)  # Password for authentication
    
    # Relationship
    vehicles = relationship('Vehicle', back_populates='customer', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'


# ============================================
# VEHICLE MODEL
# ============================================
class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    
    vehicle_id = db.Column(Integer, primary_key=True)
    customer_id = db.Column(Integer, ForeignKey('customer.customer_id'), nullable=False)
    make = db.Column(String(50), nullable=False)
    model = db.Column(String(50), nullable=False)
    year = db.Column(Integer, nullable=False)
    vin = db.Column(String(17), unique=True, nullable=False)
    
    # Relationships
    customer = relationship('Customer', back_populates='vehicles')
    service_tickets = relationship('ServiceTicket', back_populates='vehicle', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Vehicle {self.year} {self.make} {self.model}>'


# ============================================
# SERVICE TICKET MODEL
# ============================================
class ServiceTicket(db.Model):
    __tablename__ = 'service_ticket'
    
    service_ticket_id = db.Column(Integer, primary_key=True)
    vehicle_id = db.Column(Integer, ForeignKey('vehicle.vehicle_id'), nullable=False)
    date_in = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    date_out = db.Column(DateTime, nullable=True)
    description = db.Column(Text, nullable=False)
    status = db.Column(String(20), default='Open', nullable=False)  # Open, In Progress, Closed
    total_cost = db.Column(Float, default=0.0, nullable=False)
    
    # Relationships
    vehicle = relationship('Vehicle', back_populates='service_tickets')
    mechanics = relationship('Mechanic', secondary=service_ticket_mechanic, back_populates='service_tickets')
    parts = relationship('ServiceTicketPart', back_populates='service_ticket', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ServiceTicket {self.service_ticket_id} - {self.status}>'


# ============================================
# MECHANIC MODEL
# ============================================
class Mechanic(db.Model):
    __tablename__ = 'mechanic'
    
    mechanic_id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(100), nullable=False)
    address = db.Column(String(255), nullable=False)
    phone = db.Column(String(20), nullable=False)
    salary = db.Column(Float, nullable=False)
    
    # Relationship
    service_tickets = relationship('ServiceTicket', secondary=service_ticket_mechanic, back_populates='mechanics')
    
    def __repr__(self):
        return f'<Mechanic {self.name}>'


# ============================================
# INVENTORY MODEL (Parts)
# ============================================
class Inventory(db.Model):
    """
    Inventory model to track parts in stock.
    Has a many-to-many relationship with ServiceTicket through ServiceTicketPart.
    """
    __tablename__ = 'inventory'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    price = db.Column(Float, nullable=False)
    
    # Relationship (through junction table with quantity)
    service_tickets = relationship('ServiceTicketPart', back_populates='part', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Inventory {self.name} - ${self.price}>'