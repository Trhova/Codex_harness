import { buildMetroScene, pulseVehicleLights } from "./scene.js";
import { createCameraControls } from "./controls.js";
import { drawAlertPanel, drawRouteTable } from "./panels.js";
import { telemetrySnapshot } from "./telemetry.js";

const canvas = document.querySelector("#city-canvas");
const summaryPanel = document.querySelector("#summary-panel");
const routePanel = document.querySelector("#route-panel");
const controlsHost = document.querySelector("#camera-controls");

const app = buildMetroScene(canvas, telemetrySnapshot);
createCameraControls(controlsHost, app.cameraRig);
drawAlertPanel(summaryPanel, telemetrySnapshot);
drawRouteTable(routePanel, telemetrySnapshot.routes);

let previousTime = 0;

function frame(time) {
  const delta = Math.min((time - previousTime) / 1000, 0.04);
  previousTime = time;
  pulseVehicleLights(app.vehicleMeshes, telemetrySnapshot.routes, delta);
  app.render();
  requestAnimationFrame(frame);
}

requestAnimationFrame(frame);
