import { useState } from "react";
import { Code2, Loader2 } from "lucide-react";
import { PROGRAMMING_LANGUAGES } from "../../constants/languages";

const LanguagePickerModal = ({ onSelect, isSaving, error }) => {
  const [selectedLanguage, setSelectedLanguage] = useState("");

  const handleContinue = () => {
    if (!selectedLanguage || isSaving) return;
    onSelect(selectedLanguage);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="language-picker-title"
    >
      <div className="w-full max-w-lg rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">

        <div className="flex flex-col items-center text-center">

          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/15 text-accent">
            <Code2 size={26} />
          </div>

          <h2
            id="language-picker-title"
            className="text-xl font-semibold text-slate-100"
          >
            Choose Preferred Language
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            Select the language you want to use by default for coding practice. You can change it later at any time.
          </p>
        </div>

        <div className="mt-8 grid grid-cols-2 gap-4">
          {PROGRAMMING_LANGUAGES.map((language) => {
            const active = selectedLanguage === language.value;

            return (
              <button
                key={language.value}
                type="button"
                disabled={isSaving}
                onClick={() => setSelectedLanguage(language.value)}
                className={`rounded-2xl border p-5 text-left transition-all duration-200 ${
                  active
                    ? "border-accent bg-accent/10"
                    : "border-slate-800 bg-slate-950 hover:border-accent/40 hover:bg-slate-900"
                } disabled:cursor-not-allowed disabled:opacity-60`}
              >
                <div className="font-medium text-slate-100">{language.label}</div>
                <div className="mt-1 text-xs text-slate-500">{language.description}</div>
              </button>
            );
          })}
        </div>

        {error && <p className="mt-6 text-sm text-red-400">{error}</p>}

        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={handleContinue}
            disabled={!selectedLanguage || isSaving}
            className="rounded-2xl bg-accent px-5 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Continue
          </button>
        </div>

        {isSaving && (
          <div className="mt-4 flex items-center justify-center gap-2 text-sm text-slate-400">
            <Loader2 className="animate-spin" size={16} />
            Saving your preference...
          </div>
        )}
      </div>
    </div>
  );
};

export default LanguagePickerModal;