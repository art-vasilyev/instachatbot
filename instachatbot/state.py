import typing

from instachatbot.nodes import MenuNode, Node
from instachatbot.storage import Storage, MemoryStorage


class Conversation:
    def __init__(self, menu: MenuNode, storage: Storage):
        if storage is None:
            storage = MemoryStorage()
        self.storage = storage
        self._position_map = {}
        self._build_position_map([menu])

    def get_state(self, chat_id):
        state = self.storage.load(chat_id)
        if state and state.get('node'):
            node = self._get_node(state['node'])
            state['node'] = node
        return state

    def save_state(self, chat_id, state):
        if state and state.get('node'):
            node_path = self._get_node_path(state['node'])
            state['node'] = node_path
        self.storage.save(chat_id, state)

    def _build_position_map(self, node: typing.List[Node], prefix=''):
        for i, node in enumerate(node, start=1):
            if prefix:
                node_path = prefix + '.' + str(i)
            else:
                node_path = str(i)

            self._position_map[node_path] = node

            if isinstance(node, MenuNode):
                self._build_position_map(
                    [item.node for item in node.items], prefix=node_path)

    def _get_node(self, node_path: str):
        return self._position_map.get(node_path)

    def _get_node_path(self, node: Node):
        for node_path in self._position_map:
            if node is self._position_map[node_path]:
                return node_path
