export const DESIGN = {
  colors: {
    light: {
      pageBackground: "#f6f1e8",
      surface: "#ffffff",
      surfaceSoft: "#fbf7ef",

      textPrimary: "#142746",
      textSecondary: "#5f6877",
      textMuted: "#8b929d",

      navy: "#173d6a",
      gold: "#b98a34",
      border: "#e5ddcf",
    },

    dark: {
      pageBackground: "#0c1521",
      surface: "#132234",
      surfaceSoft: "#18293d",

      textPrimary: "#eef4fb",
      textSecondary: "#bcc7d7",
      textMuted: "#8d99ab",

      navy: "#77aff5",
      gold: "#e2ae55",
      border: "#31445b",
    },
  },

  typography: {
    serif: "Georgia, 'Times New Roman', serif",
    sans: "Arial, Helvetica, sans-serif",

    heroTitle: 74,
    sectionTitle: 42,
    cardTitle: 22,
    body: 16,
    small: 13,
    tiny: 11,
    nav: 13,
    button: 13,

    titleLineHeight: 1.03,
    bodyLineHeight: 1.65,
  },

  layout: {
    contentWidth: 1460,
    pagePadding: 34,

    headerHeight: 125,

    heroTopPadding: 58,
    heroBottomPadding: 24,
    heroGap: 94,

    sectionTopPadding: 24,
    sectionBottomPadding: 24,

    cardGap: 20,
  },

  spacing: {
    sectionGap: 72,

    headerGap: 38,
    navigationGap: 34,
    actionGap: 12,

    heroTextGap: 24,
    heroButtonGap: 14,
    heroStatsGap: 44,

    downloadGap: 44,
    cardInternalGap: 18,
  },

  radius: {
    small: 8,
    medium: 14,
    large: 20,
    pill: 999,
  },

  shadows: {
    small: "0 6px 18px rgba(20, 39, 70, 0.06)",
    medium: "0 16px 38px rgba(20, 39, 70, 0.10)",
  },

  header: {
    logoSize: 72,
    brandSize: 30,
    subtitleSize: 14,

    buttonHeight: 42,
    buttonPadding: 18,
  },

  hero: {
    minHeight: 520,

    contentMaxWidth: 650,
    visualMinHeight: 500,

    badgeHeight: 30,

    primaryButtonWidth: 178,
    buttonHeight: 48,

    editorialCardWidth: 470,
    editorialCardPadding: 36,

    bookWidth: 210,
    bookHeight: 270,

    circleSize: 112,
  },

  download: {
    panelPaddingY: 30,
    panelPaddingX: 38,

    titleSize: 34,

    buttonWidth: 170,
    buttonHeight: 46,
  },

  cards: {
    minHeight: 245,
    padding: 20,

    titleSize: 20,
    questionSize: 13,

    tagPaddingY: 5,
    tagPaddingX: 9,
  },

  footer: {
    topPadding: 36,
    bottomPadding: 22,
  },
} as const;