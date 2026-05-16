export function renderPresetButtons(host, presets, selectedPreset, onSelect) {
  host.innerHTML = "";
  presets.forEach((preset) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = preset.id === selectedPreset ? "preset active" : "preset";
    button.textContent = preset.label;
    button.addEventListener("click", () => onSelect(preset.id));
    host.append(button);
  });
}

export function bindMaterialForm(form, material, onChange) {
  form.elements.roughness.value = material.roughness;
  form.elements.clearcoat.value = material.clearcoat;
  form.elements.environmentShimmer.checked = material.environmentShimmer;

  form.oninput = () => {
    onChange({
      roughness: Number(form.elements.roughness.value),
      clearcoat: Number(form.elements.clearcoat.value),
      environmentShimmer: form.elements.environmentShimmer.checked,
    });
  };
}
