# AI Exposure of the Cyprus Labour Market

This document contains structured data on Cyprus occupations sourced from HRDA, Eurostat, and other EU/Cyprus data providers, each scored for AI exposure on a 0-10 scale by an LLM. Use this data to analyse, question, and discuss how AI will reshape the Cyprus labour market.

GitHub: https://github.com/alezenonos/jobscy

## Scoring methodology

Each occupation was scored on a single AI Exposure axis from 0 to 10, measuring how much AI will reshape that occupation. The score considers both direct automation (AI doing the work) and indirect effects (AI making workers so productive that fewer are needed).

A key heuristic: if the job can be done entirely from a home office on a computer — writing, coding, analyzing, communicating — then AI exposure is inherently high (7+), because AI capabilities in digital domains are advancing rapidly. Conversely, jobs requiring physical presence, manual skill, or real-time human interaction have a natural barrier.

Calibration anchors:
- 0-1 Minimal: agricultural labourers, construction labourers, commercial divers
- 2-3 Low: electricians, plumbers, firefighters, building trades workers
- 4-5 Moderate: health associate professionals, police officers, personal care workers
- 6-7 High: teaching professionals, managers, business administration professionals
- 8-9 Very high: ICT professionals, legal professionals, business/admin associate professionals
- 10 Maximum: general clerks, numerical recording clerks, data entry operators

## Aggregate statistics

- Total occupations: 39
- Total jobs: 572,100 (572K)
- Total annual wages: €10.4B
- Job-weighted average AI exposure: 4.8/10

### Breakdown by exposure tier

| Tier | Occupations | Jobs | % of jobs | Wages | % of wages | Avg pay |
|------|-------------|------|-----------|-------|------------|---------|
| Minimal (0-1) | 5 | 117K | 20.5% | €1.4B | 13.7% | €12,126 |
| Low (2-3) | 10 | 143K | 25.0% | €2.1B | 20.3% | €14,771 |
| Moderate (4-5) | 7 | 77K | 13.5% | €1.3B | 12.4% | €16,713 |
| High (6-7) | 6 | 59K | 10.2% | €1.8B | 17.6% | €31,212 |
| Very high (8-10) | 11 | 176K | 30.7% | €3.7B | 36.0% | €21,331 |

### Average exposure by pay band (job-weighted)

| Pay band | Avg exposure | Jobs |
|----------|-------------|------|
| <€20K | 3.2 | 366K |
| €20-35K | 7.8 | 184K |
| €35-50K | 6.8 | 22K |

### Average exposure by education level (job-weighted)

| Education | Avg exposure | Jobs |
|-----------|-------------|------|
| Lower secondary | 1.6 | 170K |
| Vocational | 4.6 | 196K |
| Associate / Short-cycle | 8.4 | 74K |
| Bachelor's+ | 7.3 | 132K |

### Projected declining occupations

| Occupation | Exposure | Outlook | Jobs |
|-----------|----------|---------|------|

### Fastest-growing occupations (10%+ projected growth)

| Occupation | Exposure | Outlook | Jobs |
|-----------|----------|---------|------|

## All 39 occupations

Sorted by AI exposure (descending), then by number of jobs (descending).

### Exposure 10/10 (1 occupations, 22K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | General and keyboard clerks | €14,144 | 22K | ? | Vocational | This occupation group consists of routine information processing, data entry, and document preparation that is entirely digital and structured. Current AI and RPA technologies can already automate the vast majority of these tasks, making this group highly susceptible to total displacement or radical restructuring in the Cyprus and EU administrative sectors. |

