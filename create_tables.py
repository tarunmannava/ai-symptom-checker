from sqlalchemy import inspect
from app.database import engine, Base
from app.models import Condition, Symptom, MedicalRule

def check_tables_exist():
    """Check if tables already exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    expected_tables = ['conditions', 'symptoms', 'medical_rules', 'symptom_condition_mappings']
    
    for table in expected_tables:
        if table in existing_tables:
            print(f"{table} already exists")
        else:
            print(f"{table} missing")
    
    return all(table in existing_tables for table in expected_tables)

def create_tables():
    """Create tables only if they don't exist"""
    if check_tables_exist():
        print("All tables already exist - no action needed")
        return
    
    print("Creating missing tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()