import os.path
import pathlib
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, cast

from backend import Backend

NODE_DIRECTORY = 0
NODE_FILE = 1


class Node:

    _backend: Optional[Backend]
    _children: Dict[str, "Node"]
    _indexed: bool
    _modification_time: int
    _name: str
    _parent: Optional["Node"]
    _size: int
    _type: int

    def __init__(self, name: str = "", parent: Optional["Node"] = None) -> None:

        self._backend = None
        self._name = name
        self._type = NODE_DIRECTORY
        self._children = {}
        self._parent = parent
        self._size = -1
        self._modification_time = -1
        self._indexed = True

    def setName(self, name: str) -> None:
        self._name = name

    def getName(self) -> str:
        return self._name

    def setDirectory(self) -> None:
        self._type = NODE_DIRECTORY

    def setFile(self) -> None:
        self._type = NODE_FILE

    def isDirectory(self) -> bool:
        return self._type == NODE_DIRECTORY

    def isFile(self) -> bool:
        return self._type == NODE_FILE

    def getChildren(self) -> List["Node"]:
        return list(self._children.values())

    def addChild(self, child: "Node") -> None:

        if self.isFile():
            raise IOError(
                "trying to add child {child} to parent {parent}: files cannot have children".format(
                    child=child, parent=self
                )
            )

        child.setParent(self)
        child.setBackend(cast(Backend, self._backend))
        self._children[child.getName()] = child

    def getParent(self) -> Optional["Node"]:
        return self._parent

    def setParent(self, parent: Optional["Node"]) -> None:
        self._parent = parent

    def getRoot(self) -> "Node":

        root: "Node" = self

        while root._parent is not None:
            root = root._parent

        return root

    def isRoot(self) -> bool:
        return self._parent is None

    def getPath(self) -> pathlib.Path:

        if self._parent is None:
            return pathlib.Path(self._name)

        return self._parent.getPath() / self._name

    def serialize(self) -> Dict[str, Any]:

        child: "Node"
        ser: Dict[str, Any] = {
            "name": self._name,
            "type": self._type,
            "children": [],
        }

        if self.isFile():
            ser["size"] = self._size
            ser["mtime"] = self._modification_time

        for child in self._children.values():
            ser["children"].append(child.serialize())

        return ser

    def deserialize(self, serialized: Dict[str, Any]) -> None:

        child: Dict[str, Any]

        self.removeAllChildren()
        self._name = serialized.get("name", "")
        self._type = serialized.get("type", "")

        if self.isFile():
            self._size = serialized.get("size", -1)
            self._modification_time = serialized.get("mtime", -1)

        children: List[Dict[str, Any]] = serialized.get("children", [])

        for child in children:

            node: "Node" = Node()
            node.deserialize(child)
            node.setParent(self)
            node.setBackend(cast(Backend, self._backend))
            self._children[node.getName()] = node

    def findChild(self, location: Union["Node", str]) -> Optional["Node"]:

        path: pathlib.Path

        if isinstance(location, Node):
            try:
                path = location.getPath().relative_to(self.getPath())
            except ValueError:
                if self.getPath() == pathlib.Path(""):
                    path = location.getPath()
                else:
                    # paths do not overlap -> child is not in that part of the tree
                    return None
        elif isinstance(location, str):
            path = pathlib.Path(location)
        else:
            raise NotImplementedError()

        if path == pathlib.Path(""):
            return self

        parts: Tuple[str, ...] = path.parts
        child_name: str = parts[0]

        child: Optional["Node"] = self._children.get(child_name, None)

        if child:
            if len(parts) == 1:
                return child
            else:
                return child.findChild(os.path.join(*parts[1:]))

        return None

    # depth = 0: return all children
    # depth > 0: return only children with a depth level given by depth
    # files: return files
    # dirs: return directories
    # files and dirs allow proper filtering of the iterated children
    # indexed: return only indexed children

    def iterChildren(
        self,
        depth: int = 0,
        files: bool = True,
        dirs: bool = True,
        indexed: bool = False,
    ) -> Iterator["Node"]:

        child: Node

        if indexed and not self.isIndexed(recursive=True):
            return

        for child in self._children.values():

            if indexed and not child.isIndexed(recursive=True):
                continue

            if depth > 1:
                yield from child.iterChildren(
                    depth=depth - 1, files=files, dirs=dirs, indexed=indexed
                )
            elif depth == 1:
                if (dirs and child.isDirectory()) or (files and child.isFile()):
                    yield child
            elif depth == 0:
                if files and child.isFile():
                    yield child
                elif child.isDirectory():
                    yield from child.iterChildren(
                        depth=0, files=files, dirs=dirs, indexed=indexed
                    )

    def __str__(self) -> str:

        desc: str = "<"

        if self.isFile():
            desc = desc + "File at " + self.getPath().as_posix()
        else:
            desc = desc + "Directory at " + self.getPath().as_posix()

        desc = desc + ">"

        return desc

    def __repr__(self) -> str:
        return str(self)

    def removeChild(self, child: "Node") -> None:

        if child.getName() not in self._children:
            return

        del self._children[child.getName()]

        child.setParent(None)

        child.removeAllChildren()

    def removeAllChildren(self) -> None:

        child: "Node"

        for child in self._children.values():
            child.setParent(None)
            child.removeAllChildren()

        self._children.clear()

    def clean(self) -> None:

        child: "Node"

        for child in self._children.values():

            if not child.isIndexed():
                # the element is flagged as 'not indexed', thus it can be dropped
                # if its a directory, it should take all of its children with it
                self.removeChild(child)
                continue

            if child.isDirectory():

                child.clean()

                # directories without supported files don't need to exist in our tree
                if len(child.getChildren()) == 0:
                    self.removeChild(child)

    # if recursive: return False as soon as all children are not indexed
    # means: return True as soon as at least one child is indexed
    # will return False for empty directories as well

    def isIndexed(self, recursive: bool = False) -> bool:

        if self.isDirectory() and len(self._children) == 0:
            return False

        if not recursive or len(self._children) == 0:
            return self._indexed

        child: "Node"

        for child in self._children.values():
            if child.isIndexed(recursive=True):
                return True

        return False

    def setIndexed(self, recursive: bool = False) -> None:

        child: "Node"

        self._indexed = True

        if recursive:

            for child in self._children.values():
                child.setIndexed(recursive)

    def setNotIndexed(self, recursive: bool = False) -> None:

        child: "Node"

        self._indexed = False

        if recursive:

            for child in self._children.values():
                child.setNotIndexed(recursive)

    def setBackend(self, backend: Backend) -> None:

        child: "Node"

        self._backend = backend

        for child in self._children.values():
            child.setBackend(backend)

    def getBackend(self) -> Optional[Backend]:
        return self._backend

    def getModificationTime(self) -> int:

        if not self.isFile():
            raise IOError("{node} is not a file".format(node=self))

        return self._modification_time

    def setModificationTime(self, time: int) -> None:

        if not self.isFile():
            raise IOError("{node} is not a file".format(node=self))

        self._modification_time = time

    def getSize(self) -> int:

        if not self.isFile():
            raise IOError("{node} is not a file".format(node=self))

        return self._size

    def setSize(self, size: int) -> None:

        if not self.isFile():
            raise IOError("{node} is not a file".format(node=self))

        self._size = size
