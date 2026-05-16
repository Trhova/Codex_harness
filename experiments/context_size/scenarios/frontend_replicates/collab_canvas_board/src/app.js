import { boardLayers, boardComments } from "./data.js";
import { renderLayerStack } from "./renderer.js";
import { createToolRail } from "./tools.js";
import { hitTestLayer } from "./selection.js";
import { renderComments } from "./comments.js";

const canvas = document.querySelector("#board-canvas");
const toolRail = document.querySelector("#tool-rail");
const commentsPanel = document.querySelector("#comments-panel");

const state = {
  tool: "select",
  selectedShapeId: null,
};

createToolRail(toolRail, state, () => renderLayerStack(canvas, boardLayers, state.selectedShapeId));
renderComments(commentsPanel, boardComments);
renderLayerStack(canvas, boardLayers, state.selectedShapeId);

canvas.addEventListener("pointerdown", (event) => {
  const rect = canvas.getBoundingClientRect();
  const point = {
    x: ((event.clientX - rect.left) / rect.width) * canvas.width,
    y: ((event.clientY - rect.top) / rect.height) * canvas.height,
  };
  state.selectedShapeId = hitTestLayer(boardLayers, point)?.id ?? null;
  renderLayerStack(canvas, boardLayers, state.selectedShapeId);
});
