const tools = [
  { id: "select", label: "Select" },
  { id: "pen", label: "Pen" },
  { id: "note", label: "Note" },
];

export function createToolRail(host, state, onChange) {
  host.innerHTML = "";
  tools.forEach((tool) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = tool.label;
    button.className = state.tool === tool.id ? "active" : "";
    button.addEventListener("click", () => {
      state.tool = tool.id;
      createToolRail(host, state, onChange);
      onChange();
    });
    host.append(button);
  });
}
