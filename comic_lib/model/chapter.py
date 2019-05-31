from model.base import Base
from sqlalchemy import String, Integer, Column, ForeignKey
from model.comic import Comic

class Chapter(Base):
	__tablename__ = 'chapters'

	id = Column(Integer, primary_key = True)
	comicId = Column(Integer, ForeignKey('comics.id'))
	book = Column(String)
	chapter = Column(String)
	name = Column(String)
	link = Column(String)
	content = Column(String)

	def __init__(self, chapter_number, chapter_name, content, nameLink, book):
		self.chapter = chapter_number
		self.name = chapter_name
		self.content = content
		self.link = nameLink
		self.book = book

	def save_to_db(self, session):
		session.add(self)
		session.commit()

	@classmethod
	def find_by_number(cls, comic_id, number, session):
		return session.query(Chapter).join(Chapter, Comic.chapters)\
			.filter(Comic.id == comic_id)\
			.filter(Chapter.chapter == number)\
			.first()
