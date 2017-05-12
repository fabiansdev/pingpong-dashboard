# Python
import binascii
import hashlib
import datetime
import pytz

# SQLAlchemy
from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Index, Integer, LargeBinary, Numeric, String, Table,
                        Text, UniqueConstraint, text)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

def init_db(engine):
    Base.metadata.create_all(bind=engine)

def now():
    return datetime.datetime.now(tz=pytz.utc)


class UserUser(Base):
    __tablename__ = 'user_user'

    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False, unique=True)
    username = Column(String(64), nullable=False, unique=True)
    score = Column(Float(50))
    password_crypt = Column(String(256), nullable=False)
    token = Column(String(256))
    created_date = Column(DateTime, default=now())

    def check_hash(self, password):
        derived_key = hashlib.pbkdf2_hmac('sha256', password, b'salt', 100000)
        derived_key = binascii.hexlify(derived_key)
        if derived_key == self.password_crypt:
            return True
        else:
            return False


class UserGame(Base):
    __tablename__ = 'user_game'

    id = Column(Integer, primary_key=True)
    player_one_id = Column(Integer, ForeignKey('user_user.id'), nullable=False)
    player_two_id = Column(Integer, ForeignKey('user_user.id'), nullable=False)
    score_one = Column(Integer(53))
    score_two = Column(Integer(53))
    player_one = relationship("UserUser", foreign_keys=[player_one_id])
    player_two = relationship("UserUser", foreign_keys=[player_two_id])
    created_date = Column(DateTime, default=now())

    def get_score(self):
        score_one = str(self.score_one)
        score_two = str(self.score_two)
        return score_one+"-"score_two