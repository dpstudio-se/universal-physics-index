"""Command-line demonstration of the deterministic swarm protocol."""

import argparse
import json

from .core import NodeObservation, SwarmCoordinator


def _demo() -> dict[str, object]:
    node_ids = {f"{number:016x}" for number in range(1, 10)}
    coordinator = SwarmCoordinator(node_ids)
    for number, node_id in enumerate(sorted(node_ids), start=1):
        coordinator.observe(
            NodeObservation(
                node_id=node_id,
                quality=number / 10,
                latency_ms=float(10 - number),
                sequence=1,
            )
        )
    return dict(coordinator.topology())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the VR-ASI 3-6-9 coordination demo")
    parser.add_argument("command", choices=("demo",))
    parser.parse_args()
    print(json.dumps(_demo(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
