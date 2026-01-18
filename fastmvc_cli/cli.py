"""
FastMVC CLI - Command Line Interface.

This module provides the main CLI entry point for FastMVC framework.
It uses Click for building the command-line interface.

Commands:
    generate: Create a new FastMVC project from template
    add: Add entities, migrations, etc. to existing project
    migrate: Database migration commands
    version: Display the current FastMVC version
    info: Display information about FastMVC

Example:
    $ fastmvc generate my_api
    $ fastmvc add entity Product
    $ fastmvc migrate upgrade
    $ fastmvc version
    $ fastmvc info
"""

import os
import subprocess
import click
import sys
from pathlib import Path

from fastmvc_cli import __version__
from fastmvc_cli.generator import ProjectGenerator
from fastmvc_cli.entity_generator import EntityGenerator


@click.group()
@click.version_option(version=__version__, prog_name="fastmvc")
def cli():
    """
    FastMVC - Production-grade MVC Framework for FastAPI.
    
    Generate new FastAPI projects with a clean MVC architecture,
    built-in authentication, rate limiting, security headers,
    and comprehensive documentation.
    
    \b
    Quick Start:
        $ fastmvc generate my_project
        $ cd my_project
        $ pip install -r requirements.txt
        $ python -m uvicorn app:app --reload
    
    \b
    Add Entities:
        $ cd my_project
        $ fastmvc add entity Product
        $ fastmvc add entity Order
    
    \b
    Database Migrations:
        $ fastmvc migrate generate "add products table"
        $ fastmvc migrate upgrade
        $ fastmvc migrate downgrade
    """
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--output-dir", "-o",
    default=".",
    help="Directory where the project will be created (default: current directory)"
)
@click.option(
    "--git/--no-git",
    default=True,
    help="Initialize a git repository (default: True)"
)
@click.option(
    "--venv/--no-venv",
    default=False,
    help="Create a virtual environment (default: False)"
)
@click.option(
    "--install/--no-install",
    default=False,
    help="Install dependencies after generation (default: False)"
)
def generate(project_name: str, output_dir: str, git: bool, venv: bool, install: bool):
    """
    Generate a new FastMVC project.
    
    Creates a new FastAPI project with the FastMVC architecture pattern,
    including all necessary directories, configuration files, and boilerplate code.
    
    \b
    Arguments:
        PROJECT_NAME: Name of the new project (will be used as directory name)
    
    \b
    Examples:
        $ fastmvc generate my_api
        $ fastmvc generate my_api --output-dir ~/projects
        $ fastmvc generate my_api --git --venv --install
    """
    click.echo()
    click.secho("╔══════════════════════════════════════════════════════════════╗", fg="cyan")
    click.secho("║                                                              ║", fg="cyan")
    click.secho("║   ███████╗ █████╗ ███████╗████████╗███╗   ███╗██╗   ██╗ ██████╗║", fg="cyan")
    click.secho("║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝████╗ ████║██║   ██║██╔════╝║", fg="cyan")
    click.secho("║   █████╗  ███████║███████╗   ██║   ██╔████╔██║██║   ██║██║     ║", fg="cyan")
    click.secho("║   ██╔══╝  ██╔══██║╚════██║   ██║   ██║╚██╔╝██║╚██╗ ██╔╝██║     ║", fg="cyan")
    click.secho("║   ██║     ██║  ██║███████║   ██║   ██║ ╚═╝ ██║ ╚████╔╝ ╚██████╗║", fg="cyan")
    click.secho("║   ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝  ╚═══╝   ╚═════╝║", fg="cyan")
    click.secho("║                                                              ║", fg="cyan")
    click.secho("║          Production-grade MVC Framework for FastAPI          ║", fg="cyan")
    click.secho("╚══════════════════════════════════════════════════════════════╝", fg="cyan")
    click.echo()
    
    # Validate project name
    if not project_name.replace("_", "").replace("-", "").isalnum():
        click.secho(
            f"✗ Invalid project name: '{project_name}'. "
            "Use only letters, numbers, underscores, and hyphens.",
            fg="red"
        )
        sys.exit(1)
    
    # Create generator and run
    generator = ProjectGenerator(
        project_name=project_name,
        output_dir=output_dir,
        init_git=git,
        create_venv=venv,
        install_deps=install
    )
    
    try:
        generator.generate()
        click.echo()
        click.secho("✓ Project generated successfully!", fg="green", bold=True)
        click.echo()
        click.secho("Next steps:", fg="yellow", bold=True)
        click.echo()
        click.echo(f"  1. cd {project_name}")
        click.echo("  2. pip install -r requirements.txt")
        click.echo("  3. cp .env.example .env  # Configure your environment")
        click.echo("  4. docker-compose up -d  # Start PostgreSQL and Redis")
        click.echo("  5. fastmvc migrate upgrade  # Run database migrations")
        click.echo("  6. python -m uvicorn app:app --reload")
        click.echo()
        click.secho(f"  → Your API will be available at http://localhost:8000", fg="cyan")
        click.secho(f"  → API docs at http://localhost:8000/docs", fg="cyan")
        click.echo()
    except Exception as e:
        click.secho(f"✗ Error generating project: {e}", fg="red")
        sys.exit(1)


