export interface RuntimeVersions {
  python: string;
  pandas: string;
  pydantic: string;
  numpy: string;
}

/** What the last expression of a run produced, as reported by harness.py. */
export type RunOutcome =
  | { kind: "json"; text: string }
  | { kind: "repr"; text: string; typeName: string }
  | { kind: "none" }
  | { kind: "error"; text: string };

export type OutputStream = "stdout" | "stderr";

export type ToWorker = { type: "run"; id: number; code: string };

export type FromWorker =
  | { type: "progress"; message: string }
  | { type: "ready"; versions: RuntimeVersions }
  | { type: "boot-error"; message: string }
  | { type: "stream"; id: number; stream: OutputStream; text: string }
  | { type: "done"; id: number; outcome: RunOutcome; durationMs: number };
