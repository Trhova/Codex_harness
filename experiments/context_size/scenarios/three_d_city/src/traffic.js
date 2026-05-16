import * as THREE from "three";


export function createTraffic(scene) {
  const cars = [];
  const material = new THREE.MeshStandardMaterial({ color: "#d64242" });
  for (let index = 0; index < 8; index += 1) {
    const car = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.35, 0.45), material);
    car.userData.offset = index * 0.8;
    scene.add(car);
    cars.push(car);
  }
  return {
    update(seconds) {
      for (const car of cars) {
        const loop = (seconds + car.userData.offset) % 8;
        car.position.set(loop * 2 - 8, 0.25, Math.sin(loop) * 6);
      }
    },
  };
}
