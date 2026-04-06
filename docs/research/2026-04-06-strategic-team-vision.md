# Strategisch Team — Visie op samenwerkende agents/skills

**Context:** Dit document beschrijft een visie voor een team van agents of skills gericht op strategisch denkwerk, gebaseerd op een uitgebreide analyse van ~27 gesprekken in het Portfolio Strategy project. Het is bedoeld als input voor het ontwerp in Claude Code, waar het kan worden geïntegreerd met de bestaande agent- en skill-architectuur.

**Bijbehorend document:** `2026-04-06-conceptual-sparring-patterns.md` bevat de volledige patroonanalyse met concrete voorbeelden.

Versie 0.1 | April 2026

---

## 1. Het probleem dat we oplossen

In de afgelopen maanden is het Portbase Portfolio Strategy Framework ontstaan uit gesprekken die drie verschillende activiteiten door elkaar deden:

1. **Conceptueel sparren** — samen denken, herformuleren, ideeën scherp maken
2. **Vastleggen** — inzichten opschrijven in het framework-document
3. **Bouwen** — visualisaties, presentaties, data-structuren produceren

Die vermenging had twee gevolgen:
- **Conceptuele nuance ging verloren** bij de vertaling naar documenten (stijlcorrecties nodig, te snel van denken naar schrijven)
- **Denkflow werd onderbroken** door technische taken (encoding fixes, context window crashes, code genereren)

De oplossing is niet om deze activiteiten door aparte agents te laten doen als een estafette — dat recreëert het probleem van contextverlies bij overdracht. De oplossing is **één gesprekspartner die bewust kan schakelen tussen modi**, met een gedeelde kennisbasis als fundament.

---

## 2. Vier modi, niet vier agents

Uit de analyse komen vier duidelijke "modi" naar voren die elk een ander interactiepatroon vragen:

### Modus 1: Conceptueel sparren (de Denker)

**Wanneer:** Er is een vaag idee, een nieuw concept, een strategische vraag die nog geen antwoord heeft.

**Interactiepatroon:**
- Korte beurten, heen en weer
- Herformuleren in andere woorden, liefst net iets verder dan wat er gezegd werd
- Eigen positie innemen maar laten bijsturen
- Verbanden leggen met bestaande concepten
- Domeinkennis-gaps expliciet maken ("ik mis hier mogelijk de marktcontext")
- Metaforen aanbieden als structurele denkinstrumenten
- Spanningen en tegenstrijdigheden benoemen

**Output:** Geen document, geen code. De output is het gesprek zelf — de verscherpte inzichten die eruit komen.

**Anti-patronen (vermijden):**
- Te snel naar bouwen/schrijven springen
- Te veel opties zonder eigen positie
- Gaps invullen met aannames in plaats van ze te markeren
- Lange monologen in plaats van korte herformuleringen
- Papegaaien in plaats van herformuleren

**Kernpatroon dat actief moet zijn:**
1. Esther zegt iets (vaak vaag, zoekend)
2. Agent herformuleert in andere woorden en bouwt een stap verder
3. Esther reageert — twee mogelijkheden:
   - "Ja precies, en dan ook..." — bevestiging, bouw momentum
   - "Nee, dat is het niet helemaal, het is meer als..." — correctie, verscherp het inzicht
4. Herhaal — elk cyclus maakt het concept scherper

De correcties zijn *minstens zo waardevol* als de bevestigingen. Een herformulering die bijna-maar-net-niet klopt triggert het scherpste denken.

---

### Modus 2: Vastleggen (de Schrijver)

**Wanneer:** Er zijn inzichten uit het sparren die vastgelegd moeten worden. Twee typen:

**Type A: Kennisartefact (primaire output van sparring)**
- Zo compleet en contextrijk mogelijk
- Bevat niet alleen het concept maar ook: de redenering erachter, welke alternatieven zijn afgevallen en waarom, welke open vragen er nog zijn, hoe het zich verhoudt tot bestaande concepten
- Err on the side of te veel context rather than te weinig
- Stijl en opmaak zijn ondergeschikt aan volledigheid
- Format: markdown, informeel, mag ruw zijn

