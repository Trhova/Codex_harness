import { createCityScene } from "./scene.js";
import { createTraffic } from "./traffic.js";
import { attachControls } from "./controls.js";

const canvas = document.querySelector("#city");
const city = createCityScene(canvas);
const traffic = createTraffic(city.scene);

attachControls(city.camera, city.renderer.domElement);

function render(time) {
  traffic.update(time / 1000);
  city.renderer.render(city.scene, city.camera);
  requestAnimationFrame(render);
}

requestAnimationFrame(render);
