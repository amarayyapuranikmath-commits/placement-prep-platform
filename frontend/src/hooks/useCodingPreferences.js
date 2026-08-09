import { useCallback, useEffect, useState } from "react";
import {
  getCodingPreferences,
  updateCodingPreferences,
} from "../services/codingService";

export const useCodingPreferences = () => {
  const [preferredLanguage, setPreferredLanguage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  const fetchPreferences = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getCodingPreferences();
      setPreferredLanguage(data.preferred_language ?? null);
    } catch (err) {
      // If the backend returns 404, it means the user hasn't selected a language yet.
      if (err.response?.status !== 404) {
        setError(
          err.response?.data?.message ||
            "Failed to load language preference."
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  const savePreferredLanguage = useCallback(async (language) => {
    setIsSaving(true);
    setError(null);

    try {
      const data = await updateCodingPreferences(language);

      setPreferredLanguage(data.preferred_language);

      return data.preferred_language;
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "Failed to save language preference."
      );

      throw err;
    } finally {
      setIsSaving(false);
    }
  }, []);

  return {
    preferredLanguage,

    isLoading,
    isSaving,

    error,

    fetchPreferences,

    savePreferredLanguage,

    needsLanguageSelection:
      !isLoading && preferredLanguage === null,
  };
};