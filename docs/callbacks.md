# Callbacks

This directory contains ready-made callbacks for some fields that will be used most often

## soup

* replace_text - get text from tag and replace chars
```python
from typing import Annotated
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupFind
from scrape_schema.callbacks.soup import replace_text

class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    egg: Annotated[str, SoupFind("<p>", callback=replace_text("spam", "egg"))]

schema = Schema("<p>spam</p>")
print(schema.dict()) # {"egg": "egg"}
```

* element_to_dict - convert html tag to attrs. Automatically convert 

In `SoupFind, SoupFindList` fields
```python
from scrape_schema.callbacks.soup import element_to_dict

element_to_dict('<p>')
# {"name":"p"}
element_to_dict('div class="spam" id="1" attr_1="egg"') 
# {"name": "div", "attrs":{"class": "spam", "id": "1", "attr_1": "egg"}
```

* get_text - get text from attribute. is default callback in soup fields
```python
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.soup import SoupFind

class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    spam: ScField[str, SoupFind("<p>")]

schema = Schema("<p>spam</p>")
print(schema.dict()) # {"spam": "spam"}
```
* get_attr - get attribute value from tag element
```python
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.soup import SoupFind

from scrape_schema.callbacks.soup import get_attr

class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    url: ScField[str, SoupFind("<a>", callback=get_attr("href"))]

schema = Schema('<a href="example.com">click me!</a>')
print(schema.dict()) # {"url": "example.com"}
```

* crop_by_tag_all - crop html document to parts for NestedList field
```python
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields import NestedList
from scrape_schema.fields.soup import SoupFind

from scrape_schema.callbacks.soup import get_attr, crop_by_tag_all


class SubSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    a: ScField[str, SoupFind("<a>", callback=get_attr("href"))]
    p: ScField[str, SoupFind("p")]
    
    
class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    sub_schemas: ScField[list[SubSchema], NestedList(SubSchema, crop_rule=crop_by_tag_all("div"))]

    
HTML = """
<html lang="en">
<body>
<div>
    <a href="example.com">
    <p>sample text</p>
</div>
<div>
    <a href="github.com">
    <p>github</p>
</div>
</body>
</html>
"""
schema = Schema(HTML)
print(schema.dict())
# {"sub_schemas": [
# {"a": "example.com", "p": "sample text"}, 
# {"a": "github.com", "p": "github"}]
# }
```

* crop_by_tag - crop html document to one element for Nested Field

```python
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields import Nested
from scrape_schema.fields.soup import SoupFind

from scrape_schema.callbacks.soup import get_attr, crop_by_tag


class SubSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    a: ScField[str, SoupFind("<a>", callback=get_attr("href"))]
    p: ScField[str, SoupFind("p")]
    
    
class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    sub_schema: ScField[SubSchema, Nested(SubSchema, crop_rule=crop_by_tag("div"))]

    
HTML = """
<html lang="en">
<body>
<div>
    <a href="example.com">
    <p>sample text</p>
</div>
<div>
    <a href="github.com">
    <p>github</p>
</div>
</body>
</html>
"""
schema = Schema(HTML)
print(schema.dict())
# {"sub_schema": {"a": "example.com", "p": "sample text"}}
```

* crop_by_selector - crop html document by css selector for Nested field
```python
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields import Nested
from scrape_schema.fields.soup import SoupFind, SoupSelect

from scrape_schema.callbacks.soup import get_attr, crop_by_selector


class SubSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    a: ScField[str, SoupFind("<a>", callback=get_attr("href"))]
    p: ScField[str, SoupSelect("p")]
    
    
class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    sub_schema: ScField[list[SubSchema], Nested(SubSchema, crop_rule=crop_by_selector("body > div"))]

    
HTML = """
<html lang="en">
<body>
<div>
    <a href="example.com">
    <p>sample text</p>
</div>
<div>
    <a href="github.com">
    <p>github</p>
</div>
</body>
</html>
"""
schema = Schema(HTML)
print(schema.dict())
# {"sub_schema": {"a": "example.com", "p": "sample text"}}
```
* crop_by_selector_all - crop html document to parts by css selector for NestedList field
```python
from typing import Annotated
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields import NestedList
from scrape_schema.fields.soup import SoupFind, SoupSelect

from scrape_schema.callbacks.soup import get_attr, crop_by_selector_all


class SubSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    a: ScField[str, SoupFind("<a>", callback=get_attr("href"))]
    p: ScField[str, SoupSelect("p")]
    
    
class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}
    sub_schema: ScField[list[SubSchema], NestedList(SubSchema, crop_rule=crop_by_selector_all("body > div"))]

HTML = """
<html lang="en">
<body>
<div>
    <a href="example.com">
    <p>sample text</p>
</div>
<div>
    <a href="github.com">
    <p>github</p>
</div>
</body>
</html>
"""
schema = Schema(HTML)
print(schema.dict())
# {"sub_schemas": [{"a": "example.com", "p": "sample text"},
# {"a": "github.com", "p": "github"}]
# }
```

## slax
* replace_text - get text from node and replace
```python
from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.slax import SlaxSelect
from scrape_schema.callbacks.soup import replace_text

class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    egg: ScField[str, SlaxSelect("p", callback=replace_text("spam", "egg"))]

schema = Schema("<p>spam</p>")
print(schema.dict()) # {"egg": "egg"}
```
* get_text - get text from node (default callback)
```python
from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.slax import SlaxSelect

class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    spam: ScField[str, SlaxSelect("p")]

schema = Schema("<p>spam</p>")
print(schema.dict()) # {"spam": "spam"}
```
* get_attr - get attribute from node
```python
from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.slax import SlaxSelect

from scrape_schema.callbacks.slax import get_attr

class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    url: ScField[str, SlaxSelect("a", callback=get_attr("href"))]

schema = Schema('<a href="example.com">click me!</a>')
print(schema.dict()) # {"url": "example.com"}
```
* crop_by_slax - crop html document for Nested field
```python
from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields import Nested
from scrape_schema.fields.slax import SlaxSelect

from scrape_schema.callbacks.slax import get_attr, crop_by_slax


class SubSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    a: ScField[str, SlaxSelect("a", callback=get_attr("href"))]
    p: ScField[str, SlaxSelect("p")]
    
    
class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    sub_schema: ScField[list[SubSchema], Nested(SubSchema, crop_rule=crop_by_slax("body > div"))]

    
HTML = """
<html lang="en">
<body>
<div>
    <a href="example.com">
    <p>sample text</p>
</div>
<div>
    <a href="github.com">
    <p>github</p>
</div>
</body>
</html>
"""
schema = Schema(HTML)
print(schema.dict())
# {"sub_schema": {"a": "example.com", "p": "sample text"}}
```

* crop_by_slax_all - crop html document for NestedList field
```python
from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields import NestedList
from scrape_schema.fields.slax import SlaxSelect

from scrape_schema.callbacks.slax import get_attr, crop_by_slax_all


class SubSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    a: ScField[str, SlaxSelect("a", callback=get_attr("href"))]
    p: ScField[str, SlaxSelect("p")]
    
    
class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    sub_schema: ScField[list[SubSchema], 
                        NestedList(SubSchema, crop_rule=crop_by_slax_all("body > div"))]

HTML = """
<html lang="en">
<body>
<div>
    <a href="example.com">
    <p>sample text</p>
</div>
<div>
    <a href="github.com">
    <p>github</p>
</div>
</body>
</html>
"""
schema = Schema(HTML)
print(schema.dict())
# {"sub_schemas": [
# {"a": "example.com", "p": "sample text"}
# {"a": "github.com", "p": "github"}]}
```
