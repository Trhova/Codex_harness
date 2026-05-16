export function attachControls(camera, element) {
  let dragging = false;
  let lastX = 0;

  element.addEventListener("pointerdown", (event) => {
    dragging = true;
    lastX = event.clientX;
  });

  element.addEventListener("pointerup", () => {
    dragging = false;
  });

  element.addEventListener("pointermove", (event) => {
    if (!dragging) {
      return;
    }
    const delta = event.clientX - lastX;
    lastX = event.clientX;
    const angle = delta * 0.005;
    const nextX = camera.position.x * Math.cos(angle) - camera.position.z * Math.sin(angle);
    const nextZ = camera.position.x * Math.sin(angle) + camera.position.z * Math.cos(angle);
    camera.position.x = nextX;
    camera.position.z = nextZ;
    camera.lookAt(0, 0, 0);
  });
}
