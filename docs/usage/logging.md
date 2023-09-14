## logging
For config or disable logging get logger by `scrape_schema` name

```python
import logging
logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.ERROR)
...
```

For type_caster module get logger by `type_caster` name:

```python
import logging
logger = logging.getLogger("type_caster")
logger.setLevel(logging.ERROR)
...
```
