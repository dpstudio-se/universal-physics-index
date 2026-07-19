# ARCHITECTURE.md - VR-ASI-1 Systemarkitektur

## Övergripande Vision
VR-ASI-1 är en integrerad AI/Web-OS-plattform designad för autonom orkestrering och multimodala operationer. Systemet följer principer för modulär redundans och strikt isolering, analogt med JAS-39 Gripen's systemarkitektur (fly-by-wire, modulära avionik-enheter).

### Komponentmapping (JAS-39 Analogi)
- **Puter (Web-OS)** $\rightarrow$ *Cockpit/HMI*: Användargränssnitt och grundläggande operativmiljö.
- **Angelica Core (Orkestrator)** $\rightarrow$ *Flight Control Computer (FCC)*: Central kontrollenhet som hanterar resursfördelning, sandboxing och plugin-livscykler.
- **Oden (Agent)** $\rightarrow$ *Mission Computer*: Strategisk planering och exekvering av mål.
- **Odens Öga (G0DM0D3)** $\rightarrow$ *Samsensor-system (IRST/Radar)*: Multimodal perception och dataanalys.

## Systemdesign
### 1. Plugin-plattform & Sandboxing
Alla plugins körs i isolerade containrar (Docker/Process-isolation). 
- **Manifest-validering**: Varje plugin måste ha ett JSON-manifest, exempelvis
  `oden.json` eller `odens_eye.json`, som följer `plugin.schema.json` och deklarerar permissions.
- **Resursbegränsningar**: CPU och RAM definieras i manifestet för att förhindra "noisy neighbor"-problem.
- **Permission-model**:
  - `file: false`: Kör containern med ett skrivskyddat filsystem.
  - `network: false`: Kör containern med `--network none`; `true` ger aldrig host-nätverk.
  - `exec: true`: Nekas som standard och kräver ett uttryckligt policyundantag.
- **Manifest-policy**: Okända fält, absoluta/traverserande entrypoints och ogiltiga resursvärden nekas.

### 2. Dataflöde & Persistens
Ingen kritisk state lagras i RAM. 
- **State Store**: Allt tillstånd sparas i en distribuerad KV-store eller SQL-databas.
- **Communication**: Inter-process kommunikation sker via Angelica Gateway (OpenAPI).

### 3. CI/CD & Kvalitetskontroll
- **Linter**: ESLint/Prettier (TS), Black/Flake8 (Py).
- **Säkerhet**: Trivy-scanning av container-images.
- **Validering**: Automatisk validering av varje pluginmanifest mot `plugin.schema.json`.

## Simulator-miljö (BVR)
För att säkerställa reproducerbarhet körs systemet i en simulatormiljö:
- **Mocks**: Puter-mock, Oden-mock och OdensEye-mock används för att testa Angelica's orkestreringslogik utan behov av fullständiga tunga modeller.
- **BVR Scenarier**: Definitioner av "Beyond Visual Range"-scenarier för att stresstesta agentens beslutsfattande under tidsnöd.
