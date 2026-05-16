export function renderPreview(canvas, material) {
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const centerX = width * 0.5;
  const centerY = height * 0.52;
  const radius = Math.min(width, height) * 0.24;

  ctx.clearRect(0, 0, width, height);
  const background = ctx.createLinearGradient(0, 0, width, height);
  background.addColorStop(0, "#111923");
  background.addColorStop(1, "#222b35");
  ctx.fillStyle = background;
  ctx.fillRect(0, 0, width, height);

  const productGradient = ctx.createRadialGradient(centerX - radius * 0.4, centerY - radius * 0.5, 8, centerX, centerY, radius);
  productGradient.addColorStop(0, material.accentColor);
  productGradient.addColorStop(material.roughness, material.baseColor);
  productGradient.addColorStop(1, "#12161b");

  ctx.fillStyle = productGradient;
  ctx.beginPath();
  ctx.ellipse(centerX, centerY, radius * 1.35, radius, -0.18, 0, Math.PI * 2);
  ctx.fill();

  if (material.environmentShimmer) {
    ctx.strokeStyle = `rgba(255, 255, 255, ${0.18 + material.clearcoat * 0.35})`;
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.arc(centerX - radius * 0.34, centerY - radius * 0.28, radius * 0.52, 3.8, 5.5);
    ctx.stroke();
  }
}
