from ._version import __version__  # noqa: F401
from .extension import load_jupyter_server_extension  # noqa: F401


def _jupyter_server_extension_paths():
    return [{"module": "tiledb_prompt_options"}]
