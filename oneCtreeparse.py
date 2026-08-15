import os
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QMimeData, Qt


class MetadataNode:
    """Узел дерева метаданных 1С (папка или файл)"""

    def __init__(self, name: str, path: str, parent: 'MetadataNode | None' = None):
        self.name = name
        self.path = path
        self.parent = parent
        self.children = None
        self.is_dir = os.path.isdir(path)

    def load_children(self) -> list:
        if self.children is not None:
            return self.children
        result = []
        try:
            entries = sorted(os.listdir(self.path))
        except OSError:
            self.children = result
            return result
        for entry in entries:
            result.append(MetadataNode(entry, os.path.join(self.path, entry), self))
        self.children = result
        return result

    def row(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.children.index(self)

    def child(self, row: int) -> 'MetadataNode':
        return self.children[row]


class DirectoryTreeAdapter(QAbstractItemModel):
    """Модель дерева метаданных 1С для QTreeView"""

    def __init__(self, root_path: str):
        super().__init__()
        self.base_dir = '1CMetadata'
        self.root = MetadataNode(os.path.basename(os.path.normpath(root_path)), root_path)
        self.root.load_children()

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1

    def rowCount(self, parent=QModelIndex()) -> int:
        if not parent.isValid():
            return len(self.root.children) if self.root.children is not None else 0
        node = parent.internalPointer()
        return len(node.children) if node.children is not None else 0

    def canFetchMore(self, parent=QModelIndex()) -> bool:
        if not parent.isValid():
            return self.root.is_dir and self.root.children is None
        node = parent.internalPointer()
        return node.is_dir and node.children is None

    def hasChildren(self, parent=QModelIndex()) -> bool:
        if not parent.isValid():
            return self.root.is_dir
        node = parent.internalPointer()
        if node.children is not None:
            return len(node.children) > 0
        return node.is_dir

    def fetchMore(self, parent=QModelIndex()):
        if not parent.isValid():
            node, parent_index = self.root, QModelIndex()
        else:
            node, parent_index = parent.internalPointer(), parent
        if not node.is_dir or node.children is not None:
            return
        children = node.load_children()
        self.beginInsertRows(parent_index, 0, len(children) - 1)
        self.endInsertRows()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return node.name
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled

    def mimeTypes(self) -> list:
        return ['text/plain']

    def mimeData(self, indexes) -> QMimeData:
        mime = QMimeData()
        for index in indexes:
            if index.isValid():
                node = index.internalPointer()
                rel_path = os.path.relpath(node.path, self.base_dir)
                mime.setText(rel_path)
                break
        return mime

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole and section == 0:
            return "Метаданные"
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            if self.root.children is None:
                return QModelIndex()
            node = self.root.children[row]
        else:
            node = parent.internalPointer()
            if node.children is None:
                return QModelIndex()
            node = node.children[row]
        return self.createIndex(row, column, node)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        parent_node = node.parent
        if parent_node is None or parent_node is self.root:
            return QModelIndex()
        return self.createIndex(parent_node.row(), 0, parent_node)