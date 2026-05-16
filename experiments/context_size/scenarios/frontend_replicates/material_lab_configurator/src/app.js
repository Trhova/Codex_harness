import { materialPresets } from "./presets.js";
import { renderPreview } from "./preview.js";
import { bindMaterialForm, renderPresetButtons } from "./controls.js";

const canvas = document.querySelector("#preview-canvas");
const presetList = document.querySelector("#preset-list");
const form = document.querySelector("#material-form");

const state = {
  selectedPreset: materialPresets[0].id,
  material: { ...materialPresets[0].material },
};

function applyPreset(presetId) {
  const preset = materialPresets.find((item) => item.id === presetId);
  if (!preset) {
    return;
  }
  state.selectedPreset = preset.id;
  state.material = { ...preset.material };
  bindMaterialForm(form, state.material, updateMaterial);
  renderPresetButtons(presetList, materialPresets, state.selectedPreset, applyPreset);
  renderPreview(canvas, state.material);
}

function updateMaterial(patch) {
  state.material = { ...state.material, ...patch };
  renderPreview(canvas, state.material);
}

renderPresetButtons(presetList, materialPresets, state.selectedPreset, applyPreset);
bindMaterialForm(form, state.material, updateMaterial);
renderPreview(canvas, state.material);
