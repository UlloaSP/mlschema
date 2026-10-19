// Sidebar order follows the reader's path: start, understand the contract, customize, look up.
export const sidebar = [
  {
    label: "Start",
    items: [
      { label: "Overview", slug: "" },
      { label: "Installation", slug: "getting-started/installation" },
      { label: "Quick start", slug: "getting-started/quick-start" },
    ],
  },
  {
    label: "Schema",
    items: [
      { label: "Field contract", slug: "schema/overview" },
      { label: "Field kinds", slug: "schema/field-kinds" },
      { label: "Series", slug: "schema/series" },
      { label: "Mappings", slug: "schema/mappings" },
    ],
  },
  {
    label: "Customize",
    items: [
      { label: "Overrides", slug: "guides/overrides" },
      { label: "Builders and custom kinds", slug: "guides/extensions" },
      { label: "Errors", slug: "guides/errors" },
      { label: "Use with MLForm", slug: "guides/mlform" },
    ],
  },
  {
    label: "Reference",
    items: [
      { label: "Python API", slug: "reference/api" },
      { label: "Releases", slug: "reference/releases" },
      { label: "Changelog", slug: "changelog" },
      { label: "0.1 history", slug: "changelog/0-1" },
    ],
  },
];
