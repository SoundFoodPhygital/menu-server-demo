"""Admin module - Flask-Admin configuration and views."""

from flask import redirect, request, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin.menu import MenuLink
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from ..extensions import cache, db
from ..models import Dish, Emotion, Menu, RequestLog, Shape, Texture, User


class AdminLoginForm(FlaskForm):
    """Form for admin login."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SecureModelView(ModelView):
    """Base model view that requires admin authentication."""

    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_auth.login", next=request.url))


class ManagerModelView(ModelView):
    """Model view for managers - read only access."""

    form_base_class = SecureForm
    can_create = False
    can_edit = False
    can_delete = False
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated and (
            current_user.is_admin or current_user.is_manager
        )

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_auth.login", next=request.url))


class UserAdminView(SecureModelView):
    """Admin view for User model."""

    column_list = ["id", "username", "is_admin", "is_manager"]
    column_searchable_list = ["username"]
    column_filters = ["is_admin", "is_manager"]
    form_excluded_columns = ["password_hash", "menus"]


class MenuAdminView(SecureModelView):
    """Admin view for Menu model."""

    column_list = ["id", "title", "description", "owner"]
    column_searchable_list = ["title"]


class RequestLogAdminView(ManagerModelView):
    """Admin view for RequestLog model - read only."""

    column_list = ["id", "timestamp", "method", "endpoint", "status_code", "user_id"]
    column_filters = ["method", "status_code", "timestamp"]
    column_default_sort = ("timestamp", True)


class MyAdminIndexView(AdminIndexView):
    """Custom admin index with dashboard."""

    def is_accessible(self):
        """Check if user can access admin."""
        return current_user.is_authenticated and (
            current_user.is_admin or current_user.is_manager
        )

    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login when access is denied."""
        return redirect(url_for("admin_auth.login", next=request.url))

    @expose("/")
    def index(self):
        # Dashboard statistics
        stats = cache.get("admin_dashboard_stats")
        if stats is None:
            stats = {
                "users": User.query.count(),
                "menus": Menu.query.count(),
                "dishes": Dish.query.count(),
                "emotions": Emotion.query.count(),
                "textures": Texture.query.count(),
                "shapes": Shape.query.count(),
                "requests": RequestLog.query.count(),
            }
            cache.set("admin_dashboard_stats", stats, timeout=600)

        # Chart data
        chart_data = cache.get("admin_chart_data")
        if chart_data is None:
            daily_counts = RequestLog.get_daily_counts(30)
            chart_data = {
                "labels": [row[0] for row in daily_counts],
                "values": [row[1] for row in daily_counts],
            }
            cache.set("admin_chart_data", chart_data, timeout=600)

        # Recent activity
        recent_logs = cache.get("admin_recent_logs")
        if recent_logs is None:
            recent_logs = RequestLog.get_recent(10)
            cache.set("admin_recent_logs", recent_logs, timeout=60)

        return self.render(
            "admin/custom_index.html",
            stats=stats,
            recent_logs=recent_logs,
            chart_labels=chart_data["labels"],
            chart_values=chart_data["values"],
        )


def init_admin(app):
    """Initialize Flask-Admin with all views."""
    admin = Admin(app, name="SoundFood Admin", index_view=MyAdminIndexView())

    # Add model views
    admin.add_view(UserAdminView(User, db.session, name="Users"))
    admin.add_view(MenuAdminView(Menu, db.session, name="Menus"))
    admin.add_view(SecureModelView(Dish, db.session, name="Dishes"))
    admin.add_view(
        SecureModelView(
            Emotion,
            db.session,
            name="Emotions",
            category="Attributes",
        )
    )
    admin.add_view(
        SecureModelView(
            Texture,
            db.session,
            name="Textures",
            category="Attributes",
        )
    )
    admin.add_view(
        SecureModelView(
            Shape,
            db.session,
            name="Shapes",
            category="Attributes",
        )
    )
    admin.add_view(RequestLogAdminView(RequestLog, db.session, name="Request Logs"))
    admin.add_link(MenuLink(name="Logout", url="/admin/logout"))

    return admin
