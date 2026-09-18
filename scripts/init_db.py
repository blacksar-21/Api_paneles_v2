from app.database.database import engine
from app.models.models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas (si no existían).")

if __name__ == "__main__":
    init_db()