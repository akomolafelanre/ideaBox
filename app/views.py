from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from datetime import datetime
from app import app, db, lm, oid
from .forms import LoginForm, EditForm, IdeaForm, SearchForm
from .models import User, Idea
from config import MAX_SEARCH_RESULTS


@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		g.search_form = SearchForm()

@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html'), 500

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
	form = IdeaForm()
	if form.validate_on_submit():
		idea = Idea(title = form.title.data, description = form.description.data, rank = int(form.rank.data), timestamp= datetime.utcnow(), author = g.user)
		db.session.add(idea)
		db.session.commit()
		flash('Your idea has been captured')
		return redirect(url_for('index'))
	ideas =	g.user.user_ideas().all()

	return render_template('index.html', 
							title = 'Home', 
							form = form,
							ideas = ideas)

@app.route('/login', methods= ['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
	return render_template('login.html',
							title = 'Sign In',
							form = form,
							providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	#user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash('User %s not found.' % (nickname))
		return redirect(url_for('index'))
	ideas = user.ideas
	
	return render_template('user.html', user=user, ideas=ideas)	

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    idea = Idea.query.get(id)
    if idea is None:
        flash('Idea not found.')
        return redirect(url_for('index'))
    if idea.author.id != g.user.id:
        flash('You cannot delete this idea.')
        return redirect(url_for('index'))
    db.session.delete(idea)
    db.session.commit()
    flash('Your idea has been deleted.')
    return redirect(url_for('index'))

@app.route('/editpost/<int:id>')
@login_required
def editidea(id):
    idea = Idea.query.get(id)
    if idea is None:
        flash('Idea not found.')
        return redirect(url_for('index'))
    if idea.author.id != g.user.id:
        flash('You cannot edit this idea.')
        return redirect(url_for('index'))
    idea.title += "plus some extra"
    idea.timestamp= datetime.utcnow()
    db.session.commit()
    flash('Your idea has been edited.')
    return redirect(url_for('index'))

@app.route('/like/<int:id>')
@login_required
def like(id):
    idea = Idea.query.get(id)
    if idea is None:
        flash('Idea not found.')
        return redirect(url_for('index'))
    idea.rank += 1
    db.session.commit()
    flash('Thanks for liking my idea. Lets make it work!!')
    return redirect(url_for('index'))

@app.route('/search', methods = ['POST'])
@login_required
def search():
	if not g.search_form.validate_on_submit():
		return redirect(url_for('index'))
	return redirect(url_for('search_results', query= g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
	results = Idea.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
	return render_template('search_results.html', query = query, results = results)