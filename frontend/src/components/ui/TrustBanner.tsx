import { useTranslation } from "react-i18next";

/**
 * Persistent civic-trust notice: education only, official sources for decisions.
 */
export function TrustBanner() {
  const { t } = useTranslation();
  return (
    <aside className="trust-banner" aria-label={t("trust.ariaLabel")}>
      <p className="trust-banner__text">
        {t("trust.body")}{" "}
        <a
          className="trust-banner__link"
          href="https://www.eci.gov.in/"
          target="_blank"
          rel="noopener noreferrer"
        >
          {t("trust.linkEci")}
        </a>
        {", "}
        <a
          className="trust-banner__link"
          href="https://voters.eci.gov.in/"
          target="_blank"
          rel="noopener noreferrer"
        >
          {t("trust.linkElectoralSearch")}
        </a>
        {", "}
        <a
          className="trust-banner__link"
          href="https://www.nvsp.in/"
          target="_blank"
          rel="noopener noreferrer"
        >
          {t("trust.linkNvsp")}
        </a>
        . {t("trust.footer")}
      </p>
    </aside>
  );
}
