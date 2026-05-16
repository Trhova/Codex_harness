export function renderLayerStack(canvas, boardLayers, selectedShapeId) {
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBackground(ctx, canvas);

  boardLayers.forEach((layer) => {
    layer.shapes.forEach((shape) => {
      drawShape(ctx, shape, shape.id === selectedShapeId, layer.locked);
    });
  });
}

function drawBackground(ctx, canvas) {
  ctx.fillStyle = "#f8fafc";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#dde4ee";
  ctx.lineWidth = 1;
  for (let x = 0; x < canvas.width; x += 40) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  for (let y = 0; y < canvas.height; y += 40) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
}

function drawShape(ctx, shape, selected, locked) {
  ctx.save();
  ctx.globalAlpha = locked ? 0.48 : 1;
  ctx.strokeStyle = shape.color;
  ctx.fillStyle = shape.color;
  ctx.lineWidth = selected ? 5 : 3;

  if (shape.type === "rect") {
    ctx.strokeRect(shape.x, shape.y, shape.width, shape.height);
  }
  if (shape.type === "circle") {
    ctx.beginPath();
    ctx.arc(shape.x, shape.y, shape.radius, 0, Math.PI * 2);
    ctx.fill();
  }
  if (shape.type === "line") {
    ctx.beginPath();
    ctx.moveTo(shape.x, shape.y);
    ctx.lineTo(shape.x2, shape.y2);
    ctx.stroke();
  }

  ctx.restore();
}
