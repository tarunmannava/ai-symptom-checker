from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


symptom_condition_mapping = Table(
    'symptom_condition_mappings',
    Base.metadata,
    Column('symptom_id', Integer, ForeignKey('symptoms.id'), primary_key=True),
    Column('condition_id', Integer, ForeignKey('conditions.id'), primary_key=True),
    Column('strength', Float, default=0.5)  # How strongly they're related (0-1)
)

class Condition(Base):
    """Medical conditions that can be diagnosed"""
    __tablename__ = "conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100))  # respiratory, gi, neurological
    emergency_level = Column(String(20), default="low")  # low, medium, high, critical
    description = Column(Text)
    
    # External API integration
    infermedica_isd = Column(String(100), unique=True)
    
    # Simple fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    symptoms = relationship("Symptom", secondary=symptom_condition_mapping, back_populates="conditions")

class Symptom(Base):
    """Symptoms that users can report"""
    __tablename__ = "symptoms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100))  # respiratory, gi, neurological, general
    description = Column(Text)
    
    # External API integration
    infermedica_id = Column(String(100), unique=True)
    
    # Simple fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conditions = relationship("Condition", secondary=symptom_condition_mapping, back_populates="symptoms")

class SymptomSession(Base):
    """Each symptom analysis session"""
    __tablename__ = "symptom_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User info (simple - no separate user table for now)
    user_age = Column(Integer)
    user_gender = Column(String(20))
    
    # Input and results
    symptoms_input = Column(JSON)  # What user reported
    predictions = Column(JSON)     # AI/ML results
    confidence = Column(Float)     # Overall confidence
    urgency = Column(String(20))   # low, medium, high, emergency
    
    # Simple tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

class MedicalRule(Base):
    """Simple medical decision rules"""
    __tablename__ = "medical_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    condition_id = Column(Integer, ForeignKey("conditions.id"))
    
    rule_type = Column(String(50))  # emergency, diagnostic
    rule_name = Column(String(255))
    rule_data = Column(JSON)        # Simple rule conditions
    confidence = Column(Float, default=0.5)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    condition = relationship("Condition")


class APICall(Base):
    """Track external API usage"""
    __tablename__ = "api_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("symptom_sessions.id"))
    
    provider = Column(String(50))  # infermedica, nih
    endpoint = Column(String(255))
    response_time = Column(Integer)  # milliseconds
    cost = Column(Float)
    
    called_at = Column(DateTime(timezone=True), server_default=func.now())