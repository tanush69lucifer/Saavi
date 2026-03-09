from database import SessionLocal, User, UserRole

def seed():
    db = SessionLocal()
    
    # Check if patient exists
    p = db.query(User).filter(User.email == "patient@neuro.com").first()
    if not p:
        print("Creating patient@neuro.com...")
        db.add(User(
            name="Test Patient",
            email="patient@neuro.com",
            hashed_password="password123",
            role=UserRole.patient
        ))
    
    # Check if family exists
    f = db.query(User).filter(User.email == "family@neuro.com").first()
    if not f:
        print("Creating family@neuro.com...")
        db.add(User(
            name="Test Family",
            email="family@neuro.com",
            hashed_password="password123",
            role=UserRole.family
        ))
    
    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
