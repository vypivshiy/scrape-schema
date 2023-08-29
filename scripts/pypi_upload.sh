#!/usr/bin/bash
black .
isort .
mypy . && hatch run pytest && hatch build && hatch publish
