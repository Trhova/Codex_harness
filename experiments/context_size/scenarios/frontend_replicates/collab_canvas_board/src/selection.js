export function hitTestLayer(boardLayers, point) {
  for (let layerIndex = boardLayers.length - 1; layerIndex >= 0; layerIndex -= 1) {
    const layer = boardLayers[layerIndex];
    if (layer.locked) {
      continue;
    }
    for (let shapeIndex = layer.shapes.length - 1; shapeIndex >= 0; shapeIndex -= 1) {
      const shape = layer.shapes[shapeIndex];
      if (containsPoint(shape, point)) {
        return shape;
      }
    }
  }
  return null;
}

function containsPoint(shape, point) {
  if (shape.type === "rect") {
    return point.x >= shape.x && point.x <= shape.x + shape.width && point.y >= shape.y && point.y <= shape.y + shape.height;
  }
  if (shape.type === "circle") {
    return Math.hypot(point.x - shape.x, point.y - shape.y) <= shape.radius;
  }
  if (shape.type === "line") {
    const length = Math.hypot(shape.x2 - shape.x, shape.y2 - shape.y);
    const d1 = Math.hypot(point.x - shape.x, point.y - shape.y);
    const d2 = Math.hypot(point.x - shape.x2, point.y - shape.y2);
    return Math.abs(d1 + d2 - length) < 8;
  }
  return false;
}
