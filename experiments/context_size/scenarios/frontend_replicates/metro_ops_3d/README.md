# Metro Ops 3D Fixture

This fixture models a command-center UI wrapped around a Three.js-style city scene. It is intentionally small, but the behavior is split across scene construction, telemetry data, controls, and panel rendering.

Primary comparison task:

- Ask the agent to find where transit vehicle pulse colors and critical route alerts are implemented, then change the critical route threshold from `82` to `88` without altering panel copy.

Good transcript search pattern:

`criticalLoadThreshold|routeStatus|pulseVehicleLights|drawAlertPanel`
