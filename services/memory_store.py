from datetime import datetime

class MemoryStore:
    def __init__(self):
        self._store = {}
        self._history = []

    def write(self, agent_name, key, value):
        namespaced_key = f"{agent_name}::{key}"
        self._store[namespaced_key] = value
        self._history.append({
            "agent": agent_name,
            "key": key,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": str(value)[:200],
        })

    def read(self, agent_name, key):
        return self._store.get(f"{agent_name}::{key}")

    def read_all(self, agent_name):
        prefix = f"{agent_name}::"
        return {k.replace(prefix, ""): v for k, v in self._store.items() if k.startswith(prefix)}

    def get_history(self):
        return self._history

    def snapshot(self):
        return dict(self._store)

memory = MemoryStore()
