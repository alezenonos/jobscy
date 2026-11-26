# AI Exposure of the Cyprus Labour Market

This document contains structured data on 39 Cyprus occupation groups (ISCO-08 2-digit). Employment comes from the Eurostat Labour Force Survey (LFSA_EGAI2D) and pay from the Eurostat Structure of Earnings Survey (1-digit level, so groups in the same major group share a pay figure). Each group is scored for AI exposure on a 0-10 scale and for 10-year growth outlook by an LLM; these scores are estimates, not official forecasts. Use this data to analyse, question, and discuss how AI will reshape the Cyprus labour market.

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
- Total jobs: 499,000 (499K)
- Total annual wages: €14.5B
- Job-weighted average AI exposure: 5.1/10

### Breakdown by exposure tier

| Tier | Occupations | Jobs | % of jobs | Wages | % of wages | Avg pay |
|------|-------------|------|-----------|-------|------------|---------|
| Minimal (0-1) | 3 | 52K | 10.3% | €0.8B | 5.7% | €15,989 |
| Low (2-3) | 13 | 136K | 27.2% | €2.6B | 18.2% | €19,445 |
| Moderate (4-5) | 7 | 76K | 15.3% | €2.0B | 13.8% | €26,175 |
| High (6-7) | 10 | 97K | 19.5% | €4.6B | 32.1% | €47,813 |
| Very high (8-10) | 6 | 138K | 27.8% | €4.4B | 30.2% | €31,509 |

### Average exposure by pay band (job-weighted)

| Pay band | Avg exposure | Jobs |
|----------|-------------|------|
| <€20K | 2.7 | 158K |
| €20-35K | 5.9 | 198K |
| €35-50K | 6.9 | 120K |
| €50-75K | 6.4 | 22K |

### Average exposure by education level (job-weighted)

| Education | Avg exposure | Jobs |
|-----------|-------------|------|
| Lower secondary | 1.8 | 91K |
| Vocational | 4.6 | 190K |
| Associate / Short-cycle | 7.2 | 76K |
| Bachelor's+ | 6.8 | 143K |

### Projected declining occupations

| Occupation | Exposure | Outlook | Jobs |
|-----------|----------|---------|------|
| Handicraft and printing workers | 4/10 | -17% | 1K |
| Market-oriented skilled agricultural workers | 2/10 | -11% | 8K |
| Agricultural, forestry and fishery labourers | 1/10 | -10% | 4K |
| Customer services clerks | 8/10 | -7% | 10K |
| Refuse workers and other elementary workers | 2/10 | -7% | 4K |
| General and keyboard clerks | 9/10 | -6% | 22K |
| Numerical and material recording clerks | 9/10 | -6% | 15K |
| Labourers in mining, construction, manufacturing and transport | 2/10 | -6% | 10K |
| Assemblers | 3/10 | -5% | 200 |
| Sales workers | 5/10 | -4% | 32K |
| Other clerical support workers | 7/10 | -3% | 2K |
| Market-oriented skilled forestry, fishery and hunting workers | 2/10 | -3% | 500 |
| Street and related sales and service workers | 2/10 | -3% | 100 |

### Fastest-growing occupations (10%+ projected growth)

| Occupation | Exposure | Outlook | Jobs |
|-----------|----------|---------|------|
| Information and communications technology professionals | 9/10 | +25% | 14K |
| Business and administration professionals | 8/10 | +18% | 25K |
| Health professionals | 5/10 | +10% | 18K |
| Health associate professionals | 5/10 | +10% | 3K |
| Personal care workers | 4/10 | +10% | 8K |

## All 39 occupations

Sorted by AI exposure (descending), then by number of jobs (descending).

### Exposure 9/10 (3 occupations, 51K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | General and keyboard clerks | €20,893 | 22K | -6% | Vocational | Most duties involve digital, routine information processing—such as entering data, preparing documents, maintaining records, and handling correspondence—where AI and workflow automation can both perform tasks and reduce staffing needs. Some roles include coordination or in-person service that still requires human judgment, but this is unlikely to offset the substantial potential for restructuring. |
| 2 | Numerical and material recording clerks | €20,893 | 15K | -6% | Vocational | Most core duties—entering and checking figures, maintaining stock or production records, processing documents, and updating databases—are routine information-processing tasks that AI and automated systems can increasingly handle. Some roles still involve physical stock checks or coordination with workers and suppliers, but these tasks are a limited barrier to substantial automation and productivity gains. |
| 3 | Information and communications technology professionals | €41,771 | 14K | +25% | Bachelor's+ | ICT professionals do most of their core work digitally, including software development, systems analysis, database design, testing, and technical documentation—areas where AI is advancing rapidly and can automate or accelerate substantial tasks. Human expertise remains important for architecture, security, complex requirements, and accountability, but AI-driven productivity is likely to significantly reshape staffing and workflows across Cyprus and the EU. |

