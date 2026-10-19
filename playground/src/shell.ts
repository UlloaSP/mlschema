import { icon } from "./icons.ts";
import { LINKS } from "./links.ts";
import { MENU } from "./menu.ts";
import eshkraMark from "../../brand/eshkra-mark.png?url";

export const createShell = (mark: string) => {
  const shell = document.createElement("main");
  shell.className = "app-shell";
  shell.innerHTML = `
    <header class="app-brand-header">
      <a class="mlschema-brand" href="${LINKS.home}" aria-label="MLschema home">
        <img src="${mark}" alt="" width="26" height="40" />
        <span class="mlschema-wordmark" translate="no"><span class="ml">ML</span><span class="rest">schema</span></span>
      </a>
      <nav aria-label="MLschema resources">
        <a class="icon-button" href="${LINKS.docs}" aria-label="Docs" data-tooltip="Docs">${icon("docs")}</a>
        <a class="icon-button" href="${LINKS.github}" aria-label="GitHub" data-tooltip="GitHub">${icon("github")}</a>
        <a class="icon-button" href="${LINKS.eshkra}" aria-label="eshkra" data-tooltip="eshkra">
          <img src="${eshkraMark}" alt="" width="20" height="20" />
        </a>
      </nav>
    </header>
    ${MENU}
    <div class="app-stage"></div>
  `;
  return shell;
};
