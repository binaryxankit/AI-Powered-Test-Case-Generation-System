"use client";

import * as React from "react";

/**
 * Returns a value that lags behind ``value`` by ``delay`` ms.
 *
 * Useful for deferring expensive work (network calls, validation) until
 * the user stops typing.
 */
export function useDebounce<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = React.useState<T>(value);

  React.useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delay);
    return () => window.clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
