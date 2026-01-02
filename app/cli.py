"""CLI commands for the application."""

import click
from flask import Flask
from flask.cli import with_appcontext

from .extensions import db
from .models import User


def init_cli(app: Flask):
    """Register CLI commands with the Flask app."""

    @app.cli.command("create-user")
    @click.argument("username")
    @click.option(
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="User password",
    )
    @click.option(
        "--role",
        type=click.Choice(["user", "manager", "admin"]),
        default="user",
        help="User role",
    )
    @with_appcontext
    def create_user(username: str, password: str, role: str):
        """Create a new user with specified role.

        Usage:
            flask create-user USERNAME --role admin
            flask create-user USERNAME --role manager
            flask create-user USERNAME
        """
        if User.get_by_username(username):
            click.echo(f"Error: User '{username}' already exists.", err=True)
            return

        is_admin = role == "admin"
        is_manager = role in ("admin", "manager")

        user = User.create(
            username=username,
            password=password,
            is_admin=is_admin,
            is_manager=is_manager,
        )

        click.echo(f"✓ User '{username}' created successfully with role '{role}'.")
        click.echo(f"  ID: {user.id}")
        click.echo(f"  Admin: {user.is_admin}")
        click.echo(f"  Manager: {user.is_manager}")

    @app.cli.command("list-users")
    @with_appcontext
    def list_users():
        """List all users."""
        users = User.query.all()
        if not users:
            click.echo("No users found.")
            return

        click.echo(f"{'ID':<5} {'Username':<20} {'Role':<10}")
        click.echo("-" * 35)
        for user in users:
            click.echo(f"{user.id:<5} {user.username:<20} {user.role:<10}")

    @app.cli.command("seed-attributes")
    @with_appcontext
    def seed_attributes():
        """Seed default emotions, textures, and shapes."""
        from .models import Emotion, Texture, Shape

        emotions = [
            "happy",
            "sad",
            "excited",
            "calm",
            "nostalgic",
            "romantic",
            "energetic",
            "peaceful",
            "adventurous",
        ]

        textures = [
            "crispy",
            "creamy",
            "crunchy",
            "smooth",
            "chewy",
            "tender",
            "flaky",
            "silky",
            "grainy",
            "velvety",
        ]

        shapes = [
            "round",
            "square",
            "triangular",
            "irregular",
            "spiral",
            "long",
            "flat",
            "cubed",
            "cylindrical",
        ]

        for name in emotions:
            if not Emotion.query.filter_by(name=name).first():
                db.session.add(Emotion(name=name))

        for name in textures:
            if not Texture.query.filter_by(name=name).first():
                db.session.add(Texture(name=name))

        for name in shapes:
            if not Shape.query.filter_by(name=name).first():
                db.session.add(Shape(name=name))

        db.session.commit()
        click.echo("✓ Attributes seeded successfully.")
