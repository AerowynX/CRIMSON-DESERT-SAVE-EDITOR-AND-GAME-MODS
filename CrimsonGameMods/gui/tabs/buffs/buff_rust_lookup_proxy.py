import logging
import json
from collections.abc import MutableMapping, MutableSequence

from PySide6.QtCore import QObject, Signal

log = logging.getLogger(__name__)

class _ProxyState(QObject):
    history_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.history_paused = False
        self.logging = True

class BuffRustLookupProxy(MutableMapping, dict):
    """
    A dictionary proxy that wraps _buff_rust_lookup and its nested dictionaries.
    It captures any changes to the referenced items and outputs them to the log,
    while maintaining a history of changes that can be reverted.
    """
    def __init__(self, name="_buff_rust_lookup", target=None, history=None, state=None):
        dict.__init__(self)
        self._name = name
        self._target = target if target is not None else {}
        self._history = history if history is not None else []
        self._state = state if state is not None else _ProxyState()
        dict.update(self, self._target)

    @property
    def history_changed(self):
        return self._state.history_changed

    def __getitem__(self, key):
        val = self._target[key]
        if isinstance(val, dict) and not isinstance(val, BuffRustLookupProxy):
            return BuffRustLookupProxy(f"{self._name}[{key}]", val, history=self._history, state=self._state)
        elif isinstance(val, list) and not type(val).__name__ == "BuffRustLookupListProxy":
            return BuffRustLookupListProxy(f"{self._name}[{key}]", val, history=self._history, state=self._state)
        return val

    def __setitem__(self, key, value):
        key_existed = key in self._target
        old_val = self._target.get(key)
        if old_val != value:
            self.add_to_history(
                action="set",
                target=self._target,
                key=key,
                path=f"{self._name}[{key}]",
                old_val=old_val,
                new_val=value,
                key_existed=key_existed
            )
            if self._state.logging:
                log.info("Proxy modification: %s[%r] changed from %r to %r", self._name, key, old_val, value)
        self._target[key] = value
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        if key in self._target:
            old_val = self._target[key]
            self.add_to_history(
                action="del",
                target=self._target,
                key=key,
                path=f"{self._name}[{key}]",
                old_val=old_val,
                new_val=None,
                key_existed=True
            )
            if self._state.logging:
                log.info("Proxy deletion: %s[%r] deleted", self._name, key)
            del self._target[key]
            dict.__delitem__(self, key)
        else:
            del self._target[key]  # let it raise KeyError

    def __iter__(self):
        return iter(self._target)

    def __len__(self):
        return len(self._target)

    def __repr__(self):
        return repr(self._target)
        
    def __str__(self):
        return str(self._target)

    # --- History Tracking & Reverting ---

    def add_to_history(self, action, target, key, path, old_val=None, new_val=None, key_existed=True, revert_callback=None):
        """
        Manually add an entry to the tracked history.
        This does not modify the proxy object itself, allowing for
        tracking changes made directly to the underlying referenced data.
        """
        if self._state.history_paused:
            return
            
        entry = {
            "action": action,
            "proxy": self,
            "target": target,
            "key": key,
            "path": path,
            "old_val": old_val,
            "new_val": new_val,
            "key_existed": key_existed,
            "revert_callback": revert_callback
        }
        self._history.append(entry)
        self._state.history_changed.emit()

    def get_most_recent_change(self):
        """
        Returns the most recent change as a formatted JSON string.
        """
        if not self._history:
            return "No recent changes."
            
        entry = self._history[-1]
        
        # Create a serializable version of the entry for formatting
        formatted_entry = {
            "action": entry["action"],
            "path": entry["path"],
            "key": entry["key"],
            "key_existed": entry["key_existed"]
        }
        
        # We try to use the raw value if it is serializable, else use str()
        try:
            json.dumps(entry.get("old_val"))
            formatted_entry["old_val"] = entry.get("old_val")
        except (TypeError, ValueError):
            formatted_entry["old_val"] = str(entry.get("old_val"))
            
        try:
            json.dumps(entry.get("new_val"))
            formatted_entry["new_val"] = entry.get("new_val")
        except (TypeError, ValueError):
            formatted_entry["new_val"] = str(entry.get("new_val"))
            
        return json.dumps(formatted_entry, indent=2)

    def get_formatted_history(self):
        """
        Returns the entire history of changes as a formatted JSON string.
        """
        if not self._history:
            return "No changes recorded."
            
        formatted_history = []
        for entry in self._history:
            formatted_entry = {
                "action": entry["action"],
                "path": entry["path"],
                "key": entry["key"],
                "key_existed": entry["key_existed"]
            }
            
            try:
                json.dumps(entry.get("old_val"))
                formatted_entry["old_val"] = entry.get("old_val")
            except (TypeError, ValueError):
                formatted_entry["old_val"] = str(entry.get("old_val"))
                
            try:
                json.dumps(entry.get("new_val"))
                formatted_entry["new_val"] = entry.get("new_val")
            except (TypeError, ValueError):
                formatted_entry["new_val"] = str(entry.get("new_val"))
                
            formatted_history.append(formatted_entry)
            
        return json.dumps(formatted_history, indent=2)

    @staticmethod
    def default_revert_callback(entry):
        """
        The default technique for reverting a history entry.
        Modifies the underlying target dictionary directly to avoid 
        triggering the proxy's logging and history tracking.
        """
        target = entry["target"]
        proxy = entry.get("proxy")
        key = entry["key"]
        action = entry["action"]
        key_existed = entry["key_existed"]
        old_val = entry["old_val"]
        path = entry.get("path", str(key))
        
        is_list = isinstance(target, list)

        if action == "set":
            if key_existed:
                log.info("Proxy revert: %s changed back to %r", path, old_val)
                target[key] = old_val
                if proxy is not None:
                    if is_list:
                        list.__setitem__(proxy, key, old_val)
                    else:
                        dict.__setitem__(proxy, key, old_val)
            else:
                log.info("Proxy revert: %s removed (was newly added)", path)
                if not is_list:
                    if key in target:
                        del target[key]
                    if proxy is not None and key in proxy:
                        dict.__delitem__(proxy, key)
        elif action == "del":
            log.info("Proxy revert: %s restored to %r (was deleted)", path, old_val)
            if is_list:
                target.insert(key, old_val)
                if proxy is not None:
                    list.insert(proxy, key, old_val)
            else:
                target[key] = old_val
                if proxy is not None:
                    dict.__setitem__(proxy, key, old_val)
        elif action == "insert":
            log.info("Proxy revert: %s removed (was inserted)", path)
            target.pop(key)
            if proxy is not None:
                list.pop(proxy, key)

    def revert_most_recent_change(self, revert_callback=None):
        """
        Reverts the most recent change. 
        If a callback is passed, it is used. Otherwise, it uses the callback 
        stored in the history entry, and falls back to the default technique.
        """
        if not self._history:
            return False
            
        entry = self._history.pop()
        
        callback = revert_callback or entry.get("revert_callback") or BuffRustLookupProxy.default_revert_callback
        callback(entry)
        self._state.history_changed.emit()
            
        return True

    def get_underlying_dict(self):
        """
        Retrieve the raw, un-proxied dictionary object.
        """
        return self._target

    def clear_history(self):
        """
        Clears the tracked history of changes.
        """
        self._history.clear()
        self._state.history_changed.emit()

    def pause_history(self):
        """
        Pauses history tracking so modifications are not logged or appended.
        """
        self._state.history_paused = True

    def resume_history(self):
        """
        Resumes history tracking.
        """
        self._state.history_paused = False


