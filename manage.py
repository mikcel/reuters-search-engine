#!~/projects/reuters_search_venv/ python3
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "search_engine.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)