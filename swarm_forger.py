"""Minimal Python module for the Swarm Forger project."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectInfo:
    name: str
    purpose: str
    language: str


def get_project_info() -> ProjectInfo:
    """Return the core metadata for this Swarm Forger project."""
    return ProjectInfo(
        name="generic-scraper2",
        purpose="Swarm Forger project",
        language="Python",
    )


def describe_project() -> str:
    """Return a human-readable description of the project."""
    project = get_project_info()
    return f"{project.name} is a {project.purpose} that has {project.language} code."
