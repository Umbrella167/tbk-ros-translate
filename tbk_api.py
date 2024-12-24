import tzcp.tbk.tbk_pb2 as tbkpb
import etcd3
import os


class TBKApi:
    def __init__(self):
        self.MESSAGE_PREFIX = "/tbk/ps"
        self.PARAM_PREFIX = "/tbk/params"
        self.etcd = self._client()

    def _client(self):
        pkipath = os.path.join(os.path.expanduser("~"), ".tbk/etcdadm/pki")
        return etcd3.client(
            host="127.0.0.1",
            port=2379,
            ca_cert=os.path.join(pkipath, "ca.crt"),
            cert_key=os.path.join(pkipath, "etcdctl-etcd-client.key"),
            cert_cert=os.path.join(pkipath, "etcdctl-etcd-client.crt"),
        )

    def get_message(self):
        processes = {}
        publishers = {}
        subscribers = {}
        res = self.etcd.get_prefix(self.MESSAGE_PREFIX)
        for r in res:
            key, value = r[1].key.decode(), r[0]
            keys = key[len(self.MESSAGE_PREFIX) :].split("/")[1:]
            info = None
            if len(keys) == 1:
                info = tbkpb.State()
                info.ParseFromString(value)
                processes[info.uuid] = info
            elif len(keys) == 3:
                if keys[1] == "pubs":
                    info = tbkpb.Publisher()
                    info.ParseFromString(value)
                    publishers[info.uuid] = info
                elif keys[1] == "subs":
                    info = tbkpb.Subscriber()
                    info.ParseFromString(value)
                    subscribers[info.uuid] = info
        res = {"ps": processes, "pubs": publishers, "subs": subscribers}
        self.message_data = res
        return res

    @property
    def message_tree(self):
        self.get_message()
        message_tree = {}
        for node_type in self.message_data:
            tree = {}
            if node_type == "ps":
                continue
            elif node_type == "subs":
                continue
            elif node_type == "pubs":
                data = self.message_data[node_type]
                for uuid in data:
                    node_name = data[uuid].ep_info.node_name
                    puuid = f"{node_name}_{data[uuid].puuid}"
                    if puuid not in tree:
                        tree[puuid] = {}
                    tree[puuid][uuid] = data[uuid]
            message_tree[node_type] = tree
        return message_tree
