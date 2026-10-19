import assert from "node:assert/strict";
import { test } from "node:test";
import {
  APPEARANCES,
  DEFAULT_SETTINGS,
  readSettings,
  saveSettings,
  SETTINGS_KEY,
  STYLES,
  THEMES,
  VIEWPORTS,
  viewportSize,
  type Settings,
} from "../../src/settings.ts";

const memory = (initial?: string) => {
  const items = new Map<string, string>(initial === undefined ? [] : [[SETTINGS_KEY, initial]]);
  return {
    items,
    getItem: (key: string) => items.get(key) ?? null,
    setItem: (key: string, value: string) => void items.set(key, value),
  };
};
const CHOSEN: Settings = {
  theme: "cobalt",
  style: "contrast",
  appearance: "dark",
  viewport: "custom",
  width: 500,
  height: 700,
};

test("catalogs offer MLForm's choices with unique ids", () => {
  assert.deepEqual(
    THEMES.map(({ id }) => id),
    ["eshkra", "m3diseen", "dosetailor", "clickhouse", "airbnb", "neutral", "cobalt", "sage", "sunset", "graphite"],
  );
  assert.deepEqual(STYLES.map(({ label }) => label), ["Default", "Minimal", "Soft", "Contrast"]);
  assert.deepEqual(APPEARANCES.map(({ label }) => label), ["System", "Light", "Dark"]);
  for (const items of [THEMES, STYLES, APPEARANCES, VIEWPORTS]) {
    assert.equal(new Set(items.map(({ id }) => id)).size, items.length);
  }
});

test("saved settings round-trip", () => {
  const storage = memory();
  assert.deepEqual(readSettings(storage), DEFAULT_SETTINGS);
  assert.equal(saveSettings(storage, CHOSEN), true);
  assert.deepEqual(readSettings(storage), CHOSEN);
});

test("each invalid field falls back alone", () => {
  const saved = { ...CHOSEN, theme: "unknown", style: 3, viewport: "watch", width: 0 };
  assert.deepEqual(readSettings(memory(JSON.stringify(saved))), {
    ...CHOSEN,
    theme: DEFAULT_SETTINGS.theme,
    style: DEFAULT_SETTINGS.style,
    viewport: DEFAULT_SETTINGS.viewport,
    width: DEFAULT_SETTINGS.width,
  });
  for (const size of [8193, 1.5, -1, "640", null]) {
    assert.equal(readSettings(memory(JSON.stringify({ height: size }))).height, DEFAULT_SETTINGS.height);
  }
  assert.equal(readSettings(memory(JSON.stringify({ width: 8192 }))).width, 8192);
  assert.equal(readSettings(memory(JSON.stringify({ appearance: "sepia" }))).appearance, "auto");
});

test("unreadable storage yields the defaults", () => {
  for (const raw of ["{not json", "[1, 2]", "42", "null"]) {
    assert.deepEqual(readSettings(memory(raw)), DEFAULT_SETTINGS);
  }
  const blocked = {
    getItem(): string {
      throw new Error("SecurityError");
    },
  };
  assert.deepEqual(readSettings(blocked), DEFAULT_SETTINGS);
  assert.deepEqual(readSettings(undefined), DEFAULT_SETTINGS);
});

test("saving reports unavailable storage", () => {
  const full = {
    setItem() {
      throw new Error("QuotaExceededError");
    },
  };
  assert.equal(saveSettings(full, CHOSEN), false);
  assert.equal(saveSettings(undefined, CHOSEN), false);
});

test("viewport size follows the preset or the custom size", () => {
  assert.equal(viewportSize(DEFAULT_SETTINGS), null);
  assert.deepEqual(viewportSize({ ...CHOSEN, viewport: "phone" }), {
    width: 390,
    height: 844,
    name: "Phone",
  });
  assert.deepEqual(viewportSize({ ...CHOSEN, viewport: "ultrawide" }), {
    width: 2560,
    height: 1080,
    name: "Ultrawide",
  });
  assert.deepEqual(viewportSize(CHOSEN), { width: 500, height: 700, name: "Custom" });
});
