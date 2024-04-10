from ipv8.peerdiscovery.network import PeerObserver
from asyncio import run
from binascii import hexlify
import hashlib
from ipv8.community import Community, CommunitySettings
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.payload_dataclass import dataclass
from ipv8.types import Peer
from ipv8.util import run_forever
from ipv8_service import IPv8

@dataclass(msg_id=1)  # The value 1 identifies this message and must be unique per community
class MyMessage:
    name: str
    nonce: int

message_save = {}
def find_hash_with_leading_zeros(message, k):
    prefix = '0' * k
    nonce = 0
    while True:
        encoded = str(message).encode() + str(nonce).encode()
        hash_result = hashlib.sha256(encoded ).hexdigest()
        if hash_result.startswith(prefix):
            # message[nonce] = [new_message, hash_result]
            print("Found hash:", hash_result)
            return {"message": message, "hash": nonce}
        nonce += 1
class MyCommunity(Community, PeerObserver):
    community_id = b'harbourspaceuniverse'


    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        # Register the message handler for messages (with the identifier "1").
        self.add_message_handler(MyMessage, self.on_message)
        # The Lamport clock this peer maintains.
        # This is for the example of global clock synchronization.
        self.lamport_clock = 0

    def started(self) -> None:
        self.message = find_hash_with_leading_zeros("Victor", 6);

        self.network.add_peer_observer(self)

    @lazy_wrapper(MyMessage)
    def on_message(self, peer: Peer, payload: MyMessage) -> None:
        self.lamport_clock = max(self.lamport_clock, payload.clock) + 1
        print(self.my_peer, "current clock:", self.lamport_clock)
    def on_peer_added(self, peer: Peer) -> None:
        print("I am:", self.my_peer, "I found:", peer)
        my_message = MyMessage( self.message["message"], self.message["hash"])
        print("My message:", my_message)
        self.ez_send(peer, my_message)
        print("Sent message to:", hexlify(peer.mid).decode())
        if hexlify(peer.mid).decode() == '2c060eccf67dcdc126aa18c6123617f84411d076':
            print("Found teacher");


    def on_peer_removed(self, peer: Peer) -> None:
        pass

    # def started(self) -> None:
    #     self.network.add_peer_observer(self)


async def start_communities() -> None:
    for i in [1]:
        builder = ConfigBuilder().clear_keys().clear_overlays()
        builder.add_key("my peer", "medium", f"ec{i}.pem")
        builder.add_overlay("MyCommunity", "my peer",
                            [WalkerDefinition(Strategy.RandomWalk,
                                              10, {'timeout': 3.0})],
                            default_bootstrap_defs, {}, [('started',)])
        await IPv8(builder.finalize(),
                   extra_communities={'MyCommunity': MyCommunity}).start()
    await run_forever()

run(start_communities())
