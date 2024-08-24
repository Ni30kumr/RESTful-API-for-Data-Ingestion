from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base



URL_DATABASE='mysql+pymysql://root:nitesh1234@localhost:3306/csv_reader'
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()