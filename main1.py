from asyncio import run

from ipv8.community import Community
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8.peerdiscovery.network import PeerObserver
from ipv8.types import Peer
from ipv8.util import run_forever
from ipv8_service import IPv8


class PuzzleCommunity(Community, PeerObserver):
    community_id = b'harbourspaceuniverse'  # Ensure this is 20 bytes

    def init(self, args, **kwargs):
        super().init(args, **kwargs)
        self.network.add_peer_observer(self)

    def started(self) -> None:
        # super().started()
        print("Current peers in the community:")
        for peer in self.get_peers():
            print(peer)
        print("end print----")

    def on_peer_added(self, peer: Peer) -> None:
        print("I am:", self.my_peer, "I found:", peer)

    def on_peer_removed(self, peer: Peer) -> None:
        pass


async def start_communities() -> None:
    ec_my = '123541'

    builder = ConfigBuilder().clear_keys().clear_overlays()
    builder.add_key("my peer", "medium", f"ec{ec_my}.pem")

    builder.add_overlay("PuzzleCommunity", "my peer",
                        [WalkerDefinition(Strategy.RandomWalk,
                                          20, {'timeout': 3.0})],
                        default_bootstrap_defs, {}, [('started',)])
    await IPv8(builder.finalize(),
               extra_communities={'PuzzleCommunity': PuzzleCommunity}).start()

    await run_forever()


run(start_communities())
