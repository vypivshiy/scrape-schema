from bs4 import BeautifulSoup


def crop_schedule(markup: str) -> list[str]:
    soup = BeautifulSoup(markup, "html.parser")
    tags = soup.find_all("div", class_="list-group")[1].find_all(
        "div", class_="media-body"
    )
    return [str(tag) for tag in tags]


def crop_ongoing(markup: str) -> list[str]:
    soup = BeautifulSoup(markup, "html.parser")
    tags = soup.find_all("div", class_="list-group")[0].find_all(
        "div", class_="last-update-item"
    )
    return [str(tag) for tag in tags]


def crop_new_anime(markup: str) -> list[str]:
    soup = BeautifulSoup(markup, "html.parser")
    tags = soup.select_one("#content > div:nth-child(2)").find_all(
        "div", class_="animes-list-item media"
    )
    return [str(tag) for tag in tags]
