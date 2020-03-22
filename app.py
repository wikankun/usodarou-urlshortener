from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortener.db'
# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, link):
        self.link = link

    def __repr__(self):
        return '<Link %r>' % self.id

class LinkSchema(ma.Schema):
    class Meta:
        fields = ('id', 'link', 'date_created')

# init schema
link_schema = LinkSchema()
links_schema = LinkSchema(many=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/shorturl/new', methods=['POST'])
def create():
    link = request.form['url']
    pattern = r"^(?:http(s)?:\/\/)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
    matched = re.match(pattern, link)

    if matched:
        new_link = Link(link = link)
        try:
            db.session.add(new_link)
            db.session.commit()
            # return link_schema.jsonify(new_link)
            data = link_schema.jsonify(new_link)
            base_url = request.url_root
            final_data = str(base_url)+'api/shorturl/'+str(data.json['id'])
            return render_template('success.html', data=final_data)
        except:
            return json.jsonify(error = 'invalid URL')
    else:
        return json.jsonify(error = 'invalid URL')

@app.route('/api/shorturl', methods=['GET'])
def get_links():
    all_links = Link.query.all()
    result = links_schema.dump(all_links)
    return jsonify(result)

@app.route('/api/shorturl/<id>', methods=['GET'])
def get_link(id):
    try:
        link_data = Link.query.get(id)
        link = link_schema.jsonify(link_data)
        the_link = link.json['link']
        return redirect(the_link)
    except:
        return json.jsonify(error = 'invalid URL')

if __name__ == '__main__':
    app.run(debug=True)