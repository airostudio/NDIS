"""
Database Models for Cheryl
SQLAlchemy ORM models for data persistence
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Employee(Base):
    """Employee/Worker record"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    classification = Column(String(10))  # SCHADS classification
    employment_type = Column(String(20))  # full-time, part-time, casual
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Compliance
    ndis_screening_number = Column(String(50))
    ndis_screening_expiry = Column(DateTime)
    wwcc_number = Column(String(50))
    wwcc_expiry = Column(DateTime)
    first_aid_expiry = Column(DateTime)
    cpr_expiry = Column(DateTime)
    police_check_date = Column(DateTime)

    # Relationships
    timesheets = relationship("Timesheet", back_populates="employee")
    leave_records = relationship("LeaveRecord", back_populates="employee")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Timesheet(Base):
    """Timesheet entry"""
    __tablename__ = "timesheets"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    shift_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    break_minutes = Column(Integer, default=0)

    is_public_holiday = Column(Boolean, default=False)
    is_sleepover = Column(Boolean, default=False)
    is_broken_shift = Column(Boolean, default=False)
    travel_km = Column(Float, default=0)

    # Calculated fields
    ordinary_hours = Column(Float)
    penalty_hours = Column(Float)
    ordinary_pay = Column(Float)
    penalty_pay = Column(Float)
    allowances = Column(Float)
    gross_pay = Column(Float)

    # NDIS billing
    participant_ndis_number = Column(String(20))
    support_item_number = Column(String(20))

    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    status = Column(String(20), default="pending")  # pending, approved, paid

    employee = relationship("Employee", back_populates="timesheets")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LeaveRecord(Base):
    """Leave record"""
    __tablename__ = "leave_records"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    leave_type = Column(String(50), nullable=False)  # annual, sick, carer, etc.
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    hours = Column(Float, nullable=False)

    status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_by = Column(String(100))
    approved_at = Column(DateTime)

    employee = relationship("Employee", back_populates="leave_records")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Appointment(Base):
    """Calendar appointment"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255))

    organizer = Column(String(255))
    attendees = Column(JSON)  # List of attendees

    reminder_sent = Column(Boolean, default=False)
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Contact(Base):
    """Contact/relationship record"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    company = Column(String(255))
    role = Column(String(100))

    birthday = Column(DateTime)
    notes = Column(Text)
    tags = Column(JSON)  # List of tags

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(Base):
    """Task/todo item"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="pending")  # pending, in_progress, completed

    assigned_to = Column(String(100))
    due_date = Column(DateTime)
    completed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Incident(Base):
    """Incident report"""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    incident_date = Column(DateTime, nullable=False)
    incident_type = Column(String(100), nullable=False)
    severity = Column(String(20))  # low, medium, high, critical

    description = Column(Text, nullable=False)
    location = Column(String(255))
    people_involved = Column(JSON)
    witnesses = Column(JSON)

    immediate_action_taken = Column(Text)
    reported_to_ndis = Column(Boolean, default=False)
    reported_at = Column(DateTime)

    status = Column(String(20), default="open")  # open, investigating, closed

    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit log for all actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(100))
    action = Column(String(100), nullable=False)
    module = Column(String(50))
    details = Column(JSON)
    ip_address = Column(String(45))

    created_at = Column(DateTime, default=datetime.utcnow)
