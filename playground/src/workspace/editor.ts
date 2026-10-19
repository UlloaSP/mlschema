import { defaultKeymap, history, historyKeymap, indentWithTab, isolateHistory } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { bracketMatching, indentOnInput, indentUnit } from "@codemirror/language";
import { EditorState } from "@codemirror/state";
import { EditorView, highlightActiveLine, keymap, lineNumbers } from "@codemirror/view";
import { codeHighlighting } from "./highlight.ts";

export const createCodeEditor = (
  parent: HTMLElement,
  code: string,
  onChange: (value: string) => void,
  onRun: () => void,
) => {
  const editor = new EditorView({
    parent,
    state: EditorState.create({
      doc: code,
      extensions: [
        lineNumbers(),
        history(),
        highlightActiveLine(),
        indentOnInput(),
        indentUnit.of("    "),
        bracketMatching(),
        python(),
        codeHighlighting,
        // Escape then Tab leaves the editor, so indenting with Tab does not trap focus.
        keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab]),
        EditorView.contentAttributes.of({
          "aria-label": "Python code",
          spellcheck: "false",
          autocorrect: "off",
          autocapitalize: "off",
        }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) onChange(update.state.doc.toString());
        }),
      ],
    }),
  });
  const runShortcut = (event: KeyboardEvent) => {
    if (event.key !== "Enter" || !(event.ctrlKey || event.metaKey) || event.altKey) return;
    if (event.isComposing) return;
    // Handle this app command before CodeMirror's Android Enter synthesis drops modifiers.
    event.preventDefault();
    event.stopPropagation();
    onRun();
  };
  editor.contentDOM.addEventListener("keydown", runShortcut, true);
  return {
    setCode(value: string) {
      editor.dispatch({
        ...(value !== editor.state.doc.toString()
          ? {
              changes: { from: 0, to: editor.state.doc.length, insert: value },
              annotations: isolateHistory.of("full"),
            }
          : {}),
        selection: { anchor: 0 },
        effects: EditorView.scrollIntoView(0, { y: "start" }),
      });
    },
    focus: () => editor.focus(),
    destroy() {
      editor.contentDOM.removeEventListener("keydown", runShortcut, true);
      editor.destroy();
    },
  };
};
