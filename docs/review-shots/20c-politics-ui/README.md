# 20th-century politics, internet subcultures, domain filter, UI cleanup

Data: 13 new ideas (100 total), a `domain` field on every idea, schema and CI check.
Page: domain filter chips plus a compact glass toolbar with collapsible panels.
`memeplex.html` here is the full proposed page, and `memeplex-html.diff` is the change against the current page.

Shots: `before-*` show the current page and `after-*` show this PR, on desktop at 1440x900 and on a phone at 390x844.
- `after-1-default`: minimal start, with every panel collapsed.
- `after-7-panels-open`: Search, Color, Key and Filter opened. Their open/closed state is saved in localStorage `memeplex-ui`.
- `after-4b..4e`: the domain filter set to Political theory, Religion, Philosophy, and Internet & culture.
- `after-6*`: phone. The toolbar is a single row of icons and each panel opens as a bottom sheet, one at a time.

Checks: no overlapping labels in any view, 0 console errors, and the display check passes.
