# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify
)
from flask_login import login_required, login_user, logout_user

from sprocket_factory.extensions import login_manager, db
from sprocket_factory.public.forms import LoginForm
from .models import Factory, Sprocket
from .forms import CreateSprocketForm
from sprocket_factory.user.forms import RegisterForm
from sprocket_factory.user.models import User
from sprocket_factory.utils import flash_errors


blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)

# Get list of factories
@blueprint.route('/factories', methods=["GET"])
def get_factories():
    data = Factory.query.all()
    return jsonify([{'id': d.id, 'chart_data': d.chart_data} for d in data])

# Get factory by id
@blueprint.route('/factories/<int:f_id>', methods=["GET"])
def get_factory_by_id(f_id):
    factories = Factory.query.filter_by(id=f_id).all()
    return jsonify([{'id': factory.id, 'chart_data': factory.chart_data} for factory in factories])

#get list of sprockets
@blueprint.route('/sprockets/<int:s_id>', methods=["GET"])
def get_sprocket_by_id(s_id):
    sprockets = Sprocket.query.filter_by(id=s_id).all()
    return jsonify([{'id':sprocket.id, 'teeth': sprocket.teeth, 'pitch_diameter': sprocket.pitch_diameter, 'outside_diameter': sprocket.outside_diameter, 'pitch': sprocket.pitch} for sprocket in sprockets])

#create new sprocket
@blueprint.route("/sprockets/create/", methods=["GET", "POST"])
def create():
    """Register new sprocket."""
    form = CreateSprocketForm(request.form)    
    if form.validate_on_submit():
        s = Sprocket(
            id=form.id.data,
            teeth=form.teeth.data,
            pitch_diameter=form.pitch_diameter.data,
            outside_diameter=form.outside_diameter.data,
            pitch=form.pitch.data,
        )
        db.session.add(s)
        db.session.commit()
        flash('Sprocket created successfully!')
        return redirect(f"/sprockets/{form.id.data}")
    else:
        flash_errors(form)
    return render_template("public/create.html", title ="Create Sprocket", form=form, legend='Create sprocket')

#Update existing sprocket
@blueprint.route("/sprockets/<int:s_id>/update", methods=["GET", "POST"])
def edit(s_id):
    """update existing sprocket."""
    post = Sprocket.query.get_or_404(s_id)
    form = CreateSprocketForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(f"/sprockets/{form.id.data}")
    else:
        flash_errors(form)
    return render_template("public/create.html", title='Update sprocket', form=form, legend='Update sprocket')
