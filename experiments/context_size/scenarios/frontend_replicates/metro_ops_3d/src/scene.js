import * as THREE from "https://cdn.skypack.dev/three@0.159.0";

const districtColors = {
  financial: 0x8bb7ff,
  harbor: 0x54d7b7,
  civic: 0xffd166,
  campus: 0xc89bff,
};

export function buildMetroScene(canvas, telemetry) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x10151f);
  scene.fog = new THREE.Fog(0x10151f, 32, 88);

  const camera = new THREE.PerspectiveCamera(48, canvas.clientWidth / canvas.clientHeight, 0.1, 200);
  const cameraRig = { camera, radius: 38, angle: -0.7, height: 24 };
  positionCamera(cameraRig);

  scene.add(new THREE.HemisphereLight(0xc8dcff, 0x17202c, 1.8));
  const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
  keyLight.position.set(18, 36, 12);
  scene.add(keyLight);

  const grid = new THREE.GridHelper(72, 24, 0x33506e, 0x223244);
  scene.add(grid);

  addDistrictBlocks(scene, telemetry.districts);
  const vehicleMeshes = addTransitVehicles(scene, telemetry.routes);

  window.addEventListener("resize", () => {
    renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
  });

  return {
    cameraRig,
    vehicleMeshes,
    render() {
      positionCamera(cameraRig);
      renderer.render(scene, camera);
    },
  };
}

function addDistrictBlocks(scene, districts) {
  districts.forEach((district, index) => {
    const material = new THREE.MeshStandardMaterial({
      color: districtColors[district.kind],
      metalness: 0.25,
      roughness: 0.48,
    });

    district.blocks.forEach((block) => {
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(block.width, block.height, block.depth), material);
      mesh.position.set(block.x, block.height / 2, block.z);
      mesh.userData = { district: district.name, index };
      scene.add(mesh);
    });
  });
}

function addTransitVehicles(scene, routes) {
  const meshes = [];
  routes.forEach((route, routeIndex) => {
    route.vehicles.forEach((vehicle, vehicleIndex) => {
      const material = new THREE.MeshStandardMaterial({
        color: route.color,
        emissive: route.color,
        emissiveIntensity: 0.25,
      });
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.5, 2.2), material);
      mesh.position.set(vehicle.x, 0.45, vehicle.z);
      mesh.rotation.y = vehicle.heading;
      mesh.userData = { routeId: route.id, routeIndex, vehicleIndex };
      meshes.push(mesh);
      scene.add(mesh);
    });
  });
  return meshes;
}

export function pulseVehicleLights(vehicleMeshes, routes, delta) {
  vehicleMeshes.forEach((mesh) => {
    const route = routes[mesh.userData.routeIndex];
    const loadPulse = route.load > route.criticalLoadThreshold ? 1.25 : 0.55;
    mesh.material.emissiveIntensity = 0.25 + Math.abs(Math.sin(performance.now() * 0.006)) * loadPulse;
    mesh.position.x += Math.cos(mesh.rotation.y) * route.speed * delta;
    mesh.position.z += Math.sin(mesh.rotation.y) * route.speed * delta;
  });
}

function positionCamera(cameraRig) {
  cameraRig.camera.position.set(
    Math.cos(cameraRig.angle) * cameraRig.radius,
    cameraRig.height,
    Math.sin(cameraRig.angle) * cameraRig.radius
  );
  cameraRig.camera.lookAt(0, 0, 0);
}
