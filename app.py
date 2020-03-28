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
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, original_url):
        self.original_url = original_url
        random.seed(self.id)
        self.shortened_url = self.randomStringDigits()

    def __repr__(self):
        return '<URL %r> = %r'.format(self.id, self.shortened_url)

    @classmethod
    def randomStringDigits(self, length=6):
        random_string = string.ascii_letters + string.digits
        return ''.join(random.choice(random_string) for i in range(length))

class LinkSchema(ma.Schema):
    class Meta:
        fields = ('id', 'shortened_url', 'original_url', 'date_created')

# init schema
link_schema = LinkSchema()
links_schema = LinkSchema(many=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/shorturl/new', methods=['POST'])
def create():
    link = request.form['url']

    if validators.url(link):
        new_link = Link(original_url = link)
        try:
            db.session.add(new_link)
            db.session.commit()
            # return link_schema.jsonify(new_link)
            data = link_schema.jsonify(new_link)
            base_url = request.url_root
            final_data = str(base_url)+'api/shorturl/'+str(data.json['shortened_url'])
            return render_template('success.html', data=final_data)
        except:
            return json.jsonify(error = 'invalid URL')
    else:
        return json.jsonify(error = 'invalid URL')

@app.route('/api/shorturl/', methods=['GET'])
def get_links():
    all_links = Link.query.all()
    result = links_schema.dump(all_links)
    return jsonify(result)

@app.route('/api/shorturl/<code>', methods=['GET'])
def get_link(code):
    try:
        link_data = Link.query.filter_by(shortened_url=code).first()
        link = link_schema.jsonify(link_data)
        the_link = link.json['original_url']
        return redirect(the_link)
    except:
        return json.jsonify(error = 'invalid URL')

if __name__ == '__main__':
    app.run(debug=True)