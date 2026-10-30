### Civic AI Platform: Design System & UI Specification

This design document establishes the visual design language, component architecture, design tokens, and user experience patterns for the  **Civic AI Platform**  ( *"From Complaints to Action"* ). Synthesized from municipal asset management platforms, urban sanitation operating systems, and field-tested citizen reporting interfaces, this specification provides a unified framework for transforming scattered municipal complaints into prioritized, explainable, and trackable civic action.

#### 1\. System Vision & Design Philosophy

Civic technology operates at the intersection of public trust, operational speed, and field accessibility. The Civic AI Platform serves two distinct user groups with contrasting operational environments: citizens reporting hazards on mobile devices under outdoor conditions, and municipal officers making rapid dispatch decisions on multi-screen desktop dashboards.  
To bridge these needs without introducing interface friction or cognitive overload, the design system is governed by four core design principles:

* **Field-First Accessibility** : Interfaces for citizens and field crews prioritize touch targets (minimum 48px height), high visual contrast, and simplified single-column flows that function seamlessly on phone-sized viewports.  
* **Explainable & Transparent AI** : Every AI prediction—from priority scoring to duplicate linking—presents its underlying reasoning in plain language. AI suggestions are framed as assistive recommendations rather than opaque automated decisions, maintaining an explicit "human-in-the-loop" model.  
* **Contextual Elevation & Layering** : Complex spatial and tabular data are organized using floating card stacks and modal overlays over map canvases, preserving geographic context while giving focus to immediate tasks.  
* **Restraint & Role-Based Clarity** : Information access is strictly scoped to administrative jurisdiction (from city-wide command centers down to division, zone, and ward levels). A role is defined as much by what it cannot see as what it can, building institutional trust and auditable accountability.

#### 2\. Visual Design Language & Design Tokens

The visual language balances authoritative municipal trust with approachable, modern software aesthetics. It pairs deep emerald-teals and dark slate text with soft mint surfaces and clear, color-coded priority badges.

##### 2.1 Color System & Tokens

The color system utilizes custom color tokens to ensure consistency across web, iOS, and Android client applications.

###### *Primary Brand & Surface Palette*

The primary palette establishes brand identity while maintaining high visual contrast for outdoor mobile readability.  
Token Name,HEX Code,Design Role & Usage  
color-brand-teal-dark,\#0B6B61,"Primary action buttons (""Send report"", ""Assign""), active filter pills, top status banners, completed timeline nodes."  
color-brand-teal-light,\#E1F2EF,"AI suggestion container backgrounds, active category chip fills, light surface highlights."  
color-brand-teal-hover,\#08544C,Hover and active states for primary actions.  
color-brand-teal-border,\#A8DADC,Soft outline borders for secondary action triggers and active input fields.

###### *Semantic Priority & Alert Palette*

Priority badges use soft, tinted background fills combined with saturated, high-contrast text colors to prevent visual fatigue while instantly signaling urgency levels.  
Priority Level,Fill HEX,Text / Border HEX,Visual Indicator & Usage  
High Priority / Hazard,\#FCE8E2,\#C53030,"Soft coral fill with deep rust red text. Used for immediate safety risks (e.g., open manholes, active flooding near schools)."  
Medium Priority,\#FEF3C7,\#B45309,"Soft gold fill with dark amber text. Used for infrastructure wear and non-immediate hazards (e.g., pothole clusters)."  
Low Priority / Routine,\#E6FFFA,\#0D9488,"Light mint fill with dark teal text. Used for routine municipal upkeep (e.g., broken streetlights, scheduled cleaning)."

###### *Neutral & Canvas Palette*

Neutral tones provide structural framing for card containers, map overlays, and typography.  
Token Name,HEX Code,Design Role & Usage  
color-neutral-slate-900,\#1E293B,"Primary headings, primary card titles, modal text (""What is the problem?"")."  
color-neutral-slate-600,\#64748B,"Secondary body text, timestamps, subtitle microcopy, inactive filter labels."  
color-neutral-slate-200,\#E2E8F0,"Card divider lines, input field borders, inactive chip outlines."  
color-surface-white,\#FFFFFF,"Floating card containers, active modal overlays, desktop panel backgrounds."  
color-surface-canvas,\#F8FAFC,Off-white background canvas for mobile tracking views and light card containers.  
color-map-canvas-bg,\#EAEFEA,Soft mint-gray base color for spatial vector map grids.

##### 2.2 Typography Scale & Hierarchy

