# Documentation assets

Brand images used by the root and mobile READMEs.

| File | Source | Use |
|------|--------|-----|
| `yolocilin-logo.png` | `mobile/assets/branding/app_logo.png` | Mobile README mark |
| `yolocilin-banner.png` | `mobile/assets/illustrations/yolocilin_vial_banner.png` | Root README hero |
| `yolocilin-app.gif` | App home-screen capture | README mobile preview |
| `report-figures/*.png` | Local charts | Architecture and catalog figures used in the university Word report |

Sample medicine photos for demos stay under [`data/samples/`](../../data/samples/) (linked from the root README) so large binaries are not duplicated here.

The Düzce University logo is **not** in Git. Internship Word reports (Turkish CE499 + English) are generated locally and kept out of the repository.

To refresh brand copies after a design change:

```powershell
Copy-Item mobile\assets\branding\app_logo.png docs\assets\yolocilin-logo.png
Copy-Item mobile\assets\illustrations\yolocilin_vial_banner.png docs\assets\yolocilin-banner.png
```
