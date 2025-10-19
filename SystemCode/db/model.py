from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class HousingData(Base):
    __tablename__ = 'housing_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500))
    price = Column(Integer)
    area_sqft = Column(Float)
    build_time = Column(Integer, nullable=True)
    type = Column(String(100))
    location = Column(Text)
    distance_to_mrt = Column(Integer)
    availability = Column(Text)
    beds_num = Column(Integer)
    baths_num = Column(Integer)
    is_room = Column(Boolean)
    district_id = Column(Integer, nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)

class ImageRecord(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False, index=True)
    gcs_url = Column(Text, nullable=False)
    public_url = Column(Text, nullable=False)
    file_size = Column(BigInteger)
    content_type = Column(String(100))
    bucket_name = Column(String(255))
    gcs_path = Column(String(500))
    
    def __repr__(self):
        return f"<ImageRecord(id={self.id}, filename='{self.filename}', public_url='{self.public_url}')>"