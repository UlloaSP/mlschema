@staticmethod
def normalize_dtype(dtype) -> str:
    """Normalize dtype to string representation."""
    return (
        str(dtype)
        if not hasattr(dtype, "name") or getattr(dtype, "names", None) is not None
        else dtype.name
    )
