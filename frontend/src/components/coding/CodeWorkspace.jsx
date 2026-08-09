import Editor from "@monaco-editor/react";
import { Play, RotateCcw, Send } from "lucide-react";

import { PROGRAMMING_LANGUAGES } from "../../constants/languages";

const languageLabels = Object.fromEntries(
  PROGRAMMING_LANGUAGES.map((language) => [
    language.value,
    language.label,
  ])
);

const CodeWorkspace = ({
  language,
  onLanguageChange,
  availableLanguages,
  code,
  onCodeChange,
  onRun,
  onSubmit,
  onReset,
  isRunning,
  isSubmitting,
}) => {
  const isBusy = isRunning || isSubmitting;

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/80">

      {/* Toolbar */}

      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">

        <select
          value={language}
          onChange={(event) => onLanguageChange(event.target.value)}
          aria-label="Programming language"
          className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5 text-sm text-slate-200 focus:border-accent focus:outline-none"
        >
          {availableLanguages.map((lang) => (
            <option
              key={lang}
              value={lang}
            >
              {languageLabels[lang] ?? lang}
            </option>
          ))}
        </select>

        <div className="flex items-center gap-2">

          <button
            type="button"
            onClick={onReset}
            disabled={isBusy}
            title="Reset to starter code"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-800 hover:text-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <RotateCcw size={15} />
          </button>

          <button
            type="button"
            onClick={onRun}
            disabled={isBusy}
            className="flex items-center gap-2 rounded-xl border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-200 transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Play size={14} />

            {isRunning ? "Running..." : "Run"}
          </button>

          <button
            type="button"
            onClick={onSubmit}
            disabled={isBusy}
            className="flex items-center gap-2 rounded-xl bg-accent px-3 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send size={14} />

            {isSubmitting ? "Submitting..." : "Submit"}
          </button>

        </div>
      </div>

      {/* Monaco */}

      <div className="min-h-[320px] flex-1">

        <Editor
          height="100%"
          defaultLanguage={language}
          language={language}
          value={code}
          theme="vs-dark"
          saveViewState
          onChange={(value) => onCodeChange(value ?? "")}
          options={{
            automaticLayout: true,
            minimap: {
              enabled: false,
            },
            fontSize: 14,
            tabSize: 4,
            wordWrap: "on",
            scrollBeyondLastLine: false,
            padding: {
              top: 16,
            },
          }}
        />

      </div>

    </div>
  );
};

export default CodeWorkspace;