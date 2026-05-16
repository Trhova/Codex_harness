export function createCameraControls(host, cameraRig) {
  host.innerHTML = "";
  host.append(
    makeButton("West", () => {
      cameraRig.angle -= 0.35;
    }),
    makeButton("East", () => {
      cameraRig.angle += 0.35;
    }),
    makeButton("Lower", () => {
      cameraRig.height = Math.max(12, cameraRig.height - 3);
    }),
    makeButton("Raise", () => {
      cameraRig.height = Math.min(42, cameraRig.height + 3);
    })
  );
}

function makeButton(label, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}
