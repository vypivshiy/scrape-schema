#!/usr/bin/bash
black .
isort .
ruff .
mypy . && hatch run pytest && hatch build && hatch publish
