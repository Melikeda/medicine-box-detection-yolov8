# Windows: WSL2 + Docker Desktop Helper Scripts

PowerShell scripts for setting up Docker Desktop on Windows (WSL2 backend).

**Requires:** Administrator PowerShell (`#Requires -RunAsAdministrator`)

All scripts write logs under `scripts/*.log` (gitignored).

---

## Quick start

```powershell
# 1) First install (Admin)
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\install-wsl-docker.ps1

# 2) Reboot if script says REBOOT REQUIRED

# 3) After reboot (Admin)
.\scripts\post-reboot-docker.ps1
```

When Docker engine is running:

```powershell
docker compose up --build
curl http://127.0.0.1:8000/health
```

---

## Script reference

| Script | Purpose |
|--------|---------|
| `install-wsl-docker.ps1` | Enable WSL/VMP features, install WSL + Docker Desktop via winget |
| `post-reboot-docker.ps1` | Post-reboot: verify WSL2, start Docker, optional `docker compose up` |
| `diagnose-wsl.ps1` | Log Windows features, services, `wsl --status` (15s timeout) |
| `fix-docker-wsl.ps1` | Repair WSL features, update WSL, restart Docker Desktop |
| `fix-wsl-winget.ps1` | Reinstall Microsoft.WSL via winget when DISM changes revert |
| `fix-wsl-final.ps1` | DISM + Enable-WindowsOptionalFeature for WSL + VMP |
| `fix-vmp.ps1` | Enable Virtual Machine Platform only |
| `uninstall-docker.ps1` | Remove Docker Desktop and leftover data |
| `docker-entrypoint.sh` | Container startup (model check, SQLite seed, API) — Linux only |

---

## Common issues

### WSL2 not starting / "Virtual Machine Platform"

1. Win+R → `optionalfeatures.exe` → enable:
   - Windows Subsystem for Linux
   - Virtual Machine Platform
2. Disable **Fast Startup** (Control Panel → Power Options)
3. Full reboot: `shutdown /r /t 0`
4. Run `.\scripts\post-reboot-docker.ps1`

### BIOS virtualization

Enable **Intel VT-x / AMD-V** (Huawei/Laptop: Virtualization Technology → Enabled).  
Guide: https://aka.ms/enablevirtualization

### Docker engine never ready

- Open Docker Desktop manually and read the error tray
- Run `.\scripts\diagnose-wsl.ps1` → check `scripts\diagnose-wsl.log`
- Run `wsl --status` in Admin PowerShell

### YOLO model missing

Docker needs trained weights at:

`runs/detect/runs/detect/medicine_box_yolov8n-2/weights/best.pt`

Train locally: `python src/train.py`

### Low disk space (emulator / Docker)

Docker images and WSL distros use significant C: drive space. Keep several GB free.

---

## Related docs

- [Report 14 — Docker Containerization](../docs/reports/14-docker-containerization.md)
- [Setup guide — Docker section](../docs/setup-guide.md)