### Exposure 9/10 (6 occupations, 95K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Business and administration associate professionals | €21,112 | 52K | ? | Associate | This group performs tasks that are almost entirely digital and information-based, such as financial record-keeping, sales support, and administrative coordination. Because their work product is fundamentally digital and involves routine data processing and communication, it is highly susceptible to both automation and significant productivity shifts driven by generative AI and LLMs. |
| 2 | Information and communications technology professionals | €26,728 | 14K | ? | Bachelor's+ | The work product of ICT professionals is entirely digital, consisting of code, architecture, and data analysis, which are domains where AI capabilities are advancing most rapidly. While these professionals are the primary adopters and creators of AI, the technology significantly automates core tasks like debugging, documentation, and routine coding, leading to massive productivity gains and structural shifts in the occupation. |
| 3 | Numerical and material recording clerks | €14,144 | 14K | ? | Vocational | This group performs routine information processing, data entry, and record-keeping tasks that are almost entirely digital and rule-based. In the Cyprus and EU context, these functions are being rapidly automated by AI-driven accounting software, automated inventory systems, and OCR technologies, leading to significant workforce restructuring. |
| 4 | Customer services clerks | €14,144 | 9K | ? | Vocational | The work product of customer service clerks is almost entirely digital or communication-based, making it highly susceptible to automation via Large Language Models and AI agents. In the Cyprus and EU markets, routine inquiries, booking services, and information provision are rapidly being transitioned to AI-driven interfaces, significantly reducing the need for human intervention in these clerical roles. |
| 5 | Information and communications technicians | €21,112 | 3K | ? | Associate | This group performs almost entirely digital work, including system support, network administration, and web development, which are core domains for AI automation and augmentation. While some hardware-related tasks require physical presence, the vast majority of their output is code or digital configuration, making them highly susceptible to massive productivity gains and role restructuring as AI tools take over routine technical tasks. |
| 6 | Other clerical support workers | €14,144 | 2K | ? | Vocational | This group consists of routine digital and paper-based tasks such as filing, mail processing, and personnel record maintenance, which are highly susceptible to automation through LLMs and RPA. In the Cyprus and EU context, the push for e-government and digital transformation is rapidly replacing these manual clerical functions with automated workflows and AI-driven document management systems. |

### Exposure 8/10 (4 occupations, 58K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Business and administration professionals | €26,728 | 22K | ? | Bachelor's+ | This group performs predominantly digital knowledge work involving data analysis, strategic planning, and complex communication, all of which are core strengths of generative AI. While high-level human judgment and stakeholder management in sectors like Cyprus's financial and shipping hubs provide some protection, the vast majority of their tasks are susceptible to significant automation and productivity restructuring. |
| 2 | Science and engineering professionals | €26,728 | 18K | ? | Bachelor's+ | This group performs predominantly digital knowledge work involving complex data analysis, design, and technical documentation, all of which are highly susceptible to AI-driven productivity gains and automation. While some roles require physical site visits or laboratory work (especially in Cyprus's construction and shipping sectors), the core output is digital, placing it on a steep trajectory for AI integration and restructuring. |
| 3 | Legal, social and cultural professionals | €26,728 | 13K | ? | Bachelor's+ | This group consists of highly digital and knowledge-intensive roles such as lawyers, social scientists, and writers, whose core tasks involve processing, analyzing, and generating complex text and data. While high-level human judgment and cultural nuance remain critical, AI is rapidly automating legal research, document drafting, and content creation, significantly increasing productivity and restructuring traditional workflows. |
| 4 | Legal, social, cultural and related associate professionals | €21,112 | 6K | ? | Associate | The work product of this group is almost entirely digital and information-based, involving legal research, social assistance documentation, and cultural content creation. While some roles require interpersonal empathy, the core tasks of drafting, analyzing, and organizing information are highly susceptible to AI-driven automation and productivity gains. |

### Exposure 7/10 (5 occupations, 53K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Teaching professionals | €26,728 | 26K | ? | Bachelor's+ | Teaching professionals are highly exposed because their core tasks—lesson planning, content creation, and assessment—are increasingly automated by generative AI. While the physical presence and social-emotional guidance required in Cyprus/EU classrooms provide a buffer, the digital nature of educational materials and administrative duties makes the profession ripe for significant AI-driven restructuring and productivity gains. |
| 2 | Science and engineering associate professionals | €21,112 | 10K | ? | Associate | These roles involve a high degree of technical data analysis, CAD design, and laboratory reporting which are increasingly being automated or enhanced by AI-driven simulation and diagnostic tools. While some tasks require physical presence in labs or on-site inspections in sectors like Cyprus's construction and shipping industries, the core work product is digital and highly susceptible to AI-driven productivity gains. |
| 3 | Production and specialised services managers | €40,830 | 8K | ? | Bachelor's+ | These roles involve high-level knowledge work, strategic planning, and resource allocation, which are increasingly augmented by AI-driven analytics and forecasting tools. While the need for human leadership, physical site oversight, and complex stakeholder negotiation in sectors like Cyprus's shipping and construction provides a buffer, the core administrative and analytical functions are highly susceptible to AI-driven productivity gains. |
| 4 | Administrative and commercial managers | €40,830 | 6K | ? | Bachelor's+ | These roles involve high-level knowledge work, strategic planning, and digital communication, all of which are highly susceptible to AI-driven productivity gains and data-driven decision-making. While the need for human leadership, negotiation, and complex stakeholder management in the Cyprus/EU corporate and public sectors provides a buffer, the core tasks of reporting, resource allocation, and administrative oversight are increasingly being automated or augmented by AI. |
| 5 | Chief executives, senior officials and legislators | €40,830 | 3K | ? | Bachelor's+ | This group performs high-level knowledge work involving strategic analysis, policy formulation, and complex communication, all of which are increasingly augmented by AI-driven data insights. While the core functions of leadership, ethical judgment, and political negotiation require human presence and accountability, the digital nature of their information processing and decision-support systems makes them highly exposed to AI restructuring. |

