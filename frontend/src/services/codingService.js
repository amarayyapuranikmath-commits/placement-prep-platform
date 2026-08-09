import api from "./api";

/**
 * Extracts the actual payload from the standard API response.
 */
const unwrap = (response) => response.data.data ?? response.data;

/**
 * ===============================
 * Coding Preferences
 * ===============================
 */

export const getCodingPreferences = async () => {
  const response = await api.get("/coding/preferences");
  return unwrap(response);
};

export const updateCodingPreferences = async (preferredLanguage) => {
  const response = await api.put("/coding/preferences", {
    preferred_language: preferredLanguage,
  });

  return unwrap(response);
};

/**
 * ===============================
 * Problems
 * ===============================
 */

export const listProblems = async (
  {
    page = 1,
    limit = 20,
    search = "",
    category = "",
    difficulty = "",
    language = "",
    sort = "problem_number",
  } = {},
  signal
) => {
  const response = await api.get("/coding/problems", {
    signal,
    params: {
      page,
      limit,
      search: search || undefined,
      category: category || undefined,
      difficulty: difficulty || undefined,
      language: language || undefined,
      sort,
    },
  });

  return unwrap(response);
};

export const getProblemDetail = async (problemId) => {
  const response = await api.get(`/coding/problems/${problemId}`);
  return unwrap(response);
};

export const getProblemNeighbors = async ({
  problemId,
  search = "",
  category = "",
  difficulty = "",
  language = "",
  sort = "problem_number",
}) => {
  const response = await api.get(`/coding/problems/${problemId}/neighbors`, {
    params: {
      search: search || undefined,
      category: category || undefined,
      difficulty: difficulty || undefined,
      language: language || undefined,
      sort,
    },
  });

  return unwrap(response);
};

let cachedProblemCategories = null;

export const getProblemCategories = async () => {
  if (cachedProblemCategories) {
    return cachedProblemCategories;
  }

  const response = await api.get('/coding/categories');
  const data = unwrap(response);
  cachedProblemCategories = data;
  return data;
};

/**
 * ===============================
 * Code Execution
 * ===============================
 */

export const runSolution = async (problemId, language, code) => {
  const response = await api.post(
    `/coding/problems/${problemId}/run`,
    {
      language,
      code,
    }
  );

  return unwrap(response);
};

export const submitSolution = async (problemId, language, code) => {
  const response = await api.post(
    `/coding/problems/${problemId}/submit`,
    {
      language,
      code,
    }
  );

  return unwrap(response);
};

/**
 * ===============================
 * Submission History
 * ===============================
 */

export const getSubmissionHistory = async (problemId = null) => {
  const response = await api.get("/coding/submissions", {
    params: problemId
      ? {
          problem_id: problemId,
        }
      : {},
  });

  const data = unwrap(response);

  return data.submissions ?? [];
};

/**
 * ===============================
 * Coding Progress
 * ===============================
 */

export const getCodingProgress = async () => {
  const response = await api.get("/coding/progress");
  return unwrap(response);
};