### Exposure 8/10 (3 occupations, 88K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Business and administration associate professionals | €33,063 | 53K | +5% | Associate | Much of the group’s work involves processing information, preparing documents, analysing data, coordinating transactions, and communicating digitally—tasks where AI can automate substantial work or increase worker productivity. Client-facing duties, negotiation, regulatory judgment, and local context provide some resilience, but are unlikely to prevent major restructuring across the group. |
| 2 | Business and administration professionals | €41,771 | 25K | +18% | Bachelor's+ | Most business and administration professionals do knowledge work using digital information, so AI can automate or accelerate substantial tasks such as analysis, reporting, document preparation, and forecasting. Human judgment, accountability, regulatory requirements, and client or stakeholder relationships remain important, but are unlikely to prevent major restructuring across these roles. |
| 3 | Customer services clerks | €20,893 | 10K | -7% | Vocational | Much of the work involves handling inquiries, processing requests, and updating records through digital systems—tasks increasingly supported or automated by chatbots, voice AI, and customer-service software. Human judgment and empathy remain important for complex or sensitive cases, and some roles involve in-person contact, but AI is likely to substantially reshape staffing and daily workflows. |

### Exposure 7/10 (5 occupations, 46K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Science and engineering professionals | €41,771 | 20K | +8% | Bachelor's+ | Many core tasks—modelling, analysis, research synthesis, technical documentation, and design—are digital and increasingly AI-assisted, potentially raising productivity and reducing demand for some routine analytical work. However, experiments, fieldwork, site inspections, physical prototyping, and safety-critical engineering judgment still require human expertise and presence, so exposure varies substantially across the group. |
| 2 | Legal, social and cultural professionals | €41,771 | 16K | +4% | Bachelor's+ | Much of the work involves digital research, writing, analysis, documentation, and communication, where AI can automate tasks and substantially increase productivity—especially in legal and policy-related roles. However, the group also includes occupations requiring human judgment, trust, direct social interaction, or creative and cultural work, which limits how much of the core job can be automated. |
| 3 | Administrative and commercial managers | €73,564 | 6K | +2% | Bachelor's+ | Administrative and commercial managers spend substantial time on digital work such as planning, reporting, analysis, communications, and coordinating business processes, where AI can automate tasks and increase the productivity of teams. Their roles also depend on leadership, negotiation, accountability, and context-sensitive decisions, which limits full automation but is likely to reshape how the work is done. |
| 4 | Chief executives, senior officials and legislators | €73,564 | 2K | +5% | Bachelor's+ | AI can substantially assist with analysis, briefing, communications, planning and routine decision support, making senior leaders more productive and potentially changing staffing needs. However, the role still depends heavily on accountable judgment, negotiation, political or organisational relationships, and leadership in real-world settings, which limits direct automation. |
| 5 | Other clerical support workers | €20,893 | 2K | -3% | Vocational | Many duties in this group involve routine information processing—such as filing, coding, proofreading, personnel records and copying—that AI and digital systems can automate or speed up substantially. Mail handling and other in-person or physical tasks are less directly exposed, so the group’s overall exposure is below that of fully digital clerical occupations. |

### Exposure 6/10 (5 occupations, 51K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Teaching professionals | €41,771 | 27K | +5% | Bachelor's+ | AI can substantially assist teaching professionals with lesson preparation, learning materials, routine assessment, feedback, and administrative tasks, potentially increasing productivity and changing staffing needs. However, teaching still depends heavily on in-person interaction, classroom management, adapting to learners, and professional judgment, which limits direct automation. |
| 2 | Production and specialised services managers | €73,564 | 10K | +6% | Bachelor's+ | AI can substantially assist with planning, forecasting, reporting, and resource allocation, making managers more productive and potentially reducing some administrative workload. However, this broad group includes roles overseeing physical production and specialised services that require on-site judgment, staff coordination, and accountability, limiting direct automation. |
| 3 | Legal, social, cultural and related associate professionals | €33,063 | 6K | +6% | Associate | AI can substantially assist with research, drafting, documentation, and routine administrative work across this group, particularly in legal support and cultural-content tasks. However, many roles depend on direct human interaction, practical activities, performance, or contextual judgment, limiting automation of their core work. |
| 4 | Hospitality, retail and other services managers | €73,564 | 5K | +6% | Bachelor's+ | AI can substantially assist with forecasting, pricing, scheduling, inventory, reporting, and customer communications, making managers more productive and potentially reducing administrative staffing needs. However, hospitality and retail managers still coordinate on-site operations, handle staff and customer issues, and make context-dependent decisions in physical workplaces, limiting automation of the core role. |
| 5 | Information and communications technicians | €33,063 | 3K | +9% | Associate | AI can substantially automate or accelerate routine help-desk responses, monitoring, documentation, and basic network or system diagnostics, reducing time needed for many information-processing tasks. However, the group also includes hands-on installation, equipment maintenance, and contextual troubleshooting that often require physical presence and human interaction, limiting overall exposure. |

