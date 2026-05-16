export const telemetrySnapshot = {
  networkLoad: 76,
  incidents: 3,
  districts: [
    {
      name: "North Financial",
      kind: "financial",
      blocks: [
        { x: -12, z: -9, width: 3, depth: 4, height: 14 },
        { x: -8, z: -14, width: 4, depth: 3, height: 19 },
        { x: -4, z: -8, width: 3, depth: 5, height: 10 },
      ],
    },
    {
      name: "Harbor Edge",
      kind: "harbor",
      blocks: [
        { x: 8, z: 11, width: 5, depth: 3, height: 6 },
        { x: 14, z: 8, width: 4, depth: 4, height: 8 },
        { x: 18, z: 14, width: 3, depth: 5, height: 5 },
      ],
    },
    {
      name: "Civic Spine",
      kind: "civic",
      blocks: [
        { x: 2, z: -2, width: 6, depth: 4, height: 7 },
        { x: 7, z: -5, width: 3, depth: 3, height: 12 },
      ],
    },
    {
      name: "Campus Quarter",
      kind: "campus",
      blocks: [
        { x: -16, z: 13, width: 4, depth: 4, height: 9 },
        { x: -10, z: 15, width: 5, depth: 2, height: 7 },
      ],
    },
  ],
  routes: [
    {
      id: "H1",
      name: "Harbor loop",
      color: 0x54d7b7,
      load: 86,
      criticalLoadThreshold: 82,
      delayMinutes: 4,
      headway: 5,
      speed: 1.4,
      vehicles: [
        { x: -16, z: 0, heading: 0.12 },
        { x: 4, z: 5, heading: 1.6 },
      ],
    },
    {
      id: "C4",
      name: "Civic express",
      color: 0xffd166,
      load: 64,
      criticalLoadThreshold: 82,
      delayMinutes: 2,
      headway: 4,
      speed: 1.8,
      vehicles: [{ x: 10, z: -7, heading: 3.1 }],
    },
    {
      id: "N7",
      name: "North connector",
      color: 0x8bb7ff,
      load: 78,
      criticalLoadThreshold: 82,
      delayMinutes: 8,
      headway: 6,
      speed: 1.2,
      vehicles: [{ x: -8, z: -18, heading: 0.9 }],
    },
  ],
};
