import pandas as pd
import json
from sqlalchemy import text
from app.database import SessionLocal
from app.models import Condition, Symptom, MedicalRule, symptom_condition_mapping

def check_existing_data():
    """Check if data already exists in tables"""
    db = SessionLocal()
    
    try:
        condition_count = db.query(Condition).count()
        symptom_count = db.query(Symptom).count()
        rule_count = db.query(MedicalRule).count()
        mapping_count = db.execute(text("SELECT COUNT(*) FROM symptom_condition_mappings")).scalar()
        
        return {
            'conditions': condition_count,
            'symptoms': symptom_count,
            'rules': rule_count,
            'mappings': mapping_count
        }
    except Exception as e:
        print(f"Error checking existing data: {e}")
        return None
    finally:
        db.close()

def load_all_data():
    """Load all CSV data into database tables (only if tables are empty)"""
    print("🚀 Checking database before loading...")
    
    # Check existing data first
    existing_data = check_existing_data()
    if existing_data is None:
        print("Could not check existing data")
        return
    
    # Show current state
    print("Current database state:")
    for table, count in existing_data.items():
        print(f"  {table}: {count} records")
    
    # Check if any data exists
    total_records = sum(existing_data.values())
    if total_records > 0:
        print(f"\n Database already contains {total_records} records")
        response = input("Do you want to proceed anyway? This will add more data (y/n): ")
        if response.lower() != 'y':
            print("Cancelled - existing data preserved")
            return
        print("Proceeding with data loading...")
    else:
        print("Database is empty, proceeding with data loading...")
    
    db = SessionLocal()
    
    try:
        # 1. Load Conditions (only new ones)
        print("\nLoading conditions...")
        conditions_df = pd.read_csv('data/conditions.csv')
        new_conditions = 0
        
        for _, row in conditions_df.iterrows():
            # Check if condition already exists
            existing = db.query(Condition).filter(Condition.name == row['name']).first()
            if not existing:
                condition = Condition(
                    name=row['name'],
                    category=row['category'],
                    emergency_level=row['emergency_level'],
                    description=row['description']
                )
                db.add(condition)
                new_conditions += 1
        
        db.commit()
        print(f"Added {new_conditions} new conditions (skipped {len(conditions_df) - new_conditions} existing)")
        
        # 2. Load Symptoms (only new ones)
        print("Loading symptoms...")
        symptoms_df = pd.read_csv('data/symptoms.csv')
        new_symptoms = 0
        
        for _, row in symptoms_df.iterrows():
            # Check if symptom already exists
            existing = db.query(Symptom).filter(Symptom.name == row['name']).first()
            if not existing:
                symptom = Symptom(
                    name=row['name'],
                    category=row['category'],
                    description=row['description']
                )
                db.add(symptom)
                new_symptoms += 1
        
        db.commit()
        print(f"Added {new_symptoms} new symptoms (skipped {len(symptoms_df) - new_symptoms} existing)")
        
        # 3. Load Symptom-Condition Mappings (only new ones)
        print("Loading symptom-condition mappings...")
        mappings_df = pd.read_csv('data/symptom_condition_mappings.csv')
        new_mappings = 0
        
        for _, row in mappings_df.iterrows():
            symptom = db.query(Symptom).filter(Symptom.name == row['symptom_name']).first()
            condition = db.query(Condition).filter(Condition.name == row['condition_name']).first()
            
            if symptom and condition:
                # Check if mapping already exists
                existing = db.execute(text("""
                    SELECT COUNT(*) FROM symptom_condition_mappings 
                    WHERE symptom_id = :symptom_id AND condition_id = :condition_id
                """), {'symptom_id': symptom.id, 'condition_id': condition.id}).scalar()
                
                if existing == 0:
                    stmt = symptom_condition_mapping.insert().values(
                        symptom_id=symptom.id,
                        condition_id=condition.id,
                        strength=float(row['strength'])
                    )
                    db.execute(stmt)
                    new_mappings += 1
            else:
                print(f"Could not find symptom '{row['symptom_name']}' or condition '{row['condition_name']}'")
        
        db.commit()
        print(f"Added {new_mappings} new mappings (skipped {len(mappings_df) - new_mappings} existing)")
        
        # 4. Load Medical Rules (only new ones)
        print("Loading medical rules...")
        rules_df = pd.read_csv('data/medical_rules.csv')
        new_rules = 0
        
        for _, row in rules_df.iterrows():
            condition = db.query(Condition).filter(Condition.name == row['condition_name']).first()
            if condition:
                # Check if rule already exists
                existing = db.query(MedicalRule).filter(
                    MedicalRule.condition_id == condition.id,
                    MedicalRule.rule_name == row['rule_name']
                ).first()
                
                if not existing:
                    rule = MedicalRule(
                        condition_id=condition.id,
                        rule_type=row['rule_type'],
                        rule_name=row['rule_name'],
                        rule_data=json.loads(row['rule_data']),
                        confidence=float(row['confidence'])
                    )
                    db.add(rule)
                    new_rules += 1
        
        db.commit()
        print(f"Added {new_rules} new rules (skipped {len(rules_df) - new_rules} existing)")
        
        # 5. Final verification
        print("\nFinal database state:")
        final_data = check_existing_data()
        for table, count in final_data.items():
            print(f"  {table}: {count} records")
        
        total_new = new_conditions + new_symptoms + new_mappings + new_rules
        if total_new > 0:
            print(f"\n Successfully added {total_new} new records!")
        else:
            print(f"\n All data was already present - no duplicates created!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_all_data()