from sqlalchemy import Integer, Text, Column

from test_bot.db.base_class import Base


class Girl(Base):
    __tablename__ = "girl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(Text, nullable=False)
    account_type = Column(Integer, nullable=False)
