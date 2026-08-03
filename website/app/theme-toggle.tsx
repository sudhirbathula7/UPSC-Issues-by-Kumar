"use client";

import { useEffect, useState } from "react";


type Theme = "light" | "dark";


export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const savedTheme =
      window.localStorage.getItem("site-theme") as
        | Theme
        | null;

    const preferredTheme: Theme =
      savedTheme ??
      (
        window.matchMedia(
          "(prefers-color-scheme: dark)",
        ).matches
          ? "dark"
          : "light"
      );

    document.documentElement.dataset.theme =
      preferredTheme;

    setTheme(preferredTheme);
    setMounted(true);
  }, []);

  function toggleTheme() {
    const nextTheme: Theme =
      theme === "light"
        ? "dark"
        : "light";

    document.documentElement.dataset.theme =
      nextTheme;

    window.localStorage.setItem(
      "site-theme",
      nextTheme,
    );

    setTheme(nextTheme);
  }

  if (!mounted) {
    return (
      <button
        className="theme-toggle"
        type="button"
        aria-label="Change website theme"
      >
        ◐
      </button>
    );
  }

  return (
    <button
      className="theme-toggle"
      type="button"
      onClick={toggleTheme}
      aria-label={
        theme === "light"
          ? "Switch to dark mode"
          : "Switch to light mode"
      }
      title={
        theme === "light"
          ? "Dark mode"
          : "Light mode"
      }
    >
      {theme === "light" ? "☾" : "☀"}
    </button>
  );
}