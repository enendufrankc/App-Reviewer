try:
    from .settings import AppConfig, ELIGIBILITY_CRITERIA, SYSTEM_PROMPT
    __all__ = ["AppConfig", "ELIGIBILITY_CRITERIA", "SYSTEM_PROMPT"]
except ImportError as e:
    print(f"Warning: Could not import config settings: {e}")
    __all__ = []