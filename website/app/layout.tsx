import type { CSSProperties } from "react";
import type { Metadata } from "next";

import { BRAND } from "@/lib/branding";
import { DESIGN } from "@/lib/design";

import "./globals.css";


export const metadata: Metadata = {
  title: {
    default: BRAND.name,
    template: `%s | ${BRAND.name}`,
  },

  description: BRAND.description,

  keywords: [
    "UPSC",
    "current affairs",
    "editorial analysis",
    "UPSC mains",
    "active recall",
    "knowledge anchors",
    BRAND.name,
  ],
};


const designVariables = {
  "--content-width":
    `${DESIGN.layout.contentWidth}px`,

  "--page-padding":
    `${DESIGN.layout.pagePadding}px`,

  "--header-height":
    `${DESIGN.layout.headerHeight}px`,

  "--hero-top-padding":
    `${DESIGN.layout.heroTopPadding}px`,

  "--hero-bottom-padding":
    `${DESIGN.layout.heroBottomPadding}px`,

  "--hero-gap":
    `${DESIGN.layout.heroGap}px`,

  "--section-top-padding":
    `${DESIGN.layout.sectionTopPadding}px`,

  "--section-bottom-padding":
    `${DESIGN.layout.sectionBottomPadding}px`,

  "--card-gap":
    `${DESIGN.layout.cardGap}px`,

  "--section-gap":
    `${DESIGN.spacing.sectionGap}px`,

  "--header-gap":
    `${DESIGN.spacing.headerGap}px`,

  "--navigation-gap":
    `${DESIGN.spacing.navigationGap}px`,

  "--action-gap":
    `${DESIGN.spacing.actionGap}px`,

  "--hero-text-gap":
    `${DESIGN.spacing.heroTextGap}px`,

  "--hero-button-gap":
    `${DESIGN.spacing.heroButtonGap}px`,

  "--hero-stats-gap":
    `${DESIGN.spacing.heroStatsGap}px`,

  "--download-gap":
    `${DESIGN.spacing.downloadGap}px`,

  "--card-internal-gap":
    `${DESIGN.spacing.cardInternalGap}px`,

  "--font-serif":
    DESIGN.typography.serif,

  "--font-sans":
    DESIGN.typography.sans,

  "--hero-title-size":
    `${DESIGN.typography.heroTitle}px`,

  "--section-title-size":
    `${DESIGN.typography.sectionTitle}px`,

  "--card-title-size":
    `${DESIGN.typography.cardTitle}px`,

  "--body-size":
    `${DESIGN.typography.body}px`,

  "--small-size":
    `${DESIGN.typography.small}px`,

  "--tiny-size":
    `${DESIGN.typography.tiny}px`,

  "--nav-size":
    `${DESIGN.typography.nav}px`,

  "--button-size":
    `${DESIGN.typography.button}px`,

  "--title-line-height":
    DESIGN.typography.titleLineHeight,

  "--body-line-height":
    DESIGN.typography.bodyLineHeight,

  "--radius-small":
    `${DESIGN.radius.small}px`,

  "--radius-medium":
    `${DESIGN.radius.medium}px`,

  "--radius-large":
    `${DESIGN.radius.large}px`,

  "--radius-pill":
    `${DESIGN.radius.pill}px`,

  "--shadow-small":
    DESIGN.shadows.small,

  "--shadow-medium":
    DESIGN.shadows.medium,

  "--header-logo-size":
    `${DESIGN.header.logoSize}px`,

  "--header-brand-size":
    `${DESIGN.header.brandSize}px`,

  "--header-subtitle-size":
    `${DESIGN.header.subtitleSize}px`,

  "--header-button-height":
    `${DESIGN.header.buttonHeight}px`,

  "--header-button-padding":
    `${DESIGN.header.buttonPadding}px`,

  "--hero-min-height":
    `${DESIGN.hero.minHeight}px`,

  "--hero-content-max-width":
    `${DESIGN.hero.contentMaxWidth}px`,

  "--hero-visual-min-height":
    `${DESIGN.hero.visualMinHeight}px`,

  "--hero-badge-height":
    `${DESIGN.hero.badgeHeight}px`,

  "--hero-primary-button-width":
    `${DESIGN.hero.primaryButtonWidth}px`,

  "--hero-button-height":
    `${DESIGN.hero.buttonHeight}px`,

  "--editorial-card-width":
    `${DESIGN.hero.editorialCardWidth}px`,

  "--editorial-card-padding":
    `${DESIGN.hero.editorialCardPadding}px`,

  "--book-width":
    `${DESIGN.hero.bookWidth}px`,

  "--book-height":
    `${DESIGN.hero.bookHeight}px`,

  "--circle-size":
    `${DESIGN.hero.circleSize}px`,

  "--download-panel-padding-y":
    `${DESIGN.download.panelPaddingY}px`,

  "--download-panel-padding-x":
    `${DESIGN.download.panelPaddingX}px`,

  "--download-title-size":
    `${DESIGN.download.titleSize}px`,

  "--download-button-width":
    `${DESIGN.download.buttonWidth}px`,

  "--download-button-height":
    `${DESIGN.download.buttonHeight}px`,

  "--card-min-height":
    `${DESIGN.cards.minHeight}px`,

  "--card-padding":
    `${DESIGN.cards.padding}px`,

  "--issue-card-title-size":
    `${DESIGN.cards.titleSize}px`,

  "--issue-question-size":
    `${DESIGN.cards.questionSize}px`,

  "--tag-padding-y":
    `${DESIGN.cards.tagPaddingY}px`,

  "--tag-padding-x":
    `${DESIGN.cards.tagPaddingX}px`,

  "--footer-top-padding":
    `${DESIGN.footer.topPadding}px`,

  "--footer-bottom-padding":
    `${DESIGN.footer.bottomPadding}px`,

  "--page-background":
    DESIGN.colors.light.pageBackground,

  "--surface":
    DESIGN.colors.light.surface,

  "--surface-soft":
    DESIGN.colors.light.surfaceSoft,

  "--text-primary":
    DESIGN.colors.light.textPrimary,

  "--text-secondary":
    DESIGN.colors.light.textSecondary,

  "--text-muted":
    DESIGN.colors.light.textMuted,

  "--navy":
    DESIGN.colors.light.navy,

  "--gold":
    DESIGN.colors.light.gold,

  "--border":
    DESIGN.colors.light.border,

  "--dark-page-background":
    DESIGN.colors.dark.pageBackground,

  "--dark-surface":
    DESIGN.colors.dark.surface,

  "--dark-surface-soft":
    DESIGN.colors.dark.surfaceSoft,

  "--dark-text-primary":
    DESIGN.colors.dark.textPrimary,

  "--dark-text-secondary":
    DESIGN.colors.dark.textSecondary,

  "--dark-text-muted":
    DESIGN.colors.dark.textMuted,

  "--dark-navy":
    DESIGN.colors.dark.navy,

  "--dark-gold":
    DESIGN.colors.dark.gold,

  "--dark-border":
    DESIGN.colors.dark.border,
} as CSSProperties;


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
    >
      <body style={designVariables}>
        {children}
      </body>
    </html>
  );
}