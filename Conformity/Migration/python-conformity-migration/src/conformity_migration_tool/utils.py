def str2bool(txt: str) -> bool:
    return txt.strip().lower() in {"1", "true", "yes", "on"}
