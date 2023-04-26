from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList


class Device(BaseSchema):
    num: ScField[int, ReMatch(r"^(\d+):")]
    name: ScField[str, ReMatch(r"^\d+: (\w+):")]
    interface: ScField[
        list[str], ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(",") if s else [])
    ]
    mtu: ScField[int, ReMatch(r"mtu (\d+)")]
    qdisc: ScField[str, ReMatch(r"qdisc (\w+)")]
    state: ScField[str, ReMatch(r"state ([A-Z]+)")]
    group: ScField[str, ReMatch(r"group (\w+)", default="unknown")]
    qlen: ScField[int, ReMatch(r"qlen (\d+)")]
    link: ScField[str, ReMatch(r"link/(\w+)")]
    addr: ScField[str, ReMatch(r"link/\w+ ([\d:a-z]+)")]
    ipv4: ScField[list[str], ReMatchList(r"inet ([\d./]+)")]
    ipv6: ScField[list[str], ReMatchList(r"inet6 ([a-z\d./:]+)")]
