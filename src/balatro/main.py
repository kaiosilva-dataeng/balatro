"""
Entry point for the Balatro automation application.

This module delegates to the CLI entrypoint.
"""

from .entrypoints.cli import main

if __name__ == '__main__':
    main()
