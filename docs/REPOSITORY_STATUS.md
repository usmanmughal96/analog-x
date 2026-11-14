# Repository and deployment status

## Public repository
https://github.com/usmanmughal96/analog-x

Default branch: main. Public visibility and write access confirmed.

## GitHub Pages
GitHub Pages has been enabled by the repository owner. The GitHub Actions workflow successfully passed Configure Pages and Upload site on the current deployment sequence. The latest run is tracked here: https://github.com/usmanmughal96/analog-x/actions

Expected public addresses:
- https://usmanmughal96.github.io/analog-x/
- https://usmanmughal96.github.io/analog-x/demo.html

Confirm the latest deployment run is green and test both links in a private browser before submitting to NASA.

## Current application
The root `index.html` is now the ANALOG-X Mission-to-Field Planner:
- Mission reference: Mars Syrtis Major, Mars Jezero or lunar south-polar/Shackleton context.
- Task: geology/sample-context, rover-traverse workflow, wind/dust experiment, thermal equipment trial or solar operations.
- Candidate environments: Koh-i-Sultan, Dallol, Atacama, McMurdo Dry Valleys, Haughton, Iceland, Death Valley; users can add custom coordinates.
- Live NASA POWER point climatology requests in the browser.
- Relative Field-Campaign Index, monthly field-window suggestions, map, CSV/JSON exports and a downloadable field-test plan.

The index is not a planetary similarity score. It ranks only Earth campaign conditions for selected sites and the selected task. Raw MOLA/Diviner/LOLA rasters are not processed by this build. SUPARCO Space4Climate products are not claimed as ingested.

## Binary deliverables
PDF/PPTX presentation and technical report are in the separately prepared submission package. The browser demo is `demo.html`.

## Remaining validation
Run the public app in a browser and execute a live NASA POWER scan. Confirm API/CORS availability, inspect returned values and generate one field-test card. Capture screenshots of actual scan results for the NASA submission.