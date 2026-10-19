export type CodePosition = "left" | "right" | "top" | "bottom";
export interface WorkspaceState {
  code: string;
  exampleId: string;
  position: CodePosition;
  ratio: number;
}

const STORAGE_KEY = "mlschema-playground-workspace";
export const isCodePosition = (value: unknown): value is CodePosition =>
  value === "left" || value === "right" || value === "top" || value === "bottom";

export const clampRatio = (ratio: number) => Math.max(20, Math.min(80, ratio));

export const readWorkspaceState = (
  storage: Pick<Storage, "getItem"> | undefined,
  fallback: WorkspaceState,
): WorkspaceState => {
  try {
    const saved: unknown = JSON.parse(storage?.getItem(STORAGE_KEY) ?? "null");
    if (!saved || typeof saved !== "object") return fallback;
    return {
      code: "code" in saved && typeof saved.code === "string" ? saved.code : fallback.code,
      exampleId:
        "exampleId" in saved && typeof saved.exampleId === "string"
          ? saved.exampleId
          : fallback.exampleId,
      position:
        "position" in saved && isCodePosition(saved.position) ? saved.position : fallback.position,
      ratio:
        "ratio" in saved && typeof saved.ratio === "number" && Number.isFinite(saved.ratio)
          ? clampRatio(saved.ratio)
          : fallback.ratio,
    };
  } catch {
    return fallback;
  }
};

export const saveWorkspaceState = (
  storage: Pick<Storage, "setItem"> | undefined,
  state: WorkspaceState,
): boolean => {
  try {
    storage?.setItem(STORAGE_KEY, JSON.stringify(state));
    return storage !== undefined;
  } catch {
    return false;
  }
};
