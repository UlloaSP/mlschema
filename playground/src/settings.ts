/** Options-menu settings. The catalogs mirror MLForm's playground (themes, recipes, viewports). */
export const THEMES = [
  { id: "eshkra", label: "eshkra" },
  { id: "m3diseen", label: "M3DISEEN" },
  { id: "dosetailor", label: "DoseTailor" },
  { id: "clickhouse", label: "ClickHouse" },
  { id: "airbnb", label: "Airbnb" },
  { id: "neutral", label: "Neutral" },
  { id: "cobalt", label: "Cobalt" },
  { id: "sage", label: "Sage" },
  { id: "sunset", label: "Sunset" },
  { id: "graphite", label: "Graphite" },
] as const;
export const STYLES = [
  { id: "default", label: "Default" },
  { id: "minimal", label: "Minimal" },
  { id: "soft", label: "Soft" },
  { id: "contrast", label: "Contrast" },
] as const;
export const APPEARANCES = [
  { id: "auto", label: "System" },
  { id: "light", label: "Light" },
  { id: "dark", label: "Dark" },
] as const;
export const VIEWPORTS = [
  { id: "actual", label: "Current viewport" },
  { id: "phone", label: "Phone · 390 × 844", width: 390, height: 844 },
  { id: "tablet", label: "Tablet · 820 × 1180", width: 820, height: 1180 },
  { id: "laptop", label: "Laptop · 1366 × 768", width: 1366, height: 768 },
  { id: "pc", label: "PC · 1920 × 1080", width: 1920, height: 1080 },
  { id: "ultrawide", label: "Ultrawide · 2560 × 1080", width: 2560, height: 1080 },
  { id: "custom", label: "Custom" },
] as const;
export const SIZE_LIMITS = { min: 1, max: 8192 } as const;

type Id<T extends readonly { id: string }[]> = T[number]["id"];
export interface Settings {
  theme: Id<typeof THEMES>;
  style: Id<typeof STYLES>;
  appearance: Id<typeof APPEARANCES>;
  viewport: Id<typeof VIEWPORTS>;
  width: number;
  height: number;
}
export const SETTINGS_KEY = "mlschema-playground-settings";
export const DEFAULT_SETTINGS: Settings = {
  theme: "eshkra",
  style: "default",
  appearance: "auto",
  viewport: "actual",
  width: 1280,
  height: 800,
};

export const validSize = (value: unknown): value is number =>
  typeof value === "number" &&
  Number.isInteger(value) &&
  value >= SIZE_LIMITS.min &&
  value <= SIZE_LIMITS.max;

const pick = <T extends readonly { id: string }[]>(items: T, value: unknown, fallback: Id<T>) =>
  (items.find(({ id }) => id === value)?.id as Id<T> | undefined) ?? fallback;

/** Each saved field is validated on its own, so one bad value never resets the others. */
export const parseSettings = (value: unknown): Settings => {
  const saved = value && typeof value === "object" ? (value as Record<string, unknown>) : {};
  return {
    theme: pick(THEMES, saved.theme, DEFAULT_SETTINGS.theme),
    style: pick(STYLES, saved.style, DEFAULT_SETTINGS.style),
    appearance: pick(APPEARANCES, saved.appearance, DEFAULT_SETTINGS.appearance),
    viewport: pick(VIEWPORTS, saved.viewport, DEFAULT_SETTINGS.viewport),
    width: validSize(saved.width) ? saved.width : DEFAULT_SETTINGS.width,
    height: validSize(saved.height) ? saved.height : DEFAULT_SETTINGS.height,
  };
};

export const readSettings = (storage?: Pick<Storage, "getItem">): Settings => {
  try {
    return parseSettings(JSON.parse(storage?.getItem(SETTINGS_KEY) ?? "null"));
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
};

/** Returns false when the choice cannot be stored; it still applies to this visit. */
export const saveSettings = (storage: Pick<Storage, "setItem"> | undefined, settings: Settings) => {
  try {
    storage?.setItem(SETTINGS_KEY, JSON.stringify(settings));
    return storage !== undefined;
  } catch {
    return false;
  }
};

/** The simulated viewport, or null when the workspace uses the real window. */
export const viewportSize = (settings: Settings) => {
  if (settings.viewport === "actual") return null;
  const preset = VIEWPORTS.find(({ id }) => id === settings.viewport)!;
  const size =
    "width" in preset
      ? { width: preset.width, height: preset.height }
      : { width: settings.width, height: settings.height };
  return { ...size, name: preset.label.split(" · ")[0]! };
};

export const applyDesign = (root: HTMLElement, settings: Settings) => {
  root.dataset.theme = settings.theme;
  root.dataset.style = settings.style;
  root.dataset.appearance = settings.appearance;
};

/** The browser's storage, or undefined where access is blocked (some privacy modes). */
export const browserStorage = () => {
  try {
    return window.localStorage;
  } catch {
    return undefined;
  }
};
