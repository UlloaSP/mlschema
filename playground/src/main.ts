import "@fontsource-variable/mona-sans/standard.css";
import "@fontsource-variable/jetbrains-mono/wght.css";
import "./styles/index.css";
import mark from "../../brand/mlschema.png?url";
import { bindMenu } from "./menu.ts";
import { applyDesign, browserStorage, readSettings, saveSettings } from "./settings.ts";
import { createShell } from "./shell.ts";
import { mountViewport } from "./viewport.ts";
import { mountWorkspace } from "./workspace/mount.ts";

document.querySelector<HTMLLinkElement>('link[rel="icon"]')!.href = mark;
const storage = browserStorage();
const settings = readSettings(storage);
applyDesign(document.documentElement, settings);
const root = document.querySelector<HTMLElement>("#root")!;
if (new URLSearchParams(location.search).has("editor")) {
  // The editor frame: the page around it owns the header, the menu and the settings.
  root.className = "editor-page";
  mountWorkspace(root, storage);
} else {
  const shell = createShell(mark);
  root.replaceWith(shell);
  const updateViewport = mountViewport(shell.querySelector<HTMLElement>(".app-stage")!, settings);
  bindMenu(shell, settings, (next) => {
    applyDesign(document.documentElement, next);
    updateViewport(next);
    // Unavailable storage keeps the choice for this visit only.
    saveSettings(storage, next);
  });
}