The interface specifies a modern sans-serif typography stack ( *Inter* ,  *Plus Jakarta Sans* , or  *DM Sans* ) calibrated for legibility across varied screen densities.  
The table below outlines the font sizing, weight pairing, and element mapping across mobile and desktop viewports:  
Type Role,Font Size,Line Height,Weight,Element Application  
Display Header,24px (1.5rem),32px,Bold (700),"Main screen titles (""What is the problem?"", ""Blocked drain, school gate"")."  
Section Heading,18px (1.125rem),24px,SemiBold (600),"Modal headers, dashboard column titles (""Fix first"", ""Ward 12 reports"")."  
Card Subtitle,14px (0.875rem),20px,Medium (500),"Secondary item titles, active status labels (""Assigned to Drainage crew B"")."  
Body Regular,14px (0.875rem),20px,Regular (400),"AI action briefs, note callouts, citizen report descriptions."  
Caption / Microcopy,12px (0.75rem),16px,Regular (400),"Timestamps, synthetic data notices, AI disclaimer text."  
Badge / Button Text,12px / 14px,16px / 20px,Bold (700),"Priority badge labels, filter pill tags, CTA buttons (""Send report"", ""Assign"")."

##### 2.3 Geometry, Elevation & Border Radii

Components incorporate rounded geometry and soft drop shadows to distinguish floating controls from underlying map layers.

* **Pill Radius (**  **radius-pill: 9999px**  **)** : Used for category filter chips, priority status badges, and primary action buttons.  
* **Extra Large Radius (**  **radius-xl: 24px**  **)** : Applied to sliding bottom sheet modals and primary floating dashboard card stacks.  
* **Large Radius (**  **radius-lg: 16px**  **)** : Applied to inner content containers, timeline cards, and status banners.  
* **Medium Radius (**  **radius-md: 12px**  **)** : Applied to text input areas and AI suggestion banners.  
* **Subtle Elevation (**  **shadow-subtle**  **)** : 0px 2px 8px rgba(0, 0, 0, 0.04) for list items and input fields.  
* **Floating Elevation (**  **shadow-floating**  **)** : 0px 8px 24px rgba(0, 0, 0, 0.08) for overlay dashboard panels on map canvases.  
* **Modal Elevation (**  **shadow-modal**  **)** : 0px \-4px 32px rgba(0, 0, 0, 0.12) for mobile bottom sheet drawers.

#### 3\. Component Architecture & Interface Specifications

The component library divides into citizen-facing mobile viewports and official administrative command dashboards.

##### 3.1 Citizen Mobile Interface (Capture & Progress Tracking)

The mobile experience prioritizes fast, single-handed submission and transparent, real-time status tracking.

###### *Component Layout Structure*

The mobile layout overlays a sliding bottom-sheet modal over a full-screen location picker map:  
\+------------------------------------------+  
\|  \[ \< Map Preview / Pin Selector \]       \|  
\|  \[ (o) Use my location \]                 \|  
\+------------------------------------------+  
\|  \=== (Grab Handle Bar)                   \|  
\|  What is the problem?                    \|  
\|  \+------------------------------------+  \|  
\|  \| \[Thumb\] Drain overflowing...       \|  \|  
\|  \+------------------------------------+  \|  
\|  \+------------------------------------+  \|  
\|  \| AI Suggestion: Drainage (High)     \|  \|  
\|  \| 2 similar reports nearby. \[Why?\]   \|  \|  
\|  \+------------------------------------+  \|  
\|  ( Drainage ) ( Road damage ) ( Waste )  \|  
\|                                          \|  
\|  \+------------------------------------+  \|  
\|  \|           Send report              \|  \|  
\|  \+------------------------------------+  \|  
\|  Demo data. AI suggestions can be wrong. \|  
\|  \[ Report \]   \[ My reports \]   \[ Nearby \]\|  
\+------------------------------------------+

###### *Key Component Specifications:*

