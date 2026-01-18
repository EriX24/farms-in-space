def log_error(msg, self=None):
    if self:
        print(f"[ERROR] {msg} ({self.__class__.__name__})")
    else:
        print(f"[ERROR] {msg}")
