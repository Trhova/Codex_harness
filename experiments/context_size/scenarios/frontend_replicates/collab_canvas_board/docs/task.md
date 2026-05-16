# Task Notes

Useful areas for agent comparison:

- `src/data.js` owns layer ordering and the `locked` flag.
- `src/renderer.js` draws layers in array order and dims locked shapes.
- `src/selection.js` already skips locked layers during hit testing.

Expected edit target for the handoff annotations task is mostly `boardLayers`.
