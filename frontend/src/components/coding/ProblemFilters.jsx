import { useEffect, useState } from "react";
import { Search } from "lucide-react";

import { CODING_DIFFICULTIES } from "../../constants/codingDifficulties";
import { PROGRAMMING_LANGUAGES } from "../../constants/languages";
import { getProblemCategories } from "../../services/codingService";

const ProblemFilters = ({
  search,
  onSearchChange,

  category,
  onCategoryChange,

  difficulty,
  onDifficultyChange,

  language,
  onLanguageChange,
}) => {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const data = await getProblemCategories();
        setCategories(data.categories ?? []);
      } catch {
        setCategories([]);
      }
    };

    loadCategories();
  }, []);

  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center">

      {/* Search */}

      <div className="relative flex-1">
        <Search
          size={16}
          className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
        />

        <input
          type="text"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search problems..."
          aria-label="Search coding problems"
          className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-10 py-2.5 text-sm text-slate-200 placeholder:text-slate-500 transition-colors focus:border-accent focus:outline-none"
        />
      </div>

      {/* Category */}

      <select
        value={category}
        onChange={(event) => onCategoryChange(event.target.value)}
        aria-label="Filter by category"
        className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 transition-colors focus:border-accent focus:outline-none"
      >
        <option value="">All Categories</option>

        {categories.map((categoryName) => (
          <option
            key={categoryName}
            value={categoryName}
          >
            {categoryName}
          </option>
        ))}
      </select>

      {/* Difficulty */}

      <select
        value={difficulty}
        onChange={(event) => onDifficultyChange(event.target.value)}
        aria-label="Filter by difficulty"
        className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm capitalize text-slate-200 transition-colors focus:border-accent focus:outline-none"
      >
        <option value="">All Difficulties</option>

        {CODING_DIFFICULTIES.map((difficulty) => (
          <option
            key={difficulty}
            value={difficulty}
            className="capitalize"
          >
            {difficulty}
          </option>
        ))}
      </select>

      {/* Language */}

      <select
        value={language}
        onChange={(event) => onLanguageChange(event.target.value)}
        aria-label="Preferred language"
        className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 transition-colors focus:border-accent focus:outline-none"
      >
        <option value="">Preferred Language</option>

        {PROGRAMMING_LANGUAGES.map((language) => (
          <option key={language.value} value={language.value}>
            {language.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ProblemFilters;