class BuffRustLookupListProxy(MutableSequence, list):
    """
    A list proxy that wraps a target list and its nested dictionaries/lists.
    Captures any changes to the referenced items and outputs them to the log,
    while maintaining a history of changes that can be reverted.
    """
    def __init__(self, name, target, history, state):
        list.__init__(self)
        self._name = name
        self._target = target
        self._history = history
        self._state = state
        list.extend(self, self._target)

    @property
    def history_changed(self):
        return self._state.history_changed

    def __getitem__(self, index):
        val = self._target[index]
        if isinstance(val, dict) and not isinstance(val, BuffRustLookupProxy):
            return BuffRustLookupProxy(f"{self._name}[{index}]", val, history=self._history, state=self._state)
        elif isinstance(val, list) and not type(val).__name__ == "BuffRustLookupListProxy":
            return BuffRustLookupListProxy(f"{self._name}[{index}]", val, history=self._history, state=self._state)
        return val

    def __setitem__(self, index, value):
        old_val = self._target[index]
        if old_val != value:
            self.add_to_history(
                action="set",
                target=self._target,
                key=index,
                path=f"{self._name}[{index}]",
                old_val=old_val,
                new_val=value,
                key_existed=True
            )
            if self._state.logging:
                log.info("Proxy modification: %s[%r] changed from %r to %r", self._name, index, old_val, value)
        self._target[index] = value
        list.__setitem__(self, index, value)

    def __delitem__(self, index):
        old_val = self._target[index]
        self.add_to_history(
            action="del",
            target=self._target,
            key=index,
            path=f"{self._name}[{index}]",
            old_val=old_val,
            new_val=None,
            key_existed=True
        )
        if self._state.logging:
            log.info("Proxy deletion: %s[%r] deleted", self._name, index)
        del self._target[index]
        list.__delitem__(self, index)

    def insert(self, index, value):
        self.add_to_history(
            action="insert",
            target=self._target,
            key=index,
            path=f"{self._name}[{index}]",
            old_val=None,
            new_val=value,
            key_existed=False
        )
        if self._state.logging:
            log.info("Proxy insertion: %s[%r] inserted %r", self._name, index, value)
        self._target.insert(index, value)
        list.insert(self, index, value)

    def __len__(self):
        return len(self._target)

    def add_to_history(self, action, target, key, path, old_val=None, new_val=None, key_existed=True, revert_callback=None):
        if self._state.history_paused:
            return
            
        entry = {
            "action": action,
            "proxy": self,
            "target": target,
            "key": key,
            "path": path,
            "old_val": old_val,
            "new_val": new_val,
            "key_existed": key_existed,
            "revert_callback": revert_callback
        }
        self._history.append(entry)
        self._state.history_changed.emit()

    def get_underlying_list(self):
        return self._target