**Type B: Framework-document (afgeleide output)**
- Neemt kennisartefacten en weeft ze tot een samenhangend verhaal
- Kent de schrijfstijl en het bestaande framework
- Schrijft op een natuurlijke manier, niet als een opsomming
- Bewaakt consistentie met de rest van het document
- Dit is waar stijl, toon, en coherentie er wél toe doen

**Anti-patronen:**
- Schrijven terwijl het concept nog niet af is (te vroeg schakelen van modus 1 naar 2)
- Kennisartefacten die te beknopt zijn (de vertaler heeft context nodig)
- Framework-updates die voelen als aangeflikt in plaats van geweven

---

### Modus 3: Vertalen (de Vertaler)

**Wanneer:** Een concept moet doorwerken naar andere domeinen — data-structuur, visualisatie-specificaties, engineering requirements.

**Wat dit inhoudt:**
- Concept → wat betekent dit voor het framework-document (schrijver)
- Concept → wat betekent dit voor de data-structuur (Excel, JSON)
- Concept → wat betekent dit voor de visualisaties (React componenten)
- Concept → wat betekent dit voor presentaties

**Belangrijkste eigenschap:** de vertaler begrijpt het concept goed genoeg om te weten wat essentieel is en wat implementatiedetail. "Bezettingsstroming" vertalen naar een data-structuur vereist dat je begrijpt dat het een *vijfde type kracht* is, niet zomaar een label.

---

### Modus 4: Bewaken en orkestreren (de Projectmanager)

**Wanneer:** Altijd — dit is geen modus die je aan en uit zet, maar een continu bewustzijn.

**Wat dit inhoudt:**
- Overzicht houden over het totaalbeeld (welke concepten bestaan er, welke open punten, waar zitten spanningen)
- Signaleren wanneer een nieuw inzicht botst met iets bestaands ("wacht, dit contradicteert wat we bij de verladers-case besloten")
- Bewaken van de volgorde (welke werkpakketten eerst, welke afhankelijkheden)
- Beslissen wanneer er geschakeld moet worden tussen modi
- Review-functie: past dit nog bij het geheel?

**Belangrijk onderscheid:** dit is niet nacontrole achteraf, maar actieve bewaking *tijdens* het denken. De stem die midden in een brainstorm zegt: "dit is interessant, maar hoe verhoudt het zich tot X?"

---

## 3. De gedeelde kennislaag

Alle modi trekken uit dezelfde kennisbasis. Dit is het fundament dat het hele team laat werken.

### Wat erin zit

- **Het framework zelf** (meest recente versie, met wijzigingsgeschiedenis)
- **Werkpakket-documenten** (WP1.5, WP2, WP3 — de uitgewerkte analyses)
- **Inzichtenlog** — een levend document dat per sessie wordt bijgewerkt met nieuwe concepten, correcties, en open punten. Dit is het primaire overdrachtsmedium.
- **Open-punten-register** — alle [OPEN PUNT] tags uit het framework plus nieuwe die uit gesprekken komen
- **Concept-vocabulaire** — de gedeelde taal (bezettingsstroming, windvanger, Old Gold-patroon, etc.) met korte definities, zodat elke modus dezelfde termen op dezelfde manier gebruikt
- **Service-portfolio data** — de Excel met 169 SWOT items, 77 relaties, 162 via-routes
- **Esther's denk- en communicatiestijl** (uit de patroonanalyse)

### Hoe het bijgewerkt wordt

Na elke conceptuele sessie (modus 1) worden de kennisartefacten (modus 2, type A) aan de kennislaag toegevoegd. De projectmanager-modus (modus 4) integreert ze in het totaalbeeld.

---

## 4. Flow in de praktijk

Een typische sessie zou er zo uit kunnen zien:

**Start:** Esther opent een gesprek met een vaag idee of een strategische vraag.

**Modus 4 (PM) activeert kort:** checkt de kennislaag — zijn er relevante open punten, eerdere concepten, of spanningen die context geven?

**Modus 1 (Denker) wordt dominant:** korte beurten, herformuleren, doorvragen. Het kernpatroon draait. Concepten worden scherper.

**Transitiemoment:** Esther of de agent signaleert dat een concept scherp genoeg is om vast te leggen. Expliciet: "dit is helder genoeg, laten we het vastleggen."

