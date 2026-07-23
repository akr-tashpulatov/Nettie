import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { useDebounce } from "./use-debounce";

export function useDebouncedSearch(initialValue: string = '', onSearch: (value: string) => void) {
  const [value, setValue] = useState(initialValue);
  const debounced = useDebounce(value);
  const onSearchRef = useRef(onSearch);

  useLayoutEffect(() => {
    onSearchRef.current = onSearch;
  });

  useEffect(() => {
    onSearchRef.current(debounced);
  }, [debounced]);

  return {
    value,
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setValue(e.target.value),
  };
}
