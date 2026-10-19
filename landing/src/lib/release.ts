// The latest version on PyPI, fetched once per build. A failed request returns null so an API
// outage never breaks a deploy; the page then leaves the version out instead of guessing it.
let pending: Promise<string | null> | undefined;

export const latestVersion = (): Promise<string | null> =>
  (pending ??= fetch("https://pypi.org/pypi/mlschema/json", { signal: AbortSignal.timeout(7000) })
    .then((response) => (response.ok ? response.json() : null))
    .then((data: { info?: { version?: unknown } } | null) => {
      const version = data?.info?.version;
      return typeof version === "string" ? version : null;
    })
    .catch(() => null));