* **Sliding Bottom Sheet Modal** : Positioned over the map canvas with a top grab handle (\#CBD5E1, 36px width x 4px height) and 24px rounded top corners.  
* **Category Filter Chips** : Horizontal capsule pills (radius-pill). Active chips feature solid dark teal (\#0B6B61) with white text; inactive chips use white backgrounds with subtle gray outlines (\#E2E8F0).  
* **AI Suggestion Banner** : Light mint container (\#E1F2EF) displaying auto-detected categories (Drainage · High priority) and a direct link to plain-language AI explanation triggers ("Why?").  
* **Primary Action Button** : Full-width pill button (\#0B6B61), 52px height, bold centered text, providing immediate tactile response upon tap.  
* **Vertical Timeline Progress Tracker** : Visualizes report lifecycle steps using connected circular nodes:  
* *Completed Step* : Solid dark teal circle (\#0B6B61) with bold label and timestamp.  
* *Active Step* : Open dark teal ring (\#0B6B61, 2px stroke) highlighting current assignment.  
* *Upcoming Step* : Muted gray circle (\#CBD5E1) with regular gray text.

##### 3.2 Official Command Center (Desktop Dashboard)

The administrative dashboard provides a multi-panel view overlaying an interactive municipal map.

###### *Desktop Layout Structure*

The dashboard structure features floating control panels arranged over a vector map grid:  
\+-----------------------------------------------------------------------------------+  
\| ( Ward 12 reports ) \[ All open · 12 \] \[ High · 3 \] \[ Hotspots · 2 \]               \|  
\+----------------------------------+-------------------+----------------------------+  
\| Fix first                        \|                   \| Blocked drain, school gate \|  
\| \+------------------------------+ \|                   \| Brief: Overflowing drain...\|  
\| \| Blocked drain       \[ High \] \| \|    ( Hotspot )    \| \+------------------------+ \|  
\| \| 3 reports · near school      \| \|   (O)   (O)  (O)  \| \| Why High:              \| \|  
\| \+------------------------------+ \|     (O)    (O)    \| \| · Near school (+40)    \| \|  
\| \| Open manhole        \[ High \] \| \|                   \| \| · 3 linked reports (+20)\| \|  
\| \+------------------------------+ \|                   \| \+------------------------+ \|  
\| \| Pothole cluster   \[ Medium \] \| \|                   \| Duplicates: Linked \#1038   \|  
\| \+------------------------------+ \|                   \| \[ Crew select v \] \[Assign\] \|  
\|                                  \|                   \|----------------------------+  
\|                                  \|                   \| Insight: Waste bin reported\|  
\|                                  \|                   \| 5 times in 9 days...       \|  
\+----------------------------------+-------------------+----------------------------+

###### *Key Component Specifications:*

* **Floating Navigation Header** : Translucent floating header containing segmented pill buttons for ward selection and status filtering (All open, High, Hotspots).  
* **"Fix First" Queue Panel** : Left-hand sidebar displaying a prioritized list of issues. Each card features issue titles, context badges, and color-coded priority pills (High, Medium, Low).  
* **Map Canvas & Spatial Overlays** : Custom vector map styling using soft mint-gray backgrounds (\#EAEFEA), clear road geometries, and color-coded incident dots. Spatial clusters are outlined using dashed rust-red ellipses (\#C53030) with translucent fill (rgba(197, 48, 48, 0.12)).  
* **Detail & Dispatch Panel** : Right-hand card displaying detailed AI action briefs, automated duplicate detection controls, and inline dispatch dropdowns paired with primary action buttons.

#### 4\. AI-Driven Interaction Patterns

To foster human trust and prevent algorithmic opacity, the platform implements four specialized AI interface components:

##### 4.1 Explainable Prioritization Cards ("Why High?")

Priority scores are accompanied by an expandable or inline explanation card that details the exact scoring factors.  
\+-------------------------------------------------------+  
\| Why High                                              \|  
\| Near a school \+40 · 3 linked reports \+20              \|  
\| Water on road, photo confirms \+15 · Reported today \+5 \|  
\|                                                       \|  
\| AI can misread photos. An officer confirms.           \|  
\+-------------------------------------------------------+

* **Visual Style** : Container filled with soft slate gray (\#F8FAFC) or light mint (\#E1F2EF) with dark slate typography (\#1E293B).  
* **Additive Weight Breakdown** : Displays specific contextual rules (e.g., Near a school \+40, 3 linked reports \+20, Water on road, photo confirms \+15, Reported today \+5).  
* **Officer Disclaimer** : Explicit microcopy (AI can misread photos. An officer confirms.) reinforces officer authority over automated recommendations.

##### 4.2 Duplicate Detection & Linking Badges

When multiple citizens report the same issue, AI groups them into a single actionable record.

* **Visual Indicator** : Inline tag displaying match confidence percentages (e.g., Duplicates: Linked with \#1038, \#1040 (82% match)).  
* **Override Control** : Interactive action link (Not the same) enables officers to decouple false-positive matches instantly.

##### 4.3 Spatial Cluster & Hotspot Visualizers

Rather than displaying isolated pins, the platform highlights geographic concentrations of related problems (such as simultaneous drainage overflow, waterlogging, and road damage on one street).

* **Visual Overlay** : SVG dashed ellipse (\#C53030, 2px dashed line) with translucent rust fill (rgba(197, 48, 48, 0.12)).  
* **Cluster Label Tag** : Floating black capsule banner (\#1E293B) displaying hotspot summary text (e.g., MG Road hotspot \- 7 reports).

##### 4.4 Proactive Action Briefs & Insight Callouts

Unstructured citizen reports are summarized into concise 2-sentence briefs, accompanied by systemic pattern recommendations.

* **Action Brief Component** : Positioned prominently at the top of the issue detail panel, summarizing cause, location, and immediate operational needs.  
* **Systemic Insight Callout** : Positioned at the bottom of the dashboard, surfacing recurring trends (e.g., Insight: Waste bin at Market Gate was reported 5 times in 9 days. Consider a bigger bin or a daily pickup.).

#### 5\. Information Architecture & The 4-Stage Lifecycle

The platform models citizen reports through four distinct operational stages, as mapped below:  
\+-----------------------------------------------------------------------------------+  
\|                                REPORT LIFECYCLE                                   \|  
\+-------------------+-------------------+--------------------+----------------------+  
\| 1\. CAPTURE        \| 2\. UNDERSTAND     \| 3\. REVEAL          \| 4\. ACT               \|  
\| Mobile Submissions\| AI Pipeline       \| Spatial Insights   \| Dispatch & Track     \|  
\| • Text \+ Photo    \| • Category Tagging\| • Map Dashboard    \| • Work Orders        \|  
\| • GPS Location    \| • Priority Scoring\| • Hotspot Clusters \| • Crew Assignment    \|  
\| • Category Selector\| • Duplicate Check\| • Ward Filtering   \| • Citizen Timeline   \|  
\+-------------------+-------------------+--------------------+----------------------+

* **Stage 1: Capture** :  
* *Target Execution* : Under 60 seconds on mobile devices.  
* *Interface Elements* : Mobile photo uploader, automatic map pin locator, category selector chips (Drainage, Road damage, Waste, Streetlight), submit CTA.  
* **Stage 2: Understand** :  
* *Target Execution* : Automated background processing pipeline.  
* *Interface Elements* : AI category confidence tags, explainable score breakdown cards, duplicate report group links.  
* **Stage 3: Reveal** :  
* *Target Execution* : Real-time command center view for municipal officers.  
* *Interface Elements* : Interactive spatial map, "Fix First" priority queue, hotspot grouping overlays, systemic insight callouts.  
* **Stage 4: Act** :  
* *Target Execution* : Resolution dispatch and citizen transparency.  
* *Interface Elements* : Crew selection controls, status updates ("Received" → "Reviewed" → "Assigned" → "In progress" → "Fixed"), photo evidence confirmation.

#### 6\. Administrative Hierarchy & Access Control Architecture

Following proven urban management architectures, the platform enforces strict hierarchical scoping to prevent organizational clutter and data leaks across municipal zones.  
Administrative Tree:  
Country (National Level)  
└── State / Region  
    └── City / Municipality  
        └── Division  
            └── Zone  
                └── Ward (Field Level)

##### Role-Based Access Matrix

Access permissions are strictly bounded by node placement within the administrative tree:

* **Platform Administrator** : Operates at state or national level. Manages hierarchy trees, configures ward settings, and seeds global role templates. Restricted from daily ward operations to maintain clear audit logs.  
* **Regional / Division Administrator** : Operates at city or division level. Onboards operating teams, manages subtrees, and accesses aggregate compliance reports.  
* **Zone / Ward Manager** : Operates at specific zone or ward level. Runs day-to-day rosters, assigns incidents, manages maintenance routines, and reviews field evidence. Cannot alter the administrative hierarchy tree.  
* **Field Crew / Worker** : Operates on mobile field routes. Starts shifts with a single tap, completes inspection checklists, logs photo evidence, and receives assigned tasks. Location tracking is restricted strictly to active shift hours.  
* **Citizen / Resident** : Operates within local ward. Submits geotagged reports in under 60 seconds and tracks resolution status without needing to identify underlying departmental structures.

#### 7\. Technical Implementation Standards for Frontend Engineers

Engineering teams implementing this design system across web and mobile frameworks should follow these core implementation standards:

* **CSS Variable Setup** : Implement design tokens using CSS variables defined at :root level for HEX colors, font sizing, border radii, and shadows.  
* **Z-Index Elevation Stacking** :  
* Map Canvas Layer: z-index: 1  
* Map Pins & Hotspot Overlays: z-index: 5  
* Floating Sidebar Cards & Headers: z-index: 10  
* Dropdown Menus & Popovers: z-index: 50  
* Mobile Bottom Sheet Drawer & Modals: z-index: 100  
* **Responsive Breakpoints** :  
* mobile: \< 768px (Single-column layout, full-width sliding bottom sheet, bottom navigation bar).  
* desktop: \>= 1024px (Multi-panel overlay layout on full-screen vector map canvas).  
* **Accessibility (WCAG 2.1 AA Compliance)** :  
* Ensure all primary text meets minimum 4.5:1 contrast ratios against background fills (\#0B6B61 on white \= 5.2:1; \#1E293B on white \= 12.6:1).  
* Ensure all category chips, map pins, and action triggers support full keyboard navigation and carry appropriate ARIA labels (aria-pressed, aria-expanded, aria-label).

