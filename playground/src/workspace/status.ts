import { icon, type Icon } from "../icons.ts";

export const createStatus = (element: HTMLElement) => {
  let label = "";
  return {
    get label() { return label; },
    show(text: string, symbol: Icon = "ready") {
      label = text;
      element.innerHTML = `${icon(symbol)}<span class="visually-hidden"></span>`;
      element.querySelector("span")!.textContent = text;
      element.dataset.tooltip = text;
      element.dataset.symbol = symbol;
    },
  };
};
