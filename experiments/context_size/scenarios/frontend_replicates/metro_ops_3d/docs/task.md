# Task Notes

Useful areas for agent comparison:

- `src/telemetry.js` owns static route thresholds and vehicle positions.
- `src/panels.js` owns the textual status classification.
- `src/scene.js` owns the visual pulse intensity tied to route load.

Expected edit target for the threshold task is only `criticalLoadThreshold` values in `src/telemetry.js`.
