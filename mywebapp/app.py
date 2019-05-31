from flask import Flask,jsonify,request,render_template
import sys
sys.path.append('../comic_lib')
from model.category import Category
from model.chapter import Chapter
from model.comic import Comic
from model.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import threading
from utility.utility import convert, remove_special_character

engine = create_engine('sqlite:///../fullcomic.db')
Base.metadata.create_all(engine)

Session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
app.config['url'] = '127.0.0.1/'
app.config['domain'] = 'truyenlee'

@app.template_filter()
def get_eng_name(name):
    s = convert(name)
    return remove_special_character(s)

@app.route('/')
def home():
    print(f'home {threading.get_ident()}')
    return 'not founddddddddd'

@app.route('/<string:comicNameLink>/')
def comic(comicNameLink):
    #print(f'comic threading {threading.get_ident()}, comic:{comicNameLink}, url:{request.url}')
    session = Session()
    #find comic by linkName
    tmp_comic = Comic.find_by_link(comicNameLink, session)

    if tmp_comic is not None:
        # find get index, default = 1
        page = request.args.get('page', default=1, type=int)
        # calculate total, leftIndex, rightIndex, list1, list2
        total_chapters = len(tmp_comic.chapters)
        if total_chapters % 50 == 0:
            total = total_chapters // 50
        else:
            total = total_chapters // 50 + 1

        if page > total:
            page = total

        if page - 3 <= 1:
            left_index = 1
            right_index = 7
        else:
            left_index = page - 3
            right_index = left_index + 6

        if right_index > total:
            right_index = total

        print(f'page {page} total {total} leftIndex  {left_index} rightIndex {right_index}')

        start = (page - 1)*50
        end = start + 24
        if end > total_chapters:
            end = total_chapters

        list1 = tmp_comic.chapters[start:end]
        if end + 1 < total_chapters:
            start = end + 1
            end = start + 24
            if end > total_chapters:
                end = total_chapters
            list2 = tmp_comic.chapters[start:end]
        else:
            list2 = []
        return render_template("comic.html", comic = tmp_comic, total = total, leftIndex = left_index,\
                               rightIndex = right_index, chapterList1 = list1, chapterList2 = list2, index = page)
    else:
        Session.remove()
        return "not found"


@app.route('/<string:comicName>/<string:chapterName>/')
def chapter(comicName, chapterName):
    return 'not found'

@app.route('/ajax.php' , methods=['POST'])
def ajaxphp():
    request_data = request.get_json()
    print(f'type {request.headers}')
    print(f'data {request.form}')
    return "ajaxphp"

app.jinja_env.filters['get_eng_name'] = get_eng_name
app.run(port=5000, threaded=True)
