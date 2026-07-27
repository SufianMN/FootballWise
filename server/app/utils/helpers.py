import numpy as np


def convert_numpy_types(obj):
    """
    Recursively converts NumPy scalar types into native Python types.
    This resolves serialization errors (like TypeError: 'numpy.int64' object is not iterable)
    when returning data structures from FastAPI.

    Args:
        obj: Any Python object, list, dictionary, or NumPy scalar/array.

    Returns:
        The exact same structure, with all NumPy scalars replaced by Python native types.
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    else:
        return obj
