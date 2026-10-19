import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { tags } from "@lezer/highlight";

export const codeHighlighting = syntaxHighlighting(
  HighlightStyle.define([
    { tag: [tags.keyword, tags.controlKeyword], color: "var(--accent)", fontWeight: "600" },
    { tag: [tags.string, tags.number, tags.bool, tags.null], color: "var(--success)" },
    { tag: tags.comment, color: "var(--text-muted)", fontStyle: "italic" },
    { tag: [tags.propertyName, tags.definition(tags.variableName)], color: "var(--info)" },
    { tag: [tags.className, tags.typeName], color: "var(--accent)", fontStyle: "italic" },
  ]),
);
