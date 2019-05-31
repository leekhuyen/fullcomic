import  threading
import  time
import sys
sys.path.append('comic_lib')
from model.category import Category
from model.chapter import Chapter
from model.comic import Comic
from model.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('sqlite:///./fullcomic.db')
Session = scoped_session(sessionmaker(bind=engine))

Base.metadata.create_all(engine)

session1 = Session()
session2 = Session()

def worker1():
    i = 1
    while True:
        print(f'worker1 {threading.get_ident()} {i}')
        name = session1.query(Comic).filter().first().name
        print(f'name: {name}')
        if i == 1:
            break
        time.sleep(3)
        i += 1

def worker2():
    global session2;
    i = 1
    while True:
        print(f'worker2 {threading.get_ident()} {i}')
        name = session2.query(Comic).filter().first().link
        print(f'name: {name}')
        if i == 3:
            if session2 == session1:
                print('is')
            else:
                print('not is')
            Session.remove()
            session2 = Session()
        elif i > 3:
            if session2 == session1:
                print('is')
            else:
                print('not is')

        time.sleep(3)
        i += 1

print(f'main thread {threading.get_ident()}')

t = threading.Thread(target=worker1)
t.start()

k = threading.Thread(target=worker2)
k.start()