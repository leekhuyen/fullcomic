from model.base import Base
from sqlalchemy import Column, String, Integer, Unicode

class Category(Base):
	__tablename__ = 'categories'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(Unicode)

	def __init__(self, name, description):
		self.name = name
		self.description = description

	def save_to_db(self, session):
		session.add(self)
		session.commit()
	
	@classmethod
	def find_by_name(cls, name, session):
		return session.query(Category).filter(Category.name == name).first()
