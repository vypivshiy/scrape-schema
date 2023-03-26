from bs4 import BeautifulSoup


def crop_posts(markup: str) -> list[str]:
    """a crop rule for hackenews schema"""
    soup = BeautifulSoup(markup, 'html.parser')
    # get main news table
    table = soup.find('tr', class_='athing').parent
    elements: list[str] = []
    first_tag: str = ''
    # get two 'tr' tags and concatenate, skip <tr class='spacer'>

    for tr in table.find_all('tr'):
        # <tr class="athing">
        if tr.attrs.get('class') and 'athing' in tr.attrs.get('class'):
            first_tag = str(tr)
        # <tr>
        elif not tr.attrs:
            elements.append(first_tag + '\n' + str(tr))
            first_tag = ''
        # <tr class="morespace"> END page, stop iteration
        elif tr.attrs.get('class') and 'morespace' in tr.attrs.get('class'):
            break
    return elements


def concat_href(path: str) -> str:
    """custom factory for concatenate path url with netloc"""
    return f"https://news.ycombinator.com{path}"