### Exposure 6/10 (1 occupations, 6K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Hospitality, retail and other services managers | €40,830 | 6K | ? | Bachelor's+ | This role involves a significant amount of administrative and strategic knowledge work—such as inventory management, financial planning, and marketing—which is highly susceptible to AI optimization. However, the requirement for physical presence, real-time staff supervision, and high-touch customer service in the Cyprus tourism and retail sectors provides a buffer against full automation. |

### Exposure 5/10 (1 occupations, 17K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Health professionals | €26,728 | 17K | ? | Bachelor's+ | Health professionals perform a mix of high-level cognitive tasks, such as diagnostics and treatment planning, which are highly exposed to AI assistance, and physical, hands-on clinical care that requires human presence. While AI will significantly enhance medical imaging, data analysis, and administrative efficiency in the EU/Cyprus healthcare systems, the legal responsibility and the necessity for physical patient interaction provide a substantial buffer against full automation. |

### Exposure 4/10 (6 occupations, 61K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Sales workers | €13,395 | 35K | ? | Vocational | While AI is rapidly automating digital sales, e-commerce, and customer analytics, a large portion of this group in Cyprus and the EU involves physical retail and face-to-face interaction. The core tasks of stocking shelves, handling physical goods, and providing in-person customer service in tourism-heavy economies provide a significant buffer against full AI displacement. |
| 2 | Protective services workers | €13,395 | 11K | ? | Vocational | While core duties like firefighting, policing, and physical security require real-time human presence and physical intervention, AI is increasingly used for surveillance, risk assessment, and report generation. In the Cyprus/EU context, the integration of smart city technologies and AI-driven monitoring enhances productivity but cannot replace the essential physical response and human judgment required in unpredictable public safety situations. |
| 3 | Personal care workers | €13,395 | 7K | ? | Vocational | The core duties involve physical assistance, emotional support, and real-time human interaction in healthcare and domestic settings, which are highly resistant to AI. However, exposure is moderate because AI is increasingly used for monitoring patient health, managing medication schedules, and automating the significant administrative and reporting requirements prevalent in the EU healthcare sector. |
| 4 | Health associate professionals | €21,112 | 3K | ? | Associate | This group involves a significant amount of physical interaction, clinical procedures, and patient care that cannot be digitized. While AI will heavily assist in diagnostic support, medical imaging analysis, and administrative record-keeping, the core requirement for human presence and manual dexterity in a clinical setting provides a substantial buffer against full automation. |
| 5 | Stationary plant and machine operators | €13,998 | 3K | ? | Lower sec. | While these roles involve physical machinery, the work is increasingly centered on monitoring digital control systems and optimizing processes, which are highly susceptible to AI-driven predictive maintenance and automated adjustments. However, the requirement for physical presence to handle mechanical failures, perform manual overrides, and conduct onsite inspections in industrial environments provides a significant buffer against full automation. |
| 6 | Handicraft and printing workers | €17,264 | 1K | ? | Vocational | This group combines physical craftsmanship with digital printing processes; while traditional handicraft remains low-exposure due to manual dexterity and physical materials, the printing sector is highly digitized and susceptible to AI-driven automation in layout and prepress. In the Cyprus/EU context, the shift toward digital manufacturing and automated printing offsets the more resilient, artisanal nature of traditional craft work. |

### Exposure 3/10 (4 occupations, 84K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Personal service workers | €13,395 | 33K | ? | Vocational | This group includes travel attendants, cooks, and hairdressers, whose core duties require physical presence, manual dexterity, and real-time human interaction. While AI may streamline peripheral tasks like booking, inventory management, or menu planning, the fundamental service delivery remains resistant to automation due to the physical and sensory nature of the work. |
| 2 | Assemblers | €13,998 | 23K | ? | Lower sec. | Assemblers perform physical tasks in manufacturing environments that require manual dexterity and the handling of physical components, which provides a natural barrier to current AI capabilities. While AI-driven robotics and computer vision are advancing in factory settings, the core work remains physical; AI exposure is primarily limited to peripheral tasks like inventory tracking, quality control monitoring, and workflow optimization. |
| 3 | Drivers and mobile plant operators | €13,998 | 20K | ? | Lower sec. | The core tasks involve physical operation of vehicles and machinery in unpredictable real-world environments, which provides a natural barrier to current AI capabilities. While autonomous driving technology and AI-driven logistics optimization are advancing, the need for human oversight, manual loading/unloading, and navigating complex Mediterranean urban infrastructure keeps exposure low to moderate. |
| 4 | Metal, machinery and related trades workers | €17,264 | 9K | ? | Vocational | The core tasks of this group involve physical manipulation of materials, machinery maintenance, and manual precision in non-standardized environments, which are highly resistant to AI. While AI can optimize predictive maintenance and diagnostic software used by these workers, the physical execution of repairs and metalwork remains a human-centric requirement in the Cyprus and EU industrial sectors. |

