def format_bytes(size: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024

    return f"{size:.1f} TiB"


def truncate(content: str, max_length: int) -> str:
    if len(content) <= max_length:
        return content

    return content[: max_length - 3] + "..."