# ============================================================================
# ADD COMMAND GROUP
# ============================================================================

@cli.group()
def add():
    """
    Add components to an existing FastMVC project.
    
    \b
    Available subcommands:
        entity - Generate a new entity with full CRUD
    
    \b
    Examples:
        $ fastmvc add entity Product
        $ fastmvc add entity Order --no-tests
    """
    pass


@add.command("entity")
@click.argument("entity_name")
@click.option(
    "--tests/--no-tests",
    default=True,
    help="Generate test files (default: True)"
)
def add_entity(entity_name: str, tests: bool):
    """
    Generate a new entity with full CRUD scaffolding.
    
    Creates model, repository, service, controller, DTOs, dependencies,
    and tests for the specified entity.
    
    \b
    Arguments:
        ENTITY_NAME: Name of the entity in PascalCase (e.g., Product, Order)
    
    \b
    Examples:
        $ fastmvc add entity Product
        $ fastmvc add entity OrderItem --no-tests
    
    \b
    Generated files:
        • models/<entity>.py
        • repositories/<entity>.py
        • services/<entity>/
        • controllers/<entity>/
        • dtos/requests/<entity>/
        • dependencies/repositiories/<entity>.py
        • tests/unit/models/test_<entity>.py
    """
    click.echo()
    click.secho(f"→ Generating entity: {entity_name}", fg="blue", bold=True)
    click.echo()
    
    # Validate entity name
    if not entity_name[0].isupper():
        click.secho(
            f"✗ Entity name should be in PascalCase (e.g., Product, not {entity_name})",
            fg="yellow"
        )
        entity_name = entity_name[0].upper() + entity_name[1:]
        click.secho(f"  Using: {entity_name}", fg="white")
    
    # Check we're in a FastMVC project
    project_path = Path.cwd()
    if not (project_path / "app.py").exists():
        click.secho(
            "✗ Not in a FastMVC project directory. "
            "Run this command from your project root.",
            fg="red"
        )
        sys.exit(1)
    
    try:
        generator = EntityGenerator(
            entity_name=entity_name,
            project_path=project_path,
            with_tests=tests,
        )
        generator.generate()
        
        click.echo()
        click.secho("✓ Entity generated successfully!", fg="green", bold=True)
        click.echo()
        click.secho("Next steps:", fg="yellow", bold=True)
        click.echo()
        click.echo(f"  1. Review generated files in models/, services/, controllers/")
        click.echo(f"  2. Register the router in app.py:")
        click.echo()
        click.secho(f"     from controllers.{entity_name.lower()} import router as {entity_name.lower()}_router", fg="white", dim=True)
        click.secho(f"     app.include_router({entity_name.lower()}_router)", fg="white", dim=True)
        click.echo()
        click.echo(f"  3. Generate migration: fastmvc migrate generate 'add_{entity_name.lower()}_table'")
        click.echo(f"  4. Apply migration: fastmvc migrate upgrade")
        click.echo()
    except Exception as e:
        click.secho(f"✗ Error generating entity: {e}", fg="red")
        sys.exit(1)


# ============================================================================
# MIGRATE COMMAND GROUP
# ============================================================================

@cli.group()
def migrate():
    """
    Database migration commands using Alembic.
    
    \b
    Available subcommands:
        generate - Create a new migration
        upgrade  - Apply migrations
        downgrade - Rollback migrations
        status   - Show current migration status
        history  - Show migration history
    
    \b
    Examples:
        $ fastmvc migrate generate "add users table"
        $ fastmvc migrate upgrade
        $ fastmvc migrate downgrade -1
    """
    pass


