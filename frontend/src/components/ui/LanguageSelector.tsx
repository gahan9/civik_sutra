import { useCallback } from "react";
import { useTranslation } from "react-i18next";

const LANGUAGES = [
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "hi", label: "Hindi", nativeLabel: "हिन्दी" },
] as const;

export function LanguageSelector() {
  const { i18n } = useTranslation();

  const handleChange = useCallback(
    (code: string) => {
      i18n.changeLanguage(code);
      localStorage.setItem("civiksutra-language", code);
    },
    [i18n],
  );

  return (
    <div className="language-selector">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          type="button"
          className={
            i18n.language === lang.code
              ? "lang-btn lang-btn--active"
              : "lang-btn"
          }
          onClick={() => handleChange(lang.code)}
          aria-label={`Switch to ${lang.label}`}
        >
          {lang.nativeLabel}
        </button>
      ))}
    </div>
  );
}
