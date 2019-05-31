from model.base import Base
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship

categories_comics_association = Table(
	'categories_comics', Base.metadata,
	Column('categoryId', Integer, ForeignKey('categories.id')),
	Column('comicId', Integer, ForeignKey('comics.id'))
	)


class Comic(Base):
	"""docstring for Comic"""
	__tablename__ = 'comics'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	link = Column(String)
	description = Column(String)
	writer = Column(String)
	source = Column(String)
	status = Column(String)
	rating = Column(Float)
	ratingNumber = Column(Integer)
	imageLink = Column(String)
	categories = relationship('Category', secondary=categories_comics_association)
	chapters = relationship('Chapter')

	def __init__(self, name, description, writer, source, status, rating, rating_number, image_link, linkName):
		self.name = name
		self.description = description
		self.writer = writer
		self.source = source
		self.status = status
		self.rating = rating
		self.ratingNumber = rating_number
		self.imageLink = image_link
		self.link = linkName

	def save_to_db(self, session):
		session.add(self)
		session.commit()

	@classmethod
	def find_by_name(cls, name, session):
		return session.query(Comic).filter(Comic.name == name).first()

	@classmethod
	def find_by_link(cls, link, session):
		return  session.query(Comic).filter(Comic.link == link).first()
