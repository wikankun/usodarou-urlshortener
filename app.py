from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import validators
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortener.db'
# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shortened_url = db.Column(db.String(200), nullable=False)
    original_url = db.Column(db.String(200), nullable=False)
    times_accessed = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, original_url):
        self.original_url = original_url
        random.seed(self.id)
        self.shortened_url = self.randomStringDigits()
        self.times_accessed = 0

    def __repr__(self):
        return '<URL {}> = {}'.format(self.id, self.shortened_url)

    @classmethod
    def randomStringDigits(self, length=6):
        random_string = string.ascii_letters + string.digits
        return ''.join(random.choice(random_string) for i in range(length))

class LinkSchema(ma.Schema):
    class Meta:
        fields = ('id', 'shortened_url', 'original_url', 'times_accessed', 'date_created')

# init schema
link_schema = LinkSchema()
links_schema = LinkSchema(many=True)

'''
Below are the code to consume API
'''
@app.route('/')
def index():
    resp = get_links()
    try:
    	data = resp.json[-1]['id']
    except:
    	data = 0
    return render_template('index.html', data=data)

@app.route('/create', methods=['POST'])
def create():
    resp = create_link()
    if resp.status_code == 201:
        return render_template('success.html', data=resp.json['final_url'])
    else:
        return resp

@app.route('/<code>', methods=['GET'])
def get(code):
    resp = get_link(code)
    if resp.status_code == 200:
        accessed_plus_one(code)
        return redirect(resp.json['original_url'])
    else:
        return resp

@app.route('/<code>/edit', methods=['GET'])
def edit(code):
    resp = get_link(code)
    if resp.status_code == 200:
        return render_template('edit.html', data=resp.json['shortened_url'])
    else:
        return resp

@app.route('/<code>/detail', methods=['GET'])
def detail(code):
    resp = get_link(code)
    if resp.status_code == 200:
        return render_template('detail.html', data=resp.json)
    else:
        return resp

'''
Below are some specific functions
'''
def accessed_plus_one(code):
    link = Link.query.filter_by(shortened_url=code).first()
    link.times_accessed += 1
    db.session.commit()

'''
Below are API code
'''
@app.route('/api/shorturl/new', methods=['POST'])
def create_link():
    link = request.form['url']

    if validators.url(link):
        new_link = Link(original_url = link)
        try:
            db.session.add(new_link)
            db.session.commit()
            data = link_schema.jsonify(new_link)

            data = data.json
            base_url = request.url_root
            final_url = str(base_url)+str(data['shortened_url'])
            final_data = {
                'url': data,
                'final_url': final_url
            }
            return make_response(jsonify(final_data), 201)
        except:
            db.session.rollback()
            db.session.remove()
            return make_response(jsonify(error = 'Oops something went wrong'), 400)
    else:
        return make_response(jsonify(error = 'Invalid URL'), 400)

@app.route('/api/shorturl/', methods=['GET'])
def get_links():
    all_links = Link.query.all()
    result = links_schema.dump(all_links)
    return make_response(jsonify(result), 200)

@app.route('/api/shorturl/<code>', methods=['GET'])
def get_link(code):
    try:
        link = Link.query.filter_by(shortened_url=code).first()
        if link != None:
            data = link_schema.jsonify(link)
            return make_response(data, 200)
        else:
            return make_response(jsonify(error = 'Not found'), 404)
    except:
        return make_response(jsonify(error = 'Invalid URL'), 400)

@app.route('/api/shorturl/<code>', methods=['POST', 'PUT'])
def edit_link(code):
    try:
        link = Link.query.filter_by(shortened_url=code).first()

        link.shortened_url = request.form['url']
        db.session.commit()

        data = link_schema.jsonify(link)
        data = data.json
        base_url = request.url_root
        final_url = str(base_url)+str(data['shortened_url'])
        final_data = {
            'url': data,
            'final_url': final_url
        }
        return make_response(jsonify(final_data), 200)
    except:
        return make_response(jsonify(error = 'Not found'), 404)

if __name__ == '__main__':
    app.run(debug=True)