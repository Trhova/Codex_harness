# Collaborative Canvas Board Fixture

This fixture represents a lightweight whiteboard UI with tool state, drawing commands, comments, and layer rendering.

Primary comparison task:

- Ask the agent to add a locked `handoff annotations` layer that renders above sketches but below comments, and make sure selection ignores locked layers.

Good transcript search pattern:

`boardLayers|locked|hitTestLayer|renderLayerStack`