@migrate.command("generate")
@click.argument("message")
@click.option(
    "--autogenerate/--no-autogenerate",
    default=True,
    help="Auto-generate migration from model changes (default: True)"
)
def migrate_generate(message: str, autogenerate: bool):
    """
    Generate a new database migration.
    
    Creates a new migration file based on changes to your SQLAlchemy models.
    
    \b
    Arguments:
        MESSAGE: Description of the migration (e.g., "add products table")
    
    \b
    Examples:
        $ fastmvc migrate generate "add products table"
        $ fastmvc migrate generate "add email index" --no-autogenerate
    """
    click.secho(f"→ Generating migration: {message}", fg="blue")
    
    # Check for alembic.ini
    if not Path("alembic.ini").exists():
        click.secho("✗ alembic.ini not found. Are you in a FastMVC project?", fg="red")
        sys.exit(1)
    
    try:
        cmd = ["alembic", "revision"]
        if autogenerate:
            cmd.append("--autogenerate")
        cmd.extend(["-m", message])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            click.secho("✓ Migration generated successfully!", fg="green")
            click.echo(result.stdout)
        else:
            click.secho(f"✗ Migration generation failed:", fg="red")
            click.echo(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("upgrade")
@click.argument("revision", default="head")
def migrate_upgrade(revision: str):
    """
    Apply database migrations.
    
    \b
    Arguments:
        REVISION: Target revision (default: "head" for latest)
    
    \b
    Examples:
        $ fastmvc migrate upgrade        # Apply all pending migrations
        $ fastmvc migrate upgrade head   # Same as above
        $ fastmvc migrate upgrade +1     # Apply next migration
    """
    click.secho(f"→ Upgrading database to: {revision}", fg="blue")
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", revision],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.secho("✓ Database upgraded successfully!", fg="green")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.secho(f"✗ Upgrade failed:", fg="red")
            click.echo(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("downgrade")
@click.argument("revision", default="-1")
def migrate_downgrade(revision: str):
    """
    Rollback database migrations.
    
    \b
    Arguments:
        REVISION: Target revision (default: "-1" for previous)
    
    \b
    Examples:
        $ fastmvc migrate downgrade      # Rollback one migration
        $ fastmvc migrate downgrade -1   # Same as above
        $ fastmvc migrate downgrade base # Rollback all migrations
    """
    click.secho(f"→ Downgrading database to: {revision}", fg="yellow")
    
    try:
        result = subprocess.run(
            ["alembic", "downgrade", revision],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.secho("✓ Database downgraded successfully!", fg="green")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.secho(f"✗ Downgrade failed:", fg="red")
            click.echo(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("status")
def migrate_status():
    """
    Show current database migration status.
    
    Displays the current revision applied to the database.
    """
    click.secho("→ Checking migration status...", fg="blue")
    
    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.secho("Current revision:", fg="cyan", bold=True)
            click.echo(result.stdout or "  No migrations applied yet")
        else:
            click.echo(result.stderr)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


@migrate.command("history")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def migrate_history(verbose: bool):
    """
    Show migration history.
    
    Displays all available migrations and their status.
    """
    click.secho("→ Migration history:", fg="blue")
    
    try:
        cmd = ["alembic", "history"]
        if verbose:
            cmd.append("--verbose")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo(result.stdout or "  No migrations found")
        else:
            click.echo(result.stderr)
    except FileNotFoundError:
        click.secho("✗ Alembic not found. Install with: pip install alembic", fg="red")
        sys.exit(1)


# ============================================================================
# INFO & VERSION COMMANDS
# ============================================================================

@cli.command()
def info():
    """
    Display information about FastMVC.
    
    Shows details about the framework including version,
    features, and documentation links.
    """
    click.echo()
    click.secho("FastMVC Framework", fg="cyan", bold=True)
    click.secho("=" * 50, fg="cyan")
    click.echo()
    click.echo(f"  Version:     {__version__}")
    click.echo(f"  Python:      {sys.version.split()[0]}")
    click.echo()
    click.secho("Core Features:", fg="yellow", bold=True)
    click.echo("  • MVC Architecture Pattern")
    click.echo("  • Built-in Authentication (JWT)")
    click.echo("  • Rate Limiting Middleware")
    click.echo("  • Security Headers Middleware")
    click.echo("  • Request Context Tracking")
    click.echo("  • Input Validation & Sanitization")
    click.echo("  • Comprehensive Test Suite")
    click.echo("  • Production-grade Documentation")
    click.echo()
    click.secho("New Features:", fg="green", bold=True)
    click.echo("  • Entity Generator (fastmvc add entity)")
    click.echo("  • Database Migrations (fastmvc migrate)")
    click.echo("  • Redis Caching Utilities")
    click.echo("  • Alembic Integration")
    click.echo()
    click.secho("Project Structure:", fg="yellow", bold=True)
    click.echo("  • abstractions/   - Base interfaces & contracts")
    click.echo("  • configurations/ - Config loaders")
    click.echo("  • constants/      - Application constants")
    click.echo("  • controllers/    - Request handlers")
    click.echo("  • dependencies/   - Dependency injection")
    click.echo("  • dtos/           - Data transfer objects")
    click.echo("  • errors/         - Custom exceptions")
    click.echo("  • middlewares/    - Request/Response middleware")
    click.echo("  • migrations/     - Database migrations (Alembic)")
    click.echo("  • models/         - Database models")
    click.echo("  • repositories/   - Data access layer")
    click.echo("  • services/       - Business logic")
    click.echo("  • utilities/      - Helper functions & cache")
    click.echo()
    click.secho("Commands:", fg="yellow", bold=True)
    click.echo("  fastmvc generate <name>     Create new project")
    click.echo("  fastmvc add entity <name>   Add CRUD entity")
    click.echo("  fastmvc migrate upgrade     Apply migrations")
    click.echo("  fastmvc migrate generate    Create migration")
    click.echo("  fastmvc info                Show this info")
    click.echo()


@cli.command()
def version():
    """Display the FastMVC version."""
    click.echo(f"FastMVC v{__version__}")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
