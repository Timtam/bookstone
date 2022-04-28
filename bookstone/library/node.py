import posixpath
from typing import Any, Dict, Iterator, List, Optional, Union

NODE_DIRECTORY = 0
NODE_FILE = 1


class Node:

    _children: Dict[str, "Node"]
    _modification_time: int
    _name: str
    _parent: Optional["Node"]
    _size: int
    _type: int

    def __init__(self, name: str = "", parent: Optional["Node"] = None) -> None:

        self._name = name
        self._type = NODE_DIRECTORY
        self._children = {}
        self._parent = parent
        self._size = -1
        self._modification_time = -1

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

        if self.findChild(child):
            raise ValueError(f"a child {child} for {self} already exists")

        child.setParent(self)
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

    def getPath(self) -> str:

        path: str = self._name
        current: Optional["Node"] = self._parent

        while current:

            if current._name != "":
                path = current._name + "/" + path

            current = current._parent

        return path

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
            self._children[node.getName()] = node

    def findChild(self, location: Union["Node", str]) -> Optional["Node"]:

        self_path = self.getPath()
        path: str

        if isinstance(location, Node):
            location_path = location.getPath()
            try:
                # if we're checking at root level and two nested folders are named exactly the same way
                # the algorithm thinks that they are the same
                # compare a Node abc with a Node abc fails, because they are called the same
                # but we are meant to check for children only
                if location_path == self_path:
                    path = location_path
                else:
                    path = posixpath.relpath(location_path, self_path)
            except ValueError:
                if self_path == "":
                    path = location_path
                else:
                    # paths do not overlap -> child is not in that part of the tree
                    return None
        elif isinstance(location, str):
            path = location
        else:
            raise NotImplementedError()

        if path == "":
            return self

        parts: List[str] = path.split("/")
        child_name: str = parts[0]

        child: Optional["Node"] = self._children.get(child_name, None)

        if child:
            if len(parts) == 1:
                return child
            else:
                return child.findChild(posixpath.join(*parts[1:]))

        return None

    # depth = 0: return all children
    # depth > 0: return only children with a depth level given by depth
    # files: return files
    # dirs: return directories
    # files and dirs allow proper filtering of the iterated children

    def iterChildren(
        self,
        depth: int = 0,
        files: bool = True,
        dirs: bool = True,
    ) -> Iterator["Node"]:

        child: Node

        for child in list(self._children.values()):

            if depth > 1:
                yield from child.iterChildren(depth=depth - 1, files=files, dirs=dirs)
            elif depth == 1:
                if (dirs and child.isDirectory()) or (files and child.isFile()):
                    yield child
            elif depth == 0:
                if files and child.isFile():
                    yield child
                elif child.isDirectory():
                    yield from child.iterChildren(depth=0, files=files, dirs=dirs)

    def __str__(self) -> str:

        desc: str = "<"

        if self.isFile():
            desc = desc + "File at " + self.getPath()
        else:
            desc = desc + "Directory at " + self.getPath()

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

    def isParentOf(self, child: Union["Node", str]) -> bool:

        path: str

        if isinstance(child, str):
            path = child
        else:
            path = child.getPath()

        if self._name == "":
            if path == "":
                return False
            return True

        return path.startswith(self.getPath())

    def __eq__(self, node: Any) -> bool:

        if isinstance(node, Node):
            return self.getPath() == node.getPath()
        elif isinstance(node, str):
            return self.getPath() == node

        return NotImplemented
