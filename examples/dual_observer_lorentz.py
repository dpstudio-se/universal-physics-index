"""Run the UPI dual-observer Lorentz example."""

import json

from upi.constants import C
from upi.dual_observer import Event1D, dual_observer_trace, lorentz_transform_event


def main() -> None:
    observer_a = Event1D(time_s=2e-6, position_m=300.0)
    velocity = 0.6 * C
    predicted_b = lorentz_transform_event(observer_a, velocity)

    clean = dual_observer_trace(
        observer_a,
        velocity,
        time_tolerance_s=1e-9,
        position_tolerance_m=0.1,
    )
    biased = dual_observer_trace(
        observer_a,
        velocity,
        observed_b=Event1D(
            time_s=predicted_b.time_s + 2e-9,
            position_m=predicted_b.position_m + 0.25,
        ),
        time_tolerance_s=1e-9,
        position_tolerance_m=0.1,
    )

    print(json.dumps({"clean": clean.as_dict(), "biased": biased.as_dict()}, indent=2))


if __name__ == "__main__":
    main()
