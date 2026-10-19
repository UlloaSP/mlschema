// Mounts the real MLform kit on the hero's field list and mirrors the values it would send.
// Both packages load on demand, so the rest of the page never waits for them.
export const mountLiveForm = async (host: HTMLElement, output: HTMLElement): Promise<void> => {
  const fields = JSON.parse(host.dataset.fields!);
  const row = JSON.parse(host.dataset.row!) as Record<string, unknown>;
  try {
    const [{ mountForm }, { createSubmissionSnapshot }] = await Promise.all([
      import("mlform"),
      import("mlform/runtime"),
    ]);
    host.replaceChildren();
    const { form } = mountForm(host, {
      schema: { fields },
      // There is no model behind this demo: submitting validates and stops in the browser.
      transport: { submit: async () => ({}) },
      designSystem: { mode: "auto", theme: "eshkra", recipe: "minimal" },
      reportPane: "hidden",
      labels: { submit: "Validate" },
    });
    for (const [target, value] of Object.entries(row)) {
      form.getFieldByMappedTo(target)?.setValue(value);
    }
    const show = () => {
      output.textContent = JSON.stringify(createSubmissionSnapshot(form).modelValues, null, 2);
    };
    show();
    form.subscribe(show);
  } catch (error) {
    console.error(error);
    const status = document.createElement("p");
    status.className = "live-status";
    status.textContent = "MLform could not load here. The fields are in the example above.";
    host.replaceChildren(status);
  }
};
