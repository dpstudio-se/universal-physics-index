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
- **Manifest-validering**: Varje plugin måste ha en `plugin.json` som deklarerar permissions.
- **Resursbegränsningar**: CPU och RAM definieras i manifestet för att förhindra "noisy neighbor"-problem.
- **Permission-model**:
  - `file`: Tillgång till begränsade volymer.
  - `network`: Begränsad utgående trafik (inga host-mounts).
  - `exec`: Förbjudet i produktion för okända plugins.

### 2. Dataflöde & Persistens
Ingen kritisk state lagras i RAM. 
- **State Store**: Allt tillstånd sparas i en distribuerad KV-store eller SQL-databas.
- **Communication**: Inter-process kommunikation sker via Angelica Gateway (OpenAPI).

### 3. CI/CD & Kvalitetskontroll
- **Linter**: ESLint/Prettier (TS), Black/Flake8 (Py).
- **Säkerhet**: Trivy-scanning av container-images.
- **Validering**: Automatisk validering av `plugin.json` mot `plugin.schema.json`.

## Simulator-miljö (BVR)
För att säkerställa reproducerbarhet körs systemet i en simulatormiljö:
- **Mocks**: Puter-mock, Oden-mock och OdensEye-mock används för att testa Angelica's orkestreringslogik utan behov av fullständiga tunga modeller.
- **BVR Scenarier**: Definitioner av "Beyond Visual Range"-scenarier för att stresstesta agentens beslutsfattande under tidsnöd.
