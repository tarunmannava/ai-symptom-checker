from database import engine, Base
from models import Condition, Symptom, MedicalRule

Base.metadata.create_all(bind=engine)
print("Tables created successfully!")