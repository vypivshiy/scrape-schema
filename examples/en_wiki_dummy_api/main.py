from api import EnWikiApi, PageRefer


if __name__ == '__main__':
    page = EnWikiApi().search('Python')
    print(EnWikiApi().search('Python').view())
    if isinstance(page, PageRefer):
        for ref in page.referrers:
            if ref.url.endswith("(programming_language)"):
                print(ref.get_page().view())
                break
