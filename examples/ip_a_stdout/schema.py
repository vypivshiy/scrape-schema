from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList
from typing import Annotated


class Device(BaseSchema):
    num: Annotated[int, ReMatch(r"^(\d+):")]
    name: Annotated[str, ReMatch(r"^\d+: (\w+):")]
    interface: Annotated[list[str], ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(","))]
    mtu: Annotated[int, ReMatch(r"mtu (\d+)")]
    qdisc: Annotated[str, ReMatch(r"qdisc (\w+)")]
    state: Annotated[str, ReMatch(r"state ([A-Z]+)")]
    group: Annotated[str, ReMatch(r"group (\w+)", default="unknown")]
    qlen: Annotated[int, ReMatch(r"qlen (\d+)")]
    link: Annotated[str, ReMatch(r"link/(\w+)")]
    addr: Annotated[str, ReMatch(r"link/\w+ ([\d:a-z]+)")]
    ipv4: Annotated[list[str], ReMatchList(r"inet ([\d./]+)")]
    ipv6: Annotated[list[str], ReMatchList(r"inet6 ([a-z\d./:]+)")]
