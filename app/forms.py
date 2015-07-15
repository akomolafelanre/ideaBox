from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange
from app.models import User

class LoginForm(Form):
	openid = StringField('openid', validators = [DataRequired()])
	remember_me = BooleanField('remember_me', default = False)

class EditForm(Form):
	nickname = StringField('nickname', validators = [DataRequired()])
	about_me = TextAreaField('about_me', validators = [Length(min=0, max= 500)])

	def __init__(self, original_nickname, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_nickname = original_nickname
	
	def validate(self):
		if not Form.validate(self):
			return False
		if self.nickname.data == self.original_nickname:
			return True
		user = User.query.filter_by(nickname=self.nickname.data).first()
		if user != None:
			self.nickname.errors.append('This nickname is already in use. Please choose another one.')
			return False
		return True

class IdeaForm(Form):
	title = StringField('title', validators = [DataRequired()])
	description = TextAreaField('description', validators = [DataRequired(), Length(min=0, max= 500)])
	rank = IntegerField('rank', validators = [DataRequired(), NumberRange(min = 0, max = 5, message = "Out of range")])

class SearchForm(Form):
	search = StringField('search', validators = [DataRequired()])
