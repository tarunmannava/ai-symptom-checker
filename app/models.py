from sqlalchemy import Column,Integer,String,Text,Float,Boolean,DateTime, JSON,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
class Condition(Base):
    __tablename__="conditions"
    id= Column(Integer,primary_key=True,index=True)
    name=Column(String(100),nullable=False)
    category=Column(String) # respiratory, gastrointestinal, neurological, etc.
    specialty=Column(String) # emergency, primary care, etc.
    description=Column(Text,nullable=True)

class Symptom(Base):
    __tablename__="symptoms"
    id= Column(Integer,primary_key=True,index=True)
    name= Column(String,unique=True,index=True)
    category=Column(String) # respiratory, gastrointestinal, neurological, etc.
    severity_scale=Column(String,default="1-10")

class MedicalRule(Base):
    __tablename__="medical_rules"
    id= Column(Integer,primary_key=True,index=True)
    condition_id=Column(Integer,ForeignKey("conditions.id"))
    rule_type= Column(String) #emergency, diagnostic, treatment
    rule_data= Column(JSON)
    confidence= Column(Float,default=0.5) # confidence level of the rule
    priority= Column(Integer,default=1)



