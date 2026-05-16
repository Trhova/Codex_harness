export const boardLayers = [
  {
    id: "wireframes",
    label: "Wireframes",
    locked: false,
    role: "sketch",
    shapes: [
      { id: "hero-frame", type: "rect", x: 92, y: 74, width: 380, height: 210, color: "#6a7cff" },
      { id: "cta-pill", type: "rect", x: 130, y: 238, width: 148, height: 34, color: "#22a699" },
    ],
  },
  {
    id: "flows",
    label: "User flows",
    locked: false,
    role: "sketch",
    shapes: [
      { id: "flow-line", type: "line", x: 520, y: 180, x2: 760, y2: 280, color: "#ef7b45" },
      { id: "decision-node", type: "circle", x: 804, y: 302, radius: 42, color: "#ef7b45" },
    ],
  },
  {
    id: "review-comments",
    label: "Review comments",
    locked: false,
    role: "comment",
    shapes: [
      { id: "comment-pin-a", type: "circle", x: 430, y: 92, radius: 16, color: "#f7c948" },
      { id: "comment-pin-b", type: "circle", x: 830, y: 330, radius: 16, color: "#f7c948" },
    ],
  },
];

export const boardComments = [
  { id: "a", author: "Mira", text: "Hero frame needs a denser information state.", shapeId: "comment-pin-a" },
  { id: "b", author: "Jon", text: "Decision node should link back to onboarding.", shapeId: "comment-pin-b" },
];
