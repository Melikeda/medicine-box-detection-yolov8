# Documentation assets

Brand images used by the root and mobile READMEs.

| File | Source | Use |
|------|--------|-----|
| `yolocilin-logo.png` | `mobile/assets/branding/app_logo.png` | README hero mark |
| `yolocilin-banner.png` | `mobile/assets/illustrations/yolocilin_vial_banner.png` | README banner |

Sample medicine photos for demos stay under [`data/samples/`](../../data/samples/) (linked from the root README) so large binaries are not duplicated here.

To refresh brand copies after a design change:

```powershell
Copy-Item mobile\assets\branding\app_logo.png docs\assets\yolocilin-logo.png
Copy-Item mobile\assets\illustrations\yolocilin_vial_banner.png docs\assets\yolocilin-banner.png
```
