import pytest

from scrape_schema.field import RawTableField

HTML = """
 <table>
  <tr>
    <th>Person 1</th>
    <th>Person 2</th>
    <th>Person 3</th>
  </tr>
  <tr>
    <td>Emil</td>
    <td>Tobias</td>
    <td>Linus</td>
  </tr>
  <tr>
    <td>16</td>
    <td>14</td>
    <td>10</td>
  </tr>
</table>
"""


def test_table_parse():
    assert RawTableField().table().sc_parse(HTML) == {
        "columns": ["Person 1", "Person 2", "Person 3"],
        "cells": [["Emil", "Tobias", "Linus"], ["16", "14", "10"]],
        "table": {
            "Person 1": ["Emil", "16"],
            "Person 2": ["Tobias", "14"],
            "Person 3": ["Linus", "10"],
        },
    }


def test_fail_table():
    with pytest.raises(TypeError):
        RawTableField().table().sc_parse("")
