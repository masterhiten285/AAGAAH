from sqlalchemy import create_engine
from aagaah.config import Settings
from aagaah.db import seed
if __name__=='__main__': seed(create_engine(Settings().database_url))
