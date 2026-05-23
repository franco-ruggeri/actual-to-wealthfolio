from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("actual_to_wealthfolio")
except PackageNotFoundError:
    __version__ = "unknown"
