import importlib
from django.conf import settings

DEFAULT_SVG_MODEL = "snowebsvg.models.DefaultSvg"
SVG_MODEL = getattr(
    settings,
    "SVG_MODEL",
    DEFAULT_SVG_MODEL
)


def import_from_string(val):
    """
    Attempt to import a class from a string representation.
    From: django-rest-framework
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for setting. %s: %s." % (
            val, e.__class__.__name__, e
        )
        raise ImportError(msg)
