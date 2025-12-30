"""
Domain-specific exceptions for the Balatro automation.
"""


class BalatroError(Exception):
    """Base exception for all Balatro automation errors."""

    pass


class ConfigurationError(BalatroError):
    """Raised when there's an issue with configuration."""

    pass


class AssetNotFoundError(BalatroError):
    """Raised when a required image asset cannot be loaded."""

    def __init__(self, asset_name: str, path: str = ""):
        self.asset_name = asset_name
        self.path = path
        message = f"Asset '{asset_name}' not found"
        if path:
            message += f" at path: {path}"
        super().__init__(message)


class ProfileNotFoundError(ConfigurationError):
    """Raised when a resolution profile cannot be found."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Profile '{profile_name}' not found in configuration")


class ActionNotFoundError(ConfigurationError):
    """Raised when a named action is not defined in the profile."""

    def __init__(self, action_name: str, profile_name: str):
        self.action_name = action_name
        self.profile_name = profile_name
        super().__init__(
            f"Action '{action_name}' not found in profile '{profile_name}'"
        )