### Exposure 2/10 (6 occupations, 59K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Building and related trades workers, excluding electricians | €17,264 | 25K | ? | Vocational | The core tasks of building trades workers involve physical labor, manual dexterity, and the use of tools in unpredictable, non-routine physical environments. While AI may optimize project management, logistics, or architectural planning at a higher level, the actual execution of construction and maintenance remains insulated from digital automation. |
| 2 | Electrical and electronic trades workers | €17,264 | 8K | ? | Vocational | The core duties involve physical installation, maintenance, and repair of electrical systems and electronic equipment in diverse, unpredictable physical environments. While AI may assist with diagnostic software or administrative scheduling, the manual dexterity and on-site presence required for wiring and hardware manipulation provide a strong barrier to automation. |
| 3 | Market-oriented skilled forestry, fishery and hunting workers | €13,374 | 7K | ? | Vocational | The core tasks of this occupation group involve physical labor, manual dexterity, and real-time navigation of unpredictable natural environments like forests and seas. While AI may assist in peripheral areas such as satellite-based resource monitoring or administrative record-keeping, the fundamental work of harvesting, planting, and catching remains resistant to digital automation. |
| 4 | Market-oriented skilled agricultural workers | €13,374 | 7K | ? | Vocational | The core tasks involve physical labor, manual dexterity, and real-time management of biological systems in unpredictable outdoor environments, which are highly resistant to AI. While AI can optimize irrigation, pest control, and yield forecasting via precision agriculture, the fundamental work remains hands-on and requires a physical presence on the land. |
| 5 | Food preparation assistants | €12,126 | 7K | ? | Lower sec. | The core tasks of food preparation assistants involve physical manual labor, such as cleaning, peeling, and chopping ingredients in a fast-paced kitchen environment. While AI might optimize inventory management or scheduling at a managerial level, the physical nature of the work and the need for real-time sensory feedback provide a strong barrier against AI automation. |
| 6 | Food processing, wood working, garment and other craft and related trades workers | €17,264 | 5K | ? | Vocational | The core tasks of these trades involve physical manipulation of materials, manual dexterity, and sensory judgment in physical environments like kitchens, workshops, and factories. While AI may optimize supply chains or provide recipe/design suggestions, the fundamental work of cutting, sewing, baking, and crafting remains resistant to digital automation. |

### Exposure 1/10 (5 occupations, 117K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Street and related sales and service workers | €12,126 | 62K | ? | Lower sec. | This occupation group involves physical presence in public spaces for tasks like street vending, door-to-door sales, and providing services like shoe shining or car window cleaning. The work is fundamentally manual, interpersonal, and takes place in unpredictable outdoor environments where AI and robotics currently have negligible impact. |
| 2 | Cleaners and helpers | €12,126 | 37K | ? | Lower sec. | The core tasks of cleaners and helpers are entirely physical, requiring manual dexterity and movement within unpredictable physical environments like hotels, offices, and private homes. While AI might marginally improve scheduling or inventory management at a supervisory level, the fundamental work product cannot be digitized or automated without advanced robotics that are currently cost-prohibitive and technically immature for these settings. |
| 3 | Labourers in mining, construction, manufacturing and transport | €12,126 | 9K | ? | Lower sec. | The core tasks of these occupations involve manual labor, physical strength, and the use of hand tools in unpredictable physical environments like construction sites and mines. AI has virtually no direct impact on these physical activities, and the work cannot be digitized or performed remotely. |
| 4 | Agricultural, forestry and fishery labourers | €12,126 | 5K | ? | Lower sec. | The core tasks of this group involve manual physical labor in unpredictable outdoor environments, such as harvesting, digging, and hauling, which are highly resistant to AI. While automation and robotics may impact large-scale industrial farming, the specific tasks of 'labourers' in the Cyprus and EU context remain fundamentally physical and non-digital. |
| 5 | Refuse workers and other elementary workers | €12,126 | 4K | ? | Lower sec. | The core tasks of refuse collection and elementary labor are almost entirely physical, manual, and conducted in unpredictable outdoor environments. While AI might optimize collection routes at a management level, it has virtually no impact on the physical labor required for these roles in the current Cyprus and EU infrastructure. |
