"use client";

import * as React from "react";

/**
 * Persist a piece of state to ``localStorage`` and re-hydrate it on
 * mount. Falls back to the supplied default if storage is unavailable
 * (private mode, quota errors, etc.).
 */
export function useLocalStorage<T>(
  key: string,
  defaultValue: T,
  options: { serialize?: (v: T) => string; deserialize?: (raw: string) => T } = {},
): [T, React.Dispatch<React.SetStateAction<T>>, () => void] {
  const serialize = React.useCallback(
    (v: T) => (options.serialize ? options.serialize(v) : JSON.stringify(v)),
    [options.serialize],
  );
  const deserialize = React.useCallback(
    (raw: string): T => (options.deserialize ? options.deserialize(raw) : JSON.parse(raw)),
    [options.deserialize],
  );

  const [value, setValue] = React.useState<T>(defaultValue);
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(key);
      if (raw !== null) setValue(deserialize(raw));
    } catch {
      // Ignore storage errors; keep default.
    } finally {
      setHydrated(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  React.useEffect(() => {
    if (!hydrated || typeof window === "undefined") return;
    try {
      window.localStorage.setItem(key, serialize(value));
    } catch {
      // Quota exceeded or storage disabled.
    }
  }, [key, value, serialize, hydrated]);

  const reset = React.useCallback(() => {
    setValue(defaultValue);
    if (typeof window !== "undefined") {
      try {
        window.localStorage.removeItem(key);
      } catch {
        // ignore
      }
    }
  }, [defaultValue, key]);

  return [value, setValue, reset];
}
