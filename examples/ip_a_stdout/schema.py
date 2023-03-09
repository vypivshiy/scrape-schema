from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList


class Device(BaseSchema):
    num: int = ReMatch(r"^(\d+):")
    name: str = ReMatch(r"^\d+: (\w+):")
    interface: list[str] = ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(","))
    mtu: int = ReMatch(r"mtu (\d+)")
    qdisc: str = ReMatch(r"qdisc (\w+)")
    state: str = ReMatch(r"state ([A-Z]+)")
    group: str = ReMatch(r"group (\w+)", default="unknown")
    qlen: int = ReMatch(r"qlen (\d+)")
    link: str = ReMatch(r"link/(\w+)")
    addr: str = ReMatch(r"link/\w+ ([\d:a-z]+)")
    ipv4: list[str] = ReMatchList(r"inet ([\d./]+)")
    ipv6: list[str] = ReMatchList(r"inet6 ([a-z\d./:]+)")
