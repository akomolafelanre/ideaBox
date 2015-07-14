from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), index= True, unique= True)
	email = db.Column(db.String(120), index = True, unique = True)
	ideas = db.relationship('Idea', backref = 'author', lazy = 'dynamic')

	def __repr__(self):
		return '<User %r>' % (self.nickname)

class Idea(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(120), index = True, unique = True)
	description = db.Column(db.String(200))
	rank = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Idea %r>' % (self.description)


