import { useCallback, useEffect, useRef, useState } from "react";
import { listProblems } from "../services/codingService";

const DEFAULT_PAGE_SIZE = 20;
const SEARCH_DEBOUNCE_MS = 250;

export const useProblemList = (initialFilters = {}, initialCachedList = null) => {
  const [search, setSearchState] = useState(initialFilters.search ?? "");
  const [category, setCategoryState] = useState(initialFilters.category ?? "");
  const [difficulty, setDifficultyState] = useState(initialFilters.difficulty ?? "");
  const [language, setLanguageState] = useState(initialFilters.language ?? "");

  const [page, setPageState] = useState(initialFilters.page ?? 1);
  const [limit] = useState(DEFAULT_PAGE_SIZE);
  const [debouncedSearch, setDebouncedSearch] = useState(search);

  const [problems, setProblems] = useState(initialCachedList?.problems ?? []);
  const [total, setTotal] = useState(initialCachedList?.total ?? 0);

  const [isLoading, setIsLoading] = useState(!Boolean(initialCachedList));
  const [error, setError] = useState(null);

  const controllerRef = useRef(null);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedSearch(search);
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    setSearchState(initialFilters.search ?? "");
    setCategoryState(initialFilters.category ?? "");
    setDifficultyState(initialFilters.difficulty ?? "");
    setLanguageState(initialFilters.language ?? "");
    setPageState(initialFilters.page ?? 1);
  }, [initialFilters.search, initialFilters.category, initialFilters.difficulty, initialFilters.language, initialFilters.page]);

  const setPage = useCallback((value) => {
    const nextPage = Number(value) || 1;
    setPageState(Math.max(1, nextPage));
  }, []);

  const fetchProblems = useCallback(async () => {
    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    controllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);

    try {
      const data = await listProblems(
        {
          page,
          limit,
          search: debouncedSearch,
          category,
          difficulty,
          language,
        },
        controllerRef.current.signal
      );

      setProblems(data.problems ?? []);
      setTotal(data.total ?? 0);
    } catch (err) {
      if (err.name !== "CanceledError" && err.name !== "AbortError") {
        setError(
          err.response?.data?.message || "Failed to load coding problems."
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, debouncedSearch, category, difficulty, language]);

  const shouldSkipInitialFetch = useRef(
    Boolean(
      initialCachedList &&
        initialFilters.page === page &&
        initialFilters.search === search &&
        initialFilters.category === category &&
        initialFilters.difficulty === difficulty &&
        initialFilters.language === language
    )
  );

  useEffect(() => {
    if (shouldSkipInitialFetch.current) {
      shouldSkipInitialFetch.current = false
      return () => {
        controllerRef.current?.abort()
      }
    }

    fetchProblems()

    return () => {
      controllerRef.current?.abort();
    };
  }, [fetchProblems]);

  const setSearch = (value) => {
    setPage(1);
    setSearchState(value);
  };

  const setCategory = (value) => {
    setPage(1);
    setCategoryState(value);
  };

  const setDifficulty = (value) => {
    setPage(1);
    setDifficultyState(value);
  };

  const setLanguage = (value) => {
    setPage(1);
    setLanguageState(value);
  };

  const totalPages = Math.max(Math.ceil(total / limit), 1);

  return {
    problems,
    total,

    page,
    limit,
    totalPages,

    search,
    category,
    difficulty,
    language,

    isLoading,
    error,

    setPage,
    setSearch,
    setCategory,
    setDifficulty,
    setLanguage,

    fetchProblems,
  };
};