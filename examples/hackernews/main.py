import pprint

import requests
from schema import HackerNewsSchema

if __name__ == "__main__":
    resp = requests.get("https://news.ycombinator.com").text
    schema = HackerNewsSchema(resp)
    # # or you can get posts list:
    # from schema import Post
    # from callbacks import crop_posts
    # posts = Post.init_list(crop_posts(resp))
    # ...
    pprint.pprint(schema.dict(), width=60, compact=True)
    # most_comment_posts = list(filter(lambda p: p.comments > 50, schema.posts))
    # shorten_nicknames = list(filter(lambda p: len(p.author) <= 8, schema.posts))
    # print(*most_comment_posts, sep="\n")
    # print()
    # print(*[p.author for p in shorten_nicknames], sep="\n")
