import { clampRatio, type CodePosition } from "./state.ts";

export const bindCodeSplit = (
  split: HTMLElement,
  separator: HTMLElement,
  initialPosition: CodePosition,
  initialRatio: number,
  onChange: (position: CodePosition, ratio: number) => void,
) => {
  let position = initialPosition;
  let ratio = initialRatio;
  let pointer: number | null = null;
  const horizontal = () => position === "left" || position === "right";
  const reversed = () => position === "right" || position === "bottom";
  const update = () => {
    ratio = clampRatio(ratio);
    split.dataset.position = position;
    split.style.setProperty("--code-share", `${ratio}fr`);
    split.style.setProperty("--output-share", `${100 - ratio}fr`);
    separator.setAttribute("aria-orientation", horizontal() ? "vertical" : "horizontal");
    separator.setAttribute("aria-valuenow", String(Math.round(ratio)));
    separator.setAttribute("aria-valuetext", `Code: ${Math.round(ratio)} %`);
  };
  const move = (event: PointerEvent) => {
    if (pointer !== event.pointerId) return;
    const bounds = split.getBoundingClientRect();
    const offset = horizontal() ? event.clientX - bounds.left : event.clientY - bounds.top;
    const size = horizontal() ? bounds.width : bounds.height;
    const divider = horizontal() ? separator.offsetWidth : separator.offsetHeight;
    ratio = ((offset - divider / 2) / Math.max(1, size - divider)) * 100;
    if (reversed()) ratio = 100 - ratio;
    update();
  };
  const end = () => {
    if (pointer === null) return;
    pointer = null;
    split.classList.remove("is-resizing");
    onChange(position, ratio);
  };
  const start = (event: PointerEvent) => {
    if (event.button !== 0) return;
    event.preventDefault();
    pointer = event.pointerId;
    separator.focus();
    separator.setPointerCapture(pointer);
    split.classList.add("is-resizing");
  };
  const keydown = (event: KeyboardEvent) => {
    const less = horizontal() ? "ArrowLeft" : "ArrowUp";
    const more = horizontal() ? "ArrowRight" : "ArrowDown";
    if (![less, more, "Home", "End", "Enter"].includes(event.key)) return;
    event.preventDefault();
    if (event.key === "Home") ratio = 20;
    else if (event.key === "End") ratio = 80;
    else if (event.key === "Enter") ratio = 50;
    else ratio += (event.key === more ? 1 : -1) * (reversed() ? -1 : 1) * (event.shiftKey ? 10 : 2);
    update();
    onChange(position, ratio);
  };
  const reset = () => {
    ratio = 50;
    update();
    onChange(position, ratio);
  };
  separator.addEventListener("pointerdown", start);
  separator.addEventListener("pointermove", move);
  separator.addEventListener("pointerup", end);
  separator.addEventListener("pointercancel", end);
  separator.addEventListener("lostpointercapture", end);
  separator.addEventListener("keydown", keydown);
  separator.addEventListener("dblclick", reset);
  update();
  return {
    setPosition(next: CodePosition, nextRatio = ratio) {
      position = next;
      ratio = nextRatio;
      update();
      onChange(position, ratio);
    },
    destroy() {
      separator.removeEventListener("pointerdown", start);
      separator.removeEventListener("pointermove", move);
      separator.removeEventListener("pointerup", end);
      separator.removeEventListener("pointercancel", end);
      separator.removeEventListener("lostpointercapture", end);
      separator.removeEventListener("keydown", keydown);
      separator.removeEventListener("dblclick", reset);
    },
  };
};
