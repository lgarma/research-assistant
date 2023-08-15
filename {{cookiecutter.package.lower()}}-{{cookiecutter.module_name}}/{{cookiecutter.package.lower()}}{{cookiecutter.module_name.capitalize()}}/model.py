"""{{cookiecutter.module_name.capitalize()}} Model."""
# Standar modules

# Third party modules
from pydantic.dataclasses import dataclass

# Local modules


@dataclass
class Model:
    """{{cookiecutter.module_name.capitalize()}} Model."""

    def __post_init_post_parse__(self):
        """Post init section."""
        pass

    def __str__(self):
        """Model docstring."""
        pass

    pass
