import { useCallback, useEffect, useState } from "react";
import {
  getProblemDetail,
  runSolution,
  submitSolution,
} from "../services/codingService";

export const useProblemWorkspace = (problemId, defaultLanguage) => {
  const [problem, setProblem] = useState(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [language, setLanguage] = useState(defaultLanguage ?? "python");
  const [codeByLanguage, setCodeByLanguage] = useState({});

  const [isRunning, setIsRunning] = useState(false);
  const [runResult, setRunResult] = useState(null);
  const [runError, setRunError] = useState(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  /**
   * Fetch Problem
   */
  const fetchProblem = useCallback(async () => {
    if (!problemId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await getProblemDetail(problemId);

      setProblem(data);

      setCodeByLanguage((previous) => {
        const updated = { ...previous };

        Object.entries(data.starter_code ?? {}).forEach(([lang, starter]) => {
          if (!(lang in updated)) {
            updated[lang] = starter;
          }
        });

        return updated;
      });
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "Failed to load coding problem."
      );
    } finally {
      setIsLoading(false);
    }
  }, [problemId]);

  useEffect(() => {
    fetchProblem();
  }, [fetchProblem]);

  useEffect(() => {
    if (defaultLanguage) {
      setLanguage(defaultLanguage);
    }
  }, [defaultLanguage]);

  const code =
    codeByLanguage[language] ??
    problem?.starter_code?.[language] ??
    "";

  const setCode = (value) => {
    setCodeByLanguage((previous) => ({
      ...previous,
      [language]: value,
    }));
  };

  const resetCode = () => {
    if (!problem) return;

    setCodeByLanguage((previous) => ({
      ...previous,
      [language]: problem.starter_code?.[language] ?? "",
    }));
  };

  const changeLanguage = (nextLanguage) => {
    if (nextLanguage === language) return;

    setLanguage(nextLanguage);

    setRunResult(null);
    setRunError(null);

    setSubmitResult(null);
    setSubmitError(null);
  };

  /**
   * Run Solution
   */
  const handleRun = useCallback(async () => {
    setIsRunning(true);

    setRunResult(null);
    setRunError(null);

    try {
      const result = await runSolution(
        problemId,
        language,
        code
      );

      setRunResult(result);

      return result;
    } catch (err) {
      setRunError(
        err.response?.data?.message ||
          "Failed to run solution."
      );

      throw err;
    } finally {
      setIsRunning(false);
    }
  }, [problemId, language, code]);

  /**
   * Submit Solution
   */
  const handleSubmit = useCallback(async () => {
    setIsSubmitting(true);

    setSubmitResult(null);
    setSubmitError(null);

    try {
      const result = await submitSolution(
        problemId,
        language,
        code
      );

      setSubmitResult(result);

      if (result.status === "accepted") {
        setProblem((previous) =>
          previous
            ? {
                ...previous,
                is_solved: true,
              }
            : previous
        );
      }

      return result;
    } catch (err) {
      setSubmitError(
        err.response?.data?.message ||
          "Failed to submit solution."
      );

      throw err;
    } finally {
      setIsSubmitting(false);
    }
  }, [problemId, language, code]);

  return {
    problem,

    isLoading,
    error,

    language,
    changeLanguage,

    code,
    setCode,
    resetCode,

    isRunning,
    runResult,
    runError,

    isSubmitting,
    submitResult,
    submitError,

    handleRun,
    handleSubmit,

    fetchProblem,
  };
};