# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object


# схема БД
metadata = MetaData()
Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)
    

# добавление записи в бд
def add_user (profile_id, worksheet_id):
    engine = create_engine(db_url_object)
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()

# извлечение записей из БД

#engine = create_engine(db_url_object)
def check_user (profile_id, worksheet_id):
    engine = create_engine(db_url_object)
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.profile_id==profile_id,
            Viewed.worksheet_id==worksheet_id
        #    ).all()
        #for item in from_bd:
         #   print(item.worksheet_id)
         ).first()
        return True if from_bd else False
    
if __name__ == '__main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    add_user(1234545, 456)
    res = check_user(engine, 1234545, 456)
    print (res)
