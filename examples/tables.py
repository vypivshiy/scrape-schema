import pprint

from scrape_schema import BaseSchema
from scrape_schema.field import RawTableField, TableDictView


class SchemaTable(BaseSchema):
    item: TableDictView = RawTableField().table()


if __name__ == "__main__":
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
    HTML2 = """
    <table>
  <tr>
    <td>&nbsp;</td>
    <td>Knocky</td>
    <td>Flor</td>
    <td>Ella</td>
    <td>Juan</td>
  </tr>
  <tr>
    <td>Breed</td>
    <td>Jack Russell</td>
    <td>Poodle</td>
    <td>Streetdog</td>
    <td>Cocker Spaniel</td>
  </tr>
  <tr>
    <td>Age</td>
    <td>16</td>
    <td>9</td>
    <td>10</td>
    <td>5</td>
  </tr>
  <tr>
    <td>Owner</td>
    <td>Mother-in-law</td>
    <td>Me</td>
    <td>Me</td>
    <td>Sister-in-law</td>
  </tr>
  <tr>
    <td>Eating Habits</td>
    <td>Eats everyone's leftovers</td>
    <td>Nibbles at food</td>
    <td>Hearty eater</td>
    <td>Will eat till he explodes</td>
  </tr>
</table>
    """
    HTML3 = """
    <table>
  <tr>
    <th>Animals</th>
  </tr>
  <tr>
    <th>Hippopotamus</th>
  </tr>
  <tr>
    <th>Horse</th>
    <td>Mare</td>
  </tr>
  <tr>
    <td>Stallion</td>
  </tr>
  <tr>
    <th>Crocodile</th>
  </tr>
  <tr>
    <th>Chicken</th>
    <td>Hen</td>
  </tr>
  <tr>
    <td>Rooster</td>
  </tr>
</table>

    """
    HTML4 = """
    <table cellspacing="0" cellpadding="2" border="1" style="border-collapse: collapse;">

<tbody><tr>
<th style="background:#f0f0f0;">Genus<sup id="cite_ref-ITIS_2-1" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Taxon author<sup id="cite_ref-ITIS_2-2" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Species<sup id="cite_ref-ITIS_2-3" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Subsp.<sup id="cite_ref-13" class="reference"><a href="#cite_note-13">[a]</a></sup><sup id="cite_ref-ITIS_2-4" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Common name
</th>
<th style="background:#f0f0f0;">Geographic range<sup id="cite_ref-McD99_1-3" class="reference"><a href="#cite_note-McD99-1">[1]</a></sup>
</th></tr>
<tr>
<td><i><a href="/wiki/Antaresia" title="Antaresia">Antaresia</a></i>
</td>
<td>Wells &amp; Wellington, 1984
</td>
<td style="text-align:center;">4
</td>
<td style="text-align:center;">2
</td>
<td>Children's pythons
</td>
<td style="width:40%">Australia in arid and tropical regions
</td></tr>
<tr>
<td><i><a href="/wiki/Apodora" title="Apodora">Apodora</a></i><sup id="cite_ref-14" class="reference"><a href="#cite_note-14">[13]</a></sup>
</td>
<td>Kluge, 1993
</td>
<td style="text-align:center;">1
</td>
<td style="text-align:center;">0
</td>
<td>Papuan python
</td>
<td>Papua New Guinea
</td></tr>
<tr>
<td><i><a href="/wiki/Aspidites" title="Aspidites">Aspidites</a></i>
</td>
<td><a href="/wiki/Wilhelm_Peters" title="Wilhelm Peters">Peters</a>, 1877
</td>
<td style="text-align:center;">2
</td>
<td style="text-align:center;">0
</td>
<td>pitless pythons
</td>
<td>Australia, except in the southern parts of the country
</td></tr>
<tr>
<td><i>Bothrochilus</i>
</td>
<td><a href="/wiki/Leopold_Fitzinger" title="Leopold Fitzinger">Fitzinger</a>, 1843
</td>
<td style="text-align:center;">1
</td>
<td style="text-align:center;">0
</td>
<td><a href="/wiki/Bismarck_ringed_python" title="Bismarck ringed python">Bismarck ringed python</a>
</td>
<td>the Bismarck Archipelago
</td></tr>
<tr>
<td><i><a href="/wiki/Leiopython" title="Leiopython">Leiopython</a></i>
</td>
<td><a href="/wiki/Ambrosius_Hubrecht" title="Ambrosius Hubrecht">Hubrecht</a>, 1879
</td>
<td style="text-align:center;">3
</td>
<td style="text-align:center;">0
</td>
<td>white-lipped pythons
</td>
<td>Papua New Guinea
</td></tr>
<tr>
<td><i><a href="/wiki/Liasis" title="Liasis">Liasis</a></i>
</td>
<td><a href="/wiki/John_Edward_Gray" title="John Edward Gray">Gray</a>, 1842
</td>
<td style="text-align:center;">3
</td>
<td style="text-align:center;">5
</td>
<td>water pythons
</td>
<td><a href="/wiki/Indonesia" title="Indonesia">Indonesia</a> in the <a href="/wiki/Lesser_Sunda_Islands" title="Lesser Sunda Islands">Lesser Sunda Islands</a>, east through New Guinea and northern and western Australia
</td></tr>
<tr>
<td><i><a href="/wiki/Malayopython" title="Malayopython">Malayopython</a></i>
</td>
<td>Reynolds, 2014
</td>
<td style="text-align:center;">2
</td>
<td style="text-align:center;">3
</td>
<td>reticulated and Timor pythons
</td>
<td>from India to Timor
</td></tr>
<tr>
<td><i><a href="/wiki/Morelia_(snake)" title="Morelia (snake)">Morelia</a></i>
</td>
<td>Gray, 1842
</td>
<td style="text-align:center;">6
</td>
<td style="text-align:center;">7
</td>
<td>tree pythons
</td>
<td>from Indonesia in the <a href="/wiki/Maluku_Islands" title="Maluku Islands">Maluku Islands</a>, east through New Guinea, including the Bismarck Archipelago, and Australia
</td></tr>
<tr>
<td><i>Nyctophilopython</i>
</td>
<td>Gow, 1977
</td>
<td style="text-align:center;">1
</td>
<td style="text-align:center;">0
</td>
<td><a href="/wiki/Oenpelli_python" title="Oenpelli python">Oenpelli python</a>
</td>
<td style="width:40%">the Northern Territory, Australia
</td></tr>
<tr>
<td><i><a href="/wiki/Python_(genus)" title="Python (genus)">Python</a></i><sup id="cite_ref-15" class="reference"><a href="#cite_note-15">[b]</a></sup>
</td>
<td><a href="/wiki/Fran%C3%A7ois_Marie_Daudin" title="François Marie Daudin">Daudin</a>, 1803
</td>
<td style="text-align:center;">10
</td>
<td style="text-align:center;">1
</td>
<td>true pythons
</td>
<td>Africa in the tropics south of the <a href="/wiki/Sahara" title="Sahara">Sahara Desert</a> (not including southern and extreme southwestern <a href="/wiki/Madagascar" title="Madagascar">Madagascar</a>), <a href="/wiki/Bangladesh" title="Bangladesh">Bangladesh</a>, Pakistan, India, <a href="/wiki/Sri_Lanka" title="Sri Lanka">Sri Lanka</a>, the <a href="/wiki/Nicobar_Islands" title="Nicobar Islands">Nicobar Islands</a>, <a href="/wiki/Burma" class="mw-redirect" title="Burma">Burma</a>, <a href="/wiki/Indochina" class="mw-redirect" title="Indochina">Indochina</a>, southern China, <a href="/wiki/Hong_Kong" title="Hong Kong">Hong Kong</a>, <a href="/wiki/Hainan" title="Hainan">Hainan</a>, the Malayan region of <a href="/wiki/Indonesia" title="Indonesia">Indonesia</a> and the <a href="/wiki/Philippines" title="Philippines">Philippines</a>
</td></tr>
<tr>
<td><i><a href="/wiki/Simalia" title="Simalia">Simalia</a></i>
</td>
<td>Gray, 1849
</td>
<td style="text-align:center;">6
</td>
<td style="text-align:center;">0
</td>
<td>amethystine python species complex
</td>
<td>found in Indonesia (Including the islands of <a href="/wiki/Halmahera" title="Halmahera">Halmahera</a>, <a href="/wiki/Ambon_Island" title="Ambon Island">Ambon</a>, <a href="/wiki/Seram_Island" title="Seram Island">Seram</a>, <a href="/wiki/Maluku_Islands" title="Maluku Islands">Maluku</a>), the <a href="/wiki/Northern_Territory" title="Northern Territory">Northern Territory</a>, northeastern <a href="/wiki/Queensland" title="Queensland">Queensland</a> into the <a href="/wiki/Torres_Strait" title="Torres Strait">Torres Strait</a>, and <a href="/wiki/Papua_New_Guinea" title="Papua New Guinea">Papua New Guinea</a>
</td></tr></tbody></table>
    """

    pprint.pprint(SchemaTable(HTML).dict(), compact=True)
    # correct output
    # {'item': {'cells': [['Emil', 'Tobias', 'Linus'], ['16', '14', '10']],
    #           'columns': ['Person 1', 'Person 2', 'Person 3'],
    #           'table': {'Person 1': ['Emil', '16'],
    #                     'Person 2': ['Tobias', '14'],
    #                     'Person 3': ['Linus', '10']}}}
    print("---")
    pprint.pprint(SchemaTable(HTML2).dict(), compact=True)
    # this document exclude <th> elements, failed represent "table" key value
    # {'item': {'cells': [['', 'Knocky', 'Flor', 'Ella', 'Juan'],
    #                     ['Breed', 'Jack Russell', 'Poodle', 'Streetdog',
    #                      'Cocker Spaniel'],
    #                     ['Age', '16', '9', '10', '5'],
    #                     ['Owner', 'Mother-in-law', 'Me', 'Me', 'Sister-in-law'],
    #                     ['Eating Habits', "Eats everyone's leftovers",
    #                      'Nibbles at food', 'Hearty eater',
    #                      'Will eat till he explodes']],
    #           'columns': [],
    #           'table': {}}}
    print("---")
    pprint.pprint(SchemaTable(HTML3).dict(), compact=True)
    # in table field missing values stub by `None` value
    # {'item': {'cells': [['Mare'], ['Stallion'], ['Hen'], ['Rooster']],
    #           'columns': ['Animals', 'Hippopotamus', 'Horse', 'Crocodile',
    #                       'Chicken'],
    #           'table': {'Animals': ['Mare', 'Stallion', 'Hen', 'Rooster'],
    #                     'Chicken': [None, None, None, None],
    #                     'Crocodile': [None, None, None, None],
    #                     'Hippopotamus': [None, None, None, None],
    #                     'Horse': [None, None, None, None]}}}
    print("---")
    pprint.pprint(SchemaTable(HTML4).dict(), compact=True)
    # example extract value from https://en.wikipedia.org/wiki/Pythonidae
    # {'item': {'cells': [['Antaresia ', 'Wells & Wellington, 1984', '4', '2',
    #                      "Children's pythons",
    #                      'Australia in arid and tropical regions'],
    #                     ['Apodora [13] ', 'Kluge, 1993', '1', '0', 'Papuan python',
    #                      'Papua New Guinea'],
    #                     ['Aspidites ', 'Peters , 1877', '2', '0', 'pitless pythons',
    #                      'Australia, except in the southern parts of the country'],
    #                     ['Bothrochilus ', 'Fitzinger , 1843', '1', '0',
    #                      'Bismarck ringed python ', 'the Bismarck Archipelago'],
    #                     ['Leiopython ', 'Hubrecht , 1879', '3', '0',
    #                      'white-lipped pythons', 'Papua New Guinea'],
    #                     ['Liasis ', 'Gray , 1842', '3', '5', 'water pythons',
    #                      'Indonesia in the Lesser Sunda Islands , east through New '
    #                      'Guinea and northern and western Australia'],
    #                     ['Malayopython ', 'Reynolds, 2014', '2', '3',
    #                      'reticulated and Timor pythons', 'from India to Timor'],
    #                     ['Morelia ', 'Gray, 1842', '6', '7', 'tree pythons',
    #                      'from Indonesia in the Maluku Islands , east through New '
    #                      'Guinea, including the Bismarck Archipelago, and '
    #                      'Australia'],
    #                     ['Nyctophilopython ', 'Gow, 1977', '1', '0',
    #                      'Oenpelli python ', 'the Northern Territory, Australia'],
    #                     ['Python [b] ', 'Daudin , 1803', '10', '1', 'true pythons',
    #                      'Africa in the tropics south of the Sahara Desert (not '
    #                      'including southern and extreme southwestern Madagascar '
    #                      '), Bangladesh , Pakistan, India, Sri Lanka , the Nicobar '
    #                      'Islands , Burma , Indochina , southern China, Hong Kong '
    #                      ', Hainan , the Malayan region of Indonesia and the '
    #                      'Philippines '],
    #                     ['Simalia ', 'Gray, 1849', '6', '0',
    #                      'amethystine python species complex',
    #                      'found in Indonesia (Including the islands of Halmahera , '
    #                      'Ambon , Seram , Maluku ), the Northern Territory , '
    #                      'northeastern Queensland into the Torres Strait , and '
    #                      'Papua New Guinea ']],
    #           'columns': ['Genus [2] ', 'Taxon author [2] ', 'Species [2] ',
    #                       'Subsp. [a] [2] ', 'Common name',
    #                       'Geographic range [1] '],
    #           'table': {'Common name': ["Children's pythons", 'Papuan python',
    #                                     'pitless pythons',
    #                                     'Bismarck ringed python ',
    #                                     'white-lipped pythons', 'water pythons',
    #                                     'reticulated and Timor pythons',
    #                                     'tree pythons', 'Oenpelli python ',
    #                                     'true pythons',
    #                                     'amethystine python species complex'],
    #                     'Genus [2] ': ['Antaresia ', 'Apodora [13] ', 'Aspidites ',
    #                                    'Bothrochilus ', 'Leiopython ', 'Liasis ',
    #                                    'Malayopython ', 'Morelia ',
    #                                    'Nyctophilopython ', 'Python [b] ',
    #                                    'Simalia '],
    #                     'Geographic range [1] ': ['Australia in arid and tropical '
    #                                               'regions',
    #                                               'Papua New Guinea',
    #                                               'Australia, except in the '
    #                                               'southern parts of the country',
    #                                               'the Bismarck Archipelago',
    #                                               'Papua New Guinea',
    #                                               'Indonesia in the Lesser Sunda '
    #                                               'Islands , east through New '
    #                                               'Guinea and northern and western '
    #                                               'Australia',
    #                                               'from India to Timor',
    #                                               'from Indonesia in the Maluku '
    #                                               'Islands , east through New '
    #                                               'Guinea, including the Bismarck '
    #                                               'Archipelago, and Australia',
    #                                               'the Northern Territory, '
    #                                               'Australia',
    #                                               'Africa in the tropics south of '
    #                                               'the Sahara Desert (not '
    #                                               'including southern and extreme '
    #                                               'southwestern Madagascar ), '
    #                                               'Bangladesh , Pakistan, India, '
    #                                               'Sri Lanka , the Nicobar Islands '
    #                                               ', Burma , Indochina , southern '
    #                                               'China, Hong Kong , Hainan , the '
    #                                               'Malayan region of Indonesia and '
    #                                               'the Philippines ',
    #                                               'found in Indonesia (Including '
    #                                               'the islands of Halmahera , '
    #                                               'Ambon , Seram , Maluku ), the '
    #                                               'Northern Territory , '
    #                                               'northeastern Queensland into '
    #                                               'the Torres Strait , and Papua '
    #                                               'New Guinea '],
    #                     'Species [2] ': ['4', '1', '2', '1', '3', '3', '2', '6',
    #                                      '1', '10', '6'],
    #                     'Subsp. [a] [2] ': ['2', '0', '0', '0', '0', '5', '3', '7',
    #                                         '0', '1', '0'],
    #                     'Taxon author [2] ': ['Wells & Wellington, 1984',
    #                                           'Kluge, 1993', 'Peters , 1877',
    #                                           'Fitzinger , 1843', 'Hubrecht , 1879',
    #                                           'Gray , 1842', 'Reynolds, 2014',
    #                                           'Gray, 1842', 'Gow, 1977',
    #                                           'Daudin , 1803', 'Gray, 1849']}}}
