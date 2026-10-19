import { applyDesign, viewportSize, type Settings } from "./settings.ts";

/**
 * The editor always runs in one same-origin frame. Viewport changes only resize or scale
 * that frame, so the code, the output and the running Python survive every change.
 */
export const mountViewport = (stage: HTMLElement, initial: Settings) => {
  let settings = initial;
  stage.innerHTML = `<div class="app-preview">
    <div class="app-preview-label" hidden></div>
    <div class="app-preview-viewport"><iframe class="app-preview-frame" title="Python editor"></iframe></div>
  </div>`;
  const preview = stage.querySelector<HTMLElement>(".app-preview")!;
  const label = stage.querySelector<HTMLElement>(".app-preview-label")!;
  const viewport = stage.querySelector<HTMLElement>(".app-preview-viewport")!;
  const frame = stage.querySelector<HTMLIFrameElement>("iframe")!;
  const syncDesign = () => {
    const root = frame.contentDocument?.documentElement;
    if (root) applyDesign(root, settings);
  };
  const resize = () => {
    const size = viewportSize(settings);
    stage.classList.toggle("is-preview", size !== null);
    label.hidden = size === null;
    if (!size) {
      viewport.removeAttribute("style");
      frame.removeAttribute("style");
      return;
    }
    const { width, height, name } = size;
    // Scale down to fit the stage width, as MLForm's preview does; height may scroll.
    const room = preview.clientWidth - (viewport.offsetWidth - viewport.clientWidth);
    const scale = Math.min(1, Math.max(1, room) / width);
    viewport.style.width = `${width * scale}px`;
    viewport.style.height = `${height * scale}px`;
    frame.style.width = `${width}px`;
    frame.style.height = `${height}px`;
    frame.style.transform = scale < 1 ? `scale(${scale})` : "";
    label.textContent = `${name} · ${width} × ${height} px${scale < 1 ? ` · ${Math.round(scale * 100)} %` : ""}`;
  };
  frame.addEventListener("load", syncDesign);
  const url = new URL(window.location.href);
  url.search = "?editor=1";
  url.hash = "";
  frame.src = url.href;
  new ResizeObserver(resize).observe(stage);
  resize();
  return (next: Settings) => {
    settings = next;
    syncDesign();
    resize();
  };
};
