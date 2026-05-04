from app.core.database import Base, get_engine
import app.models  # ensures models are registered


def init_db():
    Base.metadata.create_all(bind=get_engine())
