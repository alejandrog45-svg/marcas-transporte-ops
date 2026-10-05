const cfg = {
      darkMode: "class",
      theme: {
        extend: {
          "colors": {
            "on-tertiary-container": "#ffeedd",
            "outline": "#8d90a0",
            "surface": "#0e1321",
            "tertiary": "#ffb95f",
            "on-tertiary-fixed": "#2a1700",
            "tertiary-container": "#996100",
            "surface-bright": "#343948",
            "surface-variant": "#303444",
            "on-secondary-container": "#00424e",
            "inverse-on-surface": "#2b303f",
            "surface-container-low": "#161b2a",
            "on-secondary": "#003640",
            "primary-container": "#2563eb",
            "error-container": "#93000a",
            "surface-dim": "#0e1321",
            "tertiary-fixed-dim": "#ffb95f",
            "outline-variant": "#434655",
            "background": "#0e1321",
            "on-secondary-fixed": "#001f26",
            "secondary-fixed": "#acedff",
            "on-secondary-fixed-variant": "#004e5c",
            "secondary-fixed-dim": "#4cd7f6",
            "secondary": "#4cd7f6",
            "on-surface": "#dee2f6",
            "on-primary-fixed-variant": "#003ea8",
            "on-surface-variant": "#c3c6d7",
            "surface-tint": "#b4c5ff",
            "on-background": "#dee2f6",
            "primary-fixed": "#dbe1ff",
            "surface-container": "#1a1f2e",
            "error": "#ffb4ab",
            "on-primary-container": "#eeefff",
            "surface-container-high": "#252a39",
            "on-tertiary": "#472a00",
            "on-tertiary-fixed-variant": "#653e00",
            "inverse-surface": "#dee2f6",
            "primary": "#b4c5ff",
            "surface-container-highest": "#303444",
            "inverse-primary": "#0053db",
            "primary-fixed-dim": "#b4c5ff",
            "tertiary-fixed": "#ffddb8",
            "surface-container-lowest": "#090e1c",
            "secondary-container": "#03b5d3",
            "on-primary": "#002a78",
            "on-error": "#690005",
            "on-error-container": "#ffdad6",
            "on-primary-fixed": "#00174b"
          },
          "borderRadius": {
            "DEFAULT": "0.125rem",
            "lg": "0.25rem",
            "xl": "0.5rem",
            "full": "0.75rem"
          },
          "spacing": {
            "space-lg": "1.5rem",
            "space-md": "1rem",
            "gutter-desktop": "1.5rem",
            "margin-desktop": "2rem",
            "space-xs": "0.25rem",
            "space-2xl": "3rem",
            "space-xl": "2rem",
            "gutter": "1rem",
            "space-sm": "0.5rem",
            "margin": "1rem"
          },
          "fontFamily": {
            "label-sm": ["Inter"],
            "headline-sm": ["Plus Jakarta Sans"],
            "body-sm": ["Inter"],
            "body-md": ["Inter"],
            "headline-lg": ["Plus Jakarta Sans"],
            "body-lg": ["Inter"],
            "display-lg": ["Plus Jakarta Sans"],
            "numeric-table": ["Inter"],
            "headline-md": ["Plus Jakarta Sans"],
            "label-md": ["Inter"]
          },
          "fontSize": {
            "label-sm": ["11px", { "lineHeight": "14px", "letterSpacing": "0.04em", "fontWeight": "600" }],
            "headline-sm": ["16px", { "lineHeight": "24px", "letterSpacing": "-0.005em", "fontWeight": "600" }],
            "body-sm": ["12px", { "lineHeight": "16px", "fontWeight": "400" }],
            "body-md": ["14px", { "lineHeight": "20px", "fontWeight": "400" }],
            "headline-lg": ["24px", { "lineHeight": "32px", "letterSpacing": "-0.015em", "fontWeight": "600" }],
            "body-lg": ["16px", { "lineHeight": "24px", "fontWeight": "400" }],
            "display-lg": ["32px", { "lineHeight": "40px", "letterSpacing": "-0.02em", "fontWeight": "700" }],
            "numeric-table": ["13px", { "lineHeight": "18px", "letterSpacing": "-0.01em", "fontWeight": "500" }],
            "headline-md": ["20px", { "lineHeight": "28px", "letterSpacing": "-0.01em", "fontWeight": "600" }],
            "label-md": ["13px", { "lineHeight": "18px", "fontWeight": "500" }]
          }
        }
      }
    };
cfg.content=['./.build/*.html'];
cfg.plugins=[require('@tailwindcss/forms')];
module.exports=cfg;
