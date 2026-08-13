# Documentation assets

Brand images used by the root and mobile READMEs.

| File | Source | Use |
|------|--------|-----|
| `yolocilin-logo.png` | `mobile/assets/branding/app_logo.png` | README hero mark |
| `yolocilin-banner.png` | `mobile/assets/illustrations/yolocilin_vial_banner.png` | README banner |
| `report-figures/*.png` | `scripts/generate_internship_report_docx.py` (`prepare_figures`) | Architecture and catalog charts in the internship report |

Sample medicine photos for demos stay under [`data/samples/`](../../data/samples/) (linked from the root README) so large binaries are not duplicated here.

The Düzce University logo is **not** in Git. Place `docs/assets/duzce-university-logo.png` on your machine only if you generate the Word cover locally. Generated `.docx` files are gitignored; run:

```powershell
python scripts/generate_internship_report_tr.py
python scripts/generate_internship_report_docx.py
```

To refresh brand copies after a design change:

```powershell
Copy-Item mobile\assets\branding\app_logo.png docs\assets\yolocilin-logo.png
Copy-Item mobile\assets\illustrations\yolocilin_vial_banner.png docs\assets\yolocilin-banner.png
```