### Exposure 5/10 (4 occupations, 62K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Sales workers | €17,476 | 32K | -4% | Vocational | AI can automate or streamline product recommendations, routine customer enquiries, transaction processing, and some sales administration, while digital tools may let fewer workers handle more sales activity. However, many sales workers in Cyprus and the EU serve customers in person, demonstrate products, handle goods, and respond to unpredictable needs, limiting automation of the core work. |
| 2 | Health professionals | €41,771 | 18K | +10% | Bachelor's+ | AI can significantly assist health professionals with documentation, image interpretation, clinical decision support, and treatment planning, potentially increasing productivity and changing workflows. However, much of the work involves physical examination, procedures, and direct patient interaction that require human presence and judgment, limiting automation of core duties. |
| 3 | Science and engineering associate professionals | €33,063 | 10K | +7% | Associate | AI can significantly assist with technical documentation, data analysis, design support, and monitoring, especially in engineering and laboratory roles. However, many duties involve operating or calibrating equipment, conducting tests and inspections, and responding to physical-world conditions, which limits automation across this diverse group. |
| 4 | Health associate professionals | €33,063 | 3K | +10% | Associate | Health associate professionals may use AI for documentation, triage support, image or laboratory analysis, and treatment planning, making parts of their information-processing work more efficient. However, many core duties involve hands-on procedures, patient care, and real-time interaction that require physical presence and human judgment, limiting direct automation. |

### Exposure 4/10 (3 occupations, 14K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Personal care workers | €17,476 | 8K | +10% | Vocational | Personal care workers rely on hands-on assistance, physical presence, and real-time human interaction, which are difficult for AI to replace. AI may help with care documentation, scheduling, or monitoring, but these are peripheral to the core work. |
| 2 | Stationary plant and machine operators | €23,242 | 5K | +2% | Lower sec. | The work is anchored in operating and monitoring physical plant, responding to equipment conditions, and following safety procedures, so it cannot be done entirely on a computer. AI can improve process control, fault detection, and predictive maintenance, potentially reducing staffing needs, but workers remain important for on-site oversight and intervention. |
| 3 | Handicraft and printing workers | €21,235 | 1K | -17% | Vocational | Most work involves hands-on craft production, operating or tending printing equipment, and handling physical materials, which limits direct AI substitution. AI can still reshape digital design, prepress, job planning, and routine production workflows, making exposure meaningful but uneven across the group. |

### Exposure 3/10 (7 occupations, 86K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Personal service workers | €17,476 | 35K | +8% | Vocational | Personal service workers typically provide hands-on services and interact directly with customers in settings such as restaurants, hotels, salons, and tourist attractions. AI may help with bookings, translation, recommendations, and routine administration, but the core work generally requires physical presence, practical skill, and real-time human interaction. |
| 2 | Drivers and mobile plant operators | €23,242 | 20K | +4% | Lower sec. | The core work involves physically operating vehicles or mobile machinery in changing real-world conditions, where safety, practical judgment, and human presence limit near-term automation. AI can improve routing, monitoring, and scheduling, while autonomous systems may reshape some roles over time, but adoption is constrained by infrastructure, regulation, and the diversity of operating environments. |
| 3 | Protective services workers | €17,476 | 9K | +2% | Vocational | Protective services work is primarily performed in person and often involves physical intervention, unpredictable situations, and real-time judgment, which limits direct automation. AI may assist with surveillance, dispatch, risk assessment, and report writing, but these are supporting tasks rather than the core duties. |
| 4 | Metal, machinery and related trades workers | €21,235 | 9K | +4% | Vocational | The core work involves hands-on fabrication, machining, installation, and repair in physical environments, where variable conditions and skilled manual tasks limit direct AI automation. AI may assist with diagnostics, planning, and automated machinery, but these tools are more likely to change workflows than replace most workers. |
| 5 | Electrical and electronic trades workers | €21,235 | 8K | +5% | Vocational | The core work involves installing, maintaining, and repairing electrical or electronic equipment in physical environments, requiring hands-on skill, safety judgment, and often on-site presence. AI can assist with diagnostics, technical documentation, and work planning, but is unlikely to replace much of the practical work in the near term. |
| 6 | Food processing, wood working, garment and other craft and related trades workers | €21,235 | 5K | +1% | Vocational | Most work involves hands-on processing, machine operation, finishing, or craft skills in physical workplaces, which limits direct automation by AI. AI may improve production planning, pattern design, quality inspection, and machine control, but these tools are more likely to support workers than replace the core manual tasks. |
| 7 | Assemblers | €23,242 | 200 | -5% | Lower sec. | Assemblers mainly perform hands-on work with parts, tools, and machinery in physical production settings, which limits the direct impact of software-based AI. AI-enabled robotics and inspection systems may automate or support repetitive, standardized assembly tasks, but deployment depends on the production process and does not remove the need for physical operations and oversight. |

