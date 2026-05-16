import * as THREE from "three";


export function createCityScene(canvas) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#87b6d8");

  const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(18, 16, 24);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  addLights(scene);
  addGround(scene);
  addBuildings(scene);
  return { scene, camera, renderer };
}


function addLights(scene) {
  const sun = new THREE.DirectionalLight("#ffffff", 2.5);
  sun.position.set(10, 20, 8);
  scene.add(sun);
  scene.add(new THREE.AmbientLight("#d8ecff", 0.8));
}


function addGround(scene) {
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(60, 60),
    new THREE.MeshStandardMaterial({ color: "#5d8a66" }),
  );
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);
}


function addBuildings(scene) {
  const material = new THREE.MeshStandardMaterial({ color: "#c6ccd2", roughness: 0.7 });
  for (let x = -4; x <= 4; x += 2) {
    for (let z = -4; z <= 4; z += 2) {
      const height = 1.5 + ((x * x + z * z) % 5);
      const building = new THREE.Mesh(new THREE.BoxGeometry(1.1, height, 1.1), material);
      building.position.set(x * 2, height / 2, z * 2);
      scene.add(building);
    }
  }
}