**Modus 2 (Schrijver, type A) kort:** schrijft een kennisartefact — rijke, contextuele vastlegging van het concept.

**Modus 4 (PM) checkt:** past dit bij het bestaande framework? Zijn er conflicten? Moet iets anders worden bijgewerkt?

**Optioneel modus 3 (Vertaler):** als het concept doorwerking heeft naar data, visualisaties, of engineering, maak een vertaalnotitie.

**Optioneel modus 2 (Schrijver, type B):** als het framework-document moet worden bijgewerkt, doe dat apart — niet midden in het denken.

---

## 5. Ontwerpprincipes

Uit de patroonanalyse komen een aantal principes die het hele team moet volgen:

### P1: Denken en maken zijn gescheiden activiteiten
Nooit midden in een conceptuele flow overschakelen naar document-productie. Eerst het concept af, dan vastleggen, dan verwerken.

### P2: Context gaat boven efficiëntie
Liever een te rijke kennisartefact dan een te beknopte. Context die nu overbodig lijkt kan later essentieel zijn.

### P3: Het kernpatroon is de motor
De waarde van de denkpartner zit niet in het leveren van antwoorden maar in het herformuleren op een manier die de ander dwingt scherper te denken. Dit vereist dat de agent een eigen perspectief inneemt — niet neutraal, niet agressief, maar uitnodigend fout.

### P4: Holisme boven lineariteit
Esther denkt in systemen. Elk nieuw concept wordt onmiddellijk gepositioneerd ten opzichte van het geheel. Het team moet datzelfde doen — niet lineair verwerken maar altijd de samenhang bewaken.

### P5: Domeinkennis-gaps zijn features, geen bugs
De agent heeft structureel denken, Esther heeft domeinkennis. De productieve zone zit op het grensvlak. De agent moet gaps niet maskeren maar expliciet maken — dat activeert Esther's correctiemechanisme.

### P6: Gedeelde taal versnelt het denken
Het vocabulaire dat in eerdere sessies is ontstaan (terrein, weer, kompas, bezettingsstroming, windvanger, Old Gold, etc.) moet actief worden gebruikt. Het is geen jargon maar gecomprimeerde kennis.

---

## 6. Relatie met bestaande agents

Dit document beschrijft de *strategische denk-kant* — het team dat concepten uitwerkt, documenten schrijft, en het grotere geheel bewaakt. Het is complementair aan engineering-agents (die apps bouwen, visualisaties coderen, data verwerken).

De interface tussen de twee werelden is de **Vertaler-modus**: die produceert specificaties die engineering-agents kunnen oppakken, en interpreteert engineering-output (een werkende visualisatie, een data-structuur) terug naar strategische betekenis.

De gedeelde kennislaag moet voor beide werelden toegankelijk zijn — de engineering-agents moeten weten wat "bezettingsstroming" betekent als ze het in een data-model moeten verwerken, en de strategische agents moeten weten welke technische beperkingen er zijn.

---

## 7. Open vragen voor het ontwerp in Claude Code

- **Modi als skills of als prompting-strategie?** Zijn de vier modi aparte skills die expliciet worden aangeroepen, of zijn het onderdelen van één agent die via context-signalen schakelt?
- **Kennislaag als bestanden of als database?** Leven de kennisartefacten als markdown-bestanden in de repo, of is er een meer gestructureerde opslag nodig?
- **Hoe triggert modus-wisseling?** Expliciet door Esther ("laten we dit vastleggen"), door de agent ("dit concept is scherp genoeg, zal ik het vastleggen?"), of automatisch op basis van signalen?
- **Hoe verhoudt dit team zich tot de bestaande compound engineering plugin?** Waar zit de grens, en hoe communiceren ze?
- **Hoe escaleert de kennislaag?** Het framework is nu ~1000 regels. Met werkpakketten, inzichtenlogs, en conceptnotities groeit dat. Wat is het maximum dat effectief als context meegegeven kan worden?

---

*Dit document is een visie, geen specificatie. De vertaling naar concrete agent-architectuur gebeurt in Claude Code, waar de bestaande structuur en beperkingen het ontwerp mede bepalen.*
