import { expect, test, type Page } from "@playwright/test";

const frame = (page: Page) => page.frameLocator('iframe[title="Python editor"]');
const menuButton = (page: Page) => page.getByRole("button", { name: "Playground options" });
const panel = (page: Page) => page.getByRole("dialog", { name: "Playground options" });
const setting = (page: Page, name: string) => page.getByRole("combobox", { name });
const openMenu = async (page: Page) => {
  await menuButton(page).click();
  await expect(panel(page)).toBeVisible();
};
const design = (page: Page, root: "page" | "frame") =>
  (root === "page" ? page.locator("html") : frame(page).locator("html")).evaluate((html) => ({
    theme: html.dataset.theme,
    style: html.dataset.style,
    scheme: getComputedStyle(html).colorScheme,
    background: getComputedStyle(html.ownerDocument.body).backgroundColor,
  }));
const frameSize = (page: Page) =>
  frame(page).locator("html").evaluate((html) => {
    const view = html.ownerDocument.defaultView!;
    return { width: view.innerWidth, height: view.innerHeight };
  });

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});

test("menu offers only Editor and dismisses by keyboard, outside click and the editor", async ({ page }) => {
  await menuButton(page).click();
  await expect(menuButton(page)).toHaveAttribute("aria-expanded", "true");
  const editorOption = page.getByRole("menuitemradio", { name: "Editor" });
  await expect(editorOption).toBeFocused();
  await expect(editorOption).toHaveAttribute("aria-checked", "true");
  await expect(page.getByRole("menuitemradio")).toHaveCount(1);
  await expect(page.getByRole("group", { name: "Code" })).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(panel(page)).toBeHidden();
  await expect(menuButton(page)).toBeFocused();
  await expect(menuButton(page)).toHaveAttribute("aria-expanded", "false");

  await page.keyboard.press("ArrowDown");
  await expect(editorOption).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(panel(page)).toBeHidden();
  await expect(menuButton(page)).toBeFocused();

  await openMenu(page);
  await page.mouse.click(70, 68); // The header, beside the menu button.
  await expect(panel(page)).toBeHidden();

  // The result pane stays uncovered by the panel at both desktop and phone widths.
  await openMenu(page);
  await frame(page).getByRole("textbox", { name: "Schema JSON" }).click();
  await expect(panel(page)).toBeHidden();
});

test("design settings style the page and the editor, and persist", async ({ page }) => {
  await openMenu(page);
  await expect(setting(page, "Design system")).toHaveValue("eshkra");
  await expect(setting(page, "Style")).toHaveValue("default");
  await expect(setting(page, "Appearance")).toHaveValue("auto");
  await expect(setting(page, "Viewport size")).toHaveValue("actual");
  await setting(page, "Design system").selectOption("cobalt");
  await setting(page, "Style").selectOption("contrast");
  await setting(page, "Appearance").selectOption("dark");
  const cobaltDark = { theme: "cobalt", style: "contrast", scheme: "dark", background: "rgb(13, 21, 36)" };
  await expect.poll(() => design(page, "page")).toEqual(cobaltDark);
  await expect.poll(() => design(page, "frame")).toEqual(cobaltDark);
  await expect(page.getByRole("menuitemradio", { name: "Editor" })).toHaveCSS(
    "background-color",
    "rgb(104, 160, 255)",
  );

  await page.reload();
  await expect.poll(() => design(page, "frame")).toEqual(cobaltDark);
  expect(await design(page, "page")).toEqual(cobaltDark);
  await openMenu(page);
  await expect(setting(page, "Design system")).toHaveValue("cobalt");
  await setting(page, "Appearance").selectOption("light");
  await expect.poll(async () => (await design(page, "frame")).background).toBe("rgb(238, 244, 251)");
});

test("viewport sizes resize the editor without restarting Python", async ({ page }) => {
  const ws = frame(page);
  const schema = ws.getByRole("textbox", { name: "Schema JSON" });
  await expect(schema).toContainText('"kind"');
  await ws.getByRole("textbox", { name: "Python code" }).click();
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.insertText("x = 41\n[1, 2, x + 1]\n");
  await ws.getByRole("button", { name: "Run" }).click();
  await expect(schema).toContainText("42");
  // A marker on the frame's window proves the same document survives every change.
  await ws.locator("html").evaluate((html) => ((html.ownerDocument.defaultView as any).marker = 7));

  await openMenu(page);
  await setting(page, "Viewport size").selectOption("phone");
  await expect(page.getByText(/^Phone · 390 × 844 px/)).toBeVisible();
  await expect.poll(() => frameSize(page)).toEqual({ width: 390, height: 844 });
  await expect(page.getByRole("spinbutton", { name: "Width (px)" })).toBeHidden();

  await setting(page, "Viewport size").selectOption("custom");
  const width = page.getByRole("spinbutton", { name: "Width (px)" });
  const height = page.getByRole("spinbutton", { name: "Height (px)" });
  await width.fill("500");
  await width.blur();
  await height.fill("700");
  await height.blur();
  await expect.poll(() => frameSize(page)).toEqual({ width: 500, height: 700 });
  for (const invalid of ["0", "8193", "12.5"]) {
    await width.fill(invalid);
    await width.blur();
    await expect(width).toHaveValue("500");
  }
  await expect.poll(() => frameSize(page)).toEqual({ width: 500, height: 700 });

  expect(await ws.locator("html").evaluate((html) => (html.ownerDocument.defaultView as any).marker)).toBe(7);
  await expect(ws.getByRole("textbox", { name: "Python code" })).toContainText("x + 1");
  await expect(schema).toContainText("42");
  await expect(ws.getByRole("status").filter({ hasText: "Done" })).toBeAttached();

  await page.reload();
  await expect.poll(() => frameSize(page)).toEqual({ width: 500, height: 700 });
  await openMenu(page);
  await expect(setting(page, "Viewport size")).toHaveValue("custom");
  await expect(page.getByRole("spinbutton", { name: "Width (px)" })).toHaveValue("500");
  await setting(page, "Viewport size").selectOption("actual");
  await expect(page.getByText(/× 700 px/)).toBeHidden();
  const stage = await page.locator(".app-stage").evaluate((element) => element.clientWidth);
  await expect.poll(async () => (await frameSize(page)).width).toBe(stage);
});
