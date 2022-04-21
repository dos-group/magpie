
from magpie.types.str_enum import StrEnum


class DFS(StrEnum):
    """
    distributed file system
    """
    CEPH = "ceph"
    LUSTRE = "lustre"
    TOY = "toy"
