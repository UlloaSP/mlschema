const paths = {
  menu: '<path d="M5 6h14M5 12h14M5 18h14"/>',
  run: '<path d="m8 5 11 7-11 7z"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="1"/>',
  reset: '<path d="M3 10a9 9 0 1 1 2 8M3 4v6h6"/>',
  restart: '<path d="M20 7a9 9 0 0 0-15-2L2 8m0-6v6h6m-4 9a9 9 0 0 0 15 2l3-3m0 6v-6h-6"/>',
  copy: '<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  error: '<circle cx="12" cy="12" r="9"/><path d="M12 7v6m0 4h.01"/>',
  loading: '<path d="M21 12a9 9 0 1 1-9-9"/>',
  ready: '<circle cx="12" cy="12" r="7"/>',
  docs: '<path d="M12 5c-3-2-7-2-10-1v15c3-1 7-1 10 1 3-2 7-2 10-1V4c-3-1-7-1-10 1v15"/>',
  github: '<path d="M9 19c-4 1-4-2-6-2m12 5v-4a3 3 0 0 0-1-2c4-.5 6-2 6-6a5 5 0 0 0-1-3c.3-1 .3-2 0-3-2 0-3 1-4 1a13 13 0 0 0-6 0C8 5 7 4 5 4c-.3 1-.3 2 0 3a5 5 0 0 0-1 3c0 4 2 5.5 6 6a3 3 0 0 0-1 2v4"/>',
} as const;

export type Icon = keyof typeof paths;
export const icon = (name: Icon) =>
  `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]}</svg>`;

/** Icon-only control: the label is its accessible name and its hover/focus tooltip. */
export const labelIcon = (element: HTMLElement, name: Icon, label: string, tooltip = label) => {
  element.innerHTML = icon(name);
  element.setAttribute("aria-label", label);
  element.dataset.tooltip = tooltip;
};
