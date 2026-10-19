import { icon } from "./icons.ts";
import {
  APPEARANCES,
  STYLES,
  THEMES,
  VIEWPORTS,
  SIZE_LIMITS,
  validSize,
  type Settings,
} from "./settings.ts";

const options = (items: readonly { id: string; label: string }[]) =>
  items.map(({ id, label }) => `<option value="${id}">${label}</option>`).join("");
const sizeInput = (key: "width" | "height", label: string) =>
  `<label class="app-menu-field">${label}<input data-setting="${key}" type="number"
    min="${SIZE_LIMITS.min}" max="${SIZE_LIMITS.max}" step="1" inputmode="numeric" /></label>`;

/** Floating options menu, following MLForm's playground menu. Editor is the only workspace. */
export const MENU = `
  <div class="app-menu" data-role="menu">
    <button class="app-menu-button" type="button" aria-label="Playground options"
      aria-haspopup="dialog" aria-expanded="false" aria-controls="app-menu-panel"
      data-tooltip="Playground options">${icon("menu")}</button>
    <div class="app-menu-panel" id="app-menu-panel" role="dialog" aria-label="Playground options" hidden>
      <div class="app-menu-list" role="menu" aria-label="Workspace">
        <div class="app-menu-group" role="group" aria-label="Code">
          <div class="app-menu-section-label" aria-hidden="true">Code</div>
          <button class="app-menu-option is-active" type="button" role="menuitemradio"
            aria-checked="true" data-role="editor-option">Editor</button>
        </div>
      </div>
      <div class="app-menu-settings">
        <label class="app-menu-field">Design system<select data-setting="theme">${options(THEMES)}</select></label>
        <label class="app-menu-field">Style<select data-setting="style">${options(STYLES)}</select></label>
        <label class="app-menu-field">Appearance<select data-setting="appearance">${options(APPEARANCES)}</select></label>
        <label class="app-menu-field">Viewport size<select data-setting="viewport">${options(VIEWPORTS)}</select></label>
        <div class="app-menu-custom-size" data-role="custom-size" hidden>
          ${sizeInput("width", "Width (px)")}${sizeInput("height", "Height (px)")}
        </div>
      </div>
    </div>
  </div>`;

export const bindMenu = (
  shell: HTMLElement,
  initial: Settings,
  change: (settings: Settings) => void,
) => {
  let settings = initial;
  const menu = shell.querySelector<HTMLElement>('[data-role="menu"]')!;
  const button = menu.querySelector<HTMLButtonElement>(".app-menu-button")!;
  const panel = menu.querySelector<HTMLElement>(".app-menu-panel")!;
  const editor = menu.querySelector<HTMLButtonElement>('[data-role="editor-option"]')!;
  const custom = menu.querySelector<HTMLElement>('[data-role="custom-size"]')!;
  const fields = [...menu.querySelectorAll<HTMLInputElement | HTMLSelectElement>("[data-setting]")];

  const isOpen = () => menu.classList.contains("is-open");
  const setOpen = (open: boolean, restoreFocus = false) => {
    menu.classList.toggle("is-open", open);
    button.setAttribute("aria-expanded", String(open));
    panel.hidden = !open;
    if (open) editor.focus();
    else if (restoreFocus) button.focus();
  };
  const render = () => {
    for (const field of fields) field.value = String(settings[field.dataset.setting as keyof Settings]);
    custom.hidden = settings.viewport !== "custom";
  };
  const update = (field: HTMLInputElement | HTMLSelectElement) => {
    const key = field.dataset.setting as keyof Settings;
    const value = key === "width" || key === "height" ? Number(field.value) : field.value;
    // Out-of-range sizes restore the last valid value instead of resizing.
    if (typeof value === "number" && !validSize(value)) return render();
    settings = { ...settings, [key]: value };
    render();
    change(settings);
  };

  for (const field of fields) field.addEventListener("change", () => update(field));
  button.addEventListener("click", () => setOpen(!isOpen()));
  button.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowDown") return;
    event.preventDefault();
    setOpen(true);
  });
  // Editor is already showing: choosing it only closes the menu.
  editor.addEventListener("click", (event) => setOpen(false, event.detail === 0));
  document.addEventListener("click", (event) => {
    if (isOpen() && event.target instanceof Node && !menu.contains(event.target)) setOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && isOpen()) setOpen(false, true);
  });
  menu.addEventListener("focusout", (event) => {
    if (event.relatedTarget instanceof Node && !menu.contains(event.relatedTarget)) setOpen(false);
  });
  // Clicks inside the editor frame never reach this document; the frame takes focus instead.
  window.addEventListener("blur", () => {
    if (document.activeElement instanceof HTMLIFrameElement) setOpen(false);
  });
  render();
};