### Exposure 2/10 (6 occupations, 50K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Building and related trades workers, excluding electricians | €21,235 | 26K | +5% | Vocational | The core work involves hands-on construction, repair, and finishing in changing physical environments, requiring manual skill and on-site judgment that AI cannot readily replace. AI may assist with plans, measurements, scheduling, and documentation, but these are peripheral to the work and are unlikely to greatly reduce the need for workers. |
| 2 | Labourers in mining, construction, manufacturing and transport | €15,989 | 10K | -6% | Lower sec. | The core work is physical and location-bound, involving carrying, loading, cleaning, and assisting with construction, manufacturing, or transport tasks that require human presence and handling in changing environments. AI may affect scheduling and coordination, while robotics and automated equipment could reduce demand for some routine tasks over time, but these are indirect or uneven effects rather than widespread automation of the group’s core work. |
| 3 | Market-oriented skilled agricultural workers | €16,413 | 8K | -11% | Vocational | The core work involves hands-on crop or livestock production, operating equipment, and responding to changing physical conditions, which limits direct AI automation. AI may assist with planning, monitoring, and farm records, but these are supporting tasks and are unlikely to displace the need for workers in the field. |
| 4 | Refuse workers and other elementary workers | €15,989 | 4K | -7% | Lower sec. | The work is primarily physical and takes place in real-world settings, involving tasks such as collecting refuse, street cleaning, and other manual duties that require human presence. AI may assist with route planning, scheduling, or monitoring, but these are peripheral to the core work and automation faces practical challenges in varied environments. |
| 5 | Market-oriented skilled forestry, fishery and hunting workers | €16,413 | 500 | -3% | Vocational | The core work is physical and takes place outdoors or aboard vessels, involving hands-on forestry, fishing, or hunting tasks in variable environments. AI may assist with planning, monitoring, navigation, and paperwork, but is unlikely to automate much of the work itself. |
| 6 | Street and related sales and service workers | €15,989 | 100 | -3% | Lower sec. | The work is mainly performed in person and involves selling or providing services in public settings, often with hands-on tasks and real-time customer interaction. AI may assist with payments, stock management, or promotion, but these are peripheral to the core work. |

### Exposure 1/10 (3 occupations, 52K jobs)

| # | Occupation | Pay | Jobs | Outlook | Education | Rationale |
|---|-----------|-----|------|---------|-----------|-----------|
| 1 | Cleaners and helpers | €15,989 | 41K | +3% | Lower sec. | The core work involves physical cleaning in varied homes, offices, hotels, and other settings, requiring on-site presence and hands-on effort. AI may assist with scheduling or coordination, while cleaning robots could automate some repetitive tasks, but these are limited substitutes for the broader duties of cleaners and helpers. |
| 2 | Food preparation assistants | €15,989 | 7K | +6% | Lower sec. | Food preparation assistants mainly perform hands-on tasks such as washing, peeling, portioning, and assembling food in busy kitchens. AI may assist with ordering or scheduling, but the core work requires physical presence and dexterity, and kitchen automation is limited. |
| 3 | Agricultural, forestry and fishery labourers | €15,989 | 4K | -10% | Lower sec. | The core work is physical and typically performed outdoors or in other hands-on settings, such as planting, harvesting, tending animals, and maintaining forests or fishing operations. AI may assist indirectly through planning, monitoring, or machinery, but it is unlikely to replace much of the labourers’ on-site manual work in the near term. |
