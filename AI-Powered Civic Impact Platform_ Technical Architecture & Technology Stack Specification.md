### AI-Powered Civic Impact Platform: Technical Architecture & Technology Stack Specification

The modern municipal environment requires an automated, resilient, and explainable infrastructure engine capable of converting fragmented public reports into prioritized civic work orders. As specified in the platform requirement documentation, traditional municipal intake systems suffer from severe operational bottlenecks: redundant submissions clogging dispatch queues, inefficient manual triage of urgent hazards alongside routine maintenance, analytical blindspots preventing cross-category hotspot detection, and a pervasive lack of transparency that erodes public trust.  
To resolve these systemic bottlenecks, this technical specification defines an enterprise-grade technology stack optimized for rapid mobile reporting, multi-modal artificial intelligence processing, real-time spatial analytics, and deterministic workflow orchestration.

#### 1\. System Architecture & Strategic Vision

The platform is architected around four core operational lifecycle stages:  **Capture** ,  **Understand** ,  **Reveal** , and  **Act** . The underlying engineering philosophy combines lightweight edge interfaces with heavy asynchronous AI pipelines and unified spatial-vector storage.  
The platform architecture resolves the key operational friction points across three core user roles:

* **Citizen Community Members (Maya)**  require a mobile-optimized submission interface operating with an execution budget of under 60 seconds, accompanied by transparent, real-time lifecycle tracking.  
* **Municipal Administrators & Dispatchers (David)**  require an intelligent GIS dashboard capable of rendering spatial-thematic clusters, providing explainable AI priority rankings, and generating sub-minute executive action briefs.  
* **Field Maintenance Leads & Department Heads (Carlos)**  require consolidated master work orders containing precise location data, synthesized multi-report summaries, and structured job resolution logging.

#### 2\. Technology Stack Specification Matrix

To balance high-concurrency ingestion, heavy AI inference, and complex spatial-vector queries, the platform utilizes a decoupled, modern multi-tier stack.  
The following matrix outlines the selected technologies across each layer of the software delivery pipeline, detailing the primary operational justifications derived from the platform requirements:  
Stack Layer,Primary Technology Choice,Secondary / Supporting Tech,Primary Architectural Justification  
Frontend Framework,Next.js 15+ (React 19 App Router),"TypeScript, Progressive Web App (PWA) Service Workers","Delivers sub-60s mobile intake via server-side rendering (SSR), optimized bundle sizes, and offline media caching for field deployment."  
Styling & UI Library,Tailwind CSS v4,"shadcn/ui, Radix Primitives","Provides accessible, high-density dashboard components for dispatchers and responsive, touch-friendly layouts for mobile citizens."  
Interactive Mapping,MapLibre GL JS,"Mapbox Vector Tiles (MVT), Turf.js",GPU-accelerated WebGL vector map rendering capable of smoothly displaying dynamic density heatmaps and cluster polygons.  
API & Service Layer,Python 3.12+ (FastAPI),"Pydantic v2, WebSockets / Server-Sent Events","High-performance asynchronous execution for API endpoints, native Python AI/ML ecosystem integration, and real-time state broadcasts."  
Async Task Orchestration,Celery,Redis 7+ Message Broker,"Decouples resource-heavy AI pipeline jobs (embedding generation, spatial-temporal matching) from the client-facing intake API."  
Database & Vector Engine,PostgreSQL 16+,"PostGIS 3.4+, pgvector extension","Unifies structured relational data, 50-meter spatial buffer queries, and high-dimensional embedding similarity in a single engine."  
Object Storage,Cloudflare R2 / AWS S3,AWS CloudFront / Cloudflare CDN,"High-throughput storage for photographic evidence, optimizing media delivery for rapid browser preview and computer vision pipelines."  
Auth & Access Control,Supabase Auth / Clerk,"JWT, OAuth2, Signed Tracking Tokens",Enables low-friction citizen report lookup via signed tokens while enforcing strict Role-Based Access Control (RBAC) for admins.  
Deployment Infrastructure,Vercel  (Frontend Edge),AWS ECS (Docker) & Neon Serverless Postgres,"Ensures elastic auto-scaling during sudden emergency traffic surges (e.g., severe flooding or storm damage events)."

#### 3\. Deep-Dive Tier Specifications

##### 3.1 Frontend & GIS Visualization Engine

The client layer is partitioned into two dedicated web applications sharing a core design system: a lightweight Mobile Capture App and an Administrative GIS Triage Console.

* **Next.js 15 App Router & PWA Architecture** : The citizen interface uses Next.js server components and client-side web workers to minimize mobile JavaScript payloads. PWA web app manifests and service workers enable offline photo and location capture, automatically uploading buffered reports when network connection is restored.  
* **WebGL Mapping with MapLibre GL JS** : Administrative dispatchers process hundreds of active complaints simultaneously. MapLibre GL JS leverages browser WebGL shaders to render vector tiles, heatmaps, and spatial cluster boundaries at 60 FPS without DOM degradation. Turf.js executes client-side geospatial calculations, such as dynamic buffer rendering around active dispatch sites.  
* **Responsive Multi-Role Layouts** : Using Tailwind CSS v4 and modular UI primitives, the application switches layout density based on user context—providing full-screen single-thumb navigation for Citizens, multi-pane tile grids for Dispatchers, and simplified task cards for Field Maintenance Leads.

##### 3.2 Backend Services & AI Pipeline Engine

The backend architecture separates synchronous API routing from asynchronous intelligence workloads.

1. **Asynchronous Processing with FastAPI** : FastAPI's native async/await loop handles high-throughput HTTP ingestion. Submissions are validated instantly via Pydantic schemas and written to PostgreSQL before handing off multi-step processing to queue workers.  
2. **Task Queue & Multi-Modal Processing via Celery & Redis** : Heavy AI inference—including image feature extraction, sentence transformer text embeddings, and spatial buffer scans—runs inside Celery worker nodes backed by Redis. This architecture keeps the initial client HTTP response time under 600 milliseconds.  
3. **Plain-Language Explainable Prioritization Engine** : To prevent opaque black-box dispatching, the AI engine evaluates multi-factor safety parameters to calculate dynamic priority ranks ( \$P \\in \\{1, 2, 3, 4\\}\$ ). The priority engine evaluates:  
4. **Urgency & Safety Threat** : Risk of immediate physical harm (e.g., exposed live power lines adjacent to standing water).  
5. **Impact Scope** : Total volume of impacted citizens or duplicate complaints linked within a 50-meter spatial radius.  
6. **Infrastructure Degradation** : Escalation risk if untreated (e.g., unblocked drainage causing asphalt road erosion).  
7. **Proximity Risk** : Proximity within 75 meters of sensitive municipal infrastructure, such as schools, hospitals, or transit hubs.

The backend passes these factors to an LLM orchestration layer (using LangChain and structured output prompts) to generate concise, human-readable explanations detailing why a specific report outranks others in the dispatch queue.

* **Sub-Minute Executive Action Brief Synthesis** : When multiple reports form a spatial cluster, the backend synthesizes multi-complaint data into a single operational brief. The LLM summarizes up to dozens of individual submissions into a unified technical problem description, recommended field crew actions, and suggested municipal department allocations (e.g., Public Works or Electrical Maintenance).

##### 3.3 Unified Persistence, Spatial & Vector Engine

Rather than maintaining separate relational, spatial, and vector database systems—which introduces synchronization lag and complex operational overhead—the platform consolidates persistence into PostgreSQL using PostGIS and pgvector.

* **PostGIS Spatial Analytics** : PostGIS handles geographic geometry storage and spatial index operations (GIST). Spatial queries utilize the ST\_DWithin function with spatial casting to execute exact distance-based duplicate matching within 50-meter radii and proximity scoring within 75-meter sensitivity zones.  
* **pgvector Semantic Embedding Engine** : Text descriptions and multi-modal image features are converted into dense vector embeddings (e.g., 768-dimensional vectors from open-source transformer models) and stored in vector column types. Using Hierarchical Navigable Small World (HNSW) indexing with cosine distance (\<-\>), the database performs sub-millisecond semantic similarity searches across historical report databases.  
* **Hybrid Spatial-Temporal Duplicate Engine** : The matching pipeline combines relational, spatial, and vector clauses into a single query engine. When an incoming report is evaluated, PostGIS identifies all reports logged within a 50-meter radius over the prior 48 hours, while pgvector measures the semantic similarity of the description embeddings.

\-- Hybrid Spatial-Temporal & Semantic Duplicate Query Example  
SELECT   
    id,   
    verified\_category,   
    created\_at,  
    ST\_Distance(location::geography, ST\_SetSRID(ST\_MakePoint(:lon, :lat), 4326)::geography) AS distance\_meters,  
    (description\_embedding \<=\> :query\_embedding) AS semantic\_distance  
FROM reports  
WHERE   
    lifecycle\_status IN ('Submitted', 'Under Review')  
    AND ST\_DWithin(location::geography, ST\_SetSRID(ST\_MakePoint(:lon, :lat), 4326)::geography, 50\)  
    AND created\_at \>= NOW() \- INTERVAL '48 hours'  
    AND (description\_embedding \<=\> :query\_embedding) \< 0.25  
ORDER BY semantic\_distance ASC  
LIMIT 5;

When a match is confirmed, the system marks the submission as a Linked Duplicate, links it to the primary Master Ticket, increments the master ticket's citizen impact weight, and notifies the submitter.

#### 4\. Unified Spatial-Vector Schema & Data Architecture

The relational schema strictly enforces lifecycle state transitions, spatial indexing, embedding parameters, and manual administrative overrides.  
\-- Core Schema Definition for Civic Impact Platform  
CREATE EXTENSION IF NOT EXISTS postgis;  
CREATE EXTENSION IF NOT EXISTS vector;

\-- Enforce explicit lifecycle state machine  
CREATE TYPE lifecycle\_status\_enum AS ENUM ('Submitted', 'Under Review', 'Assigned', 'Resolved');  
CREATE TYPE priority\_rank\_enum AS ENUM ('Priority 1', 'Priority 2', 'Priority 3', 'Priority 4');

\-- Main Reports & Master Tickets Table  
CREATE TABLE reports (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    tracking\_id VARCHAR(12) UNIQUE NOT NULL,  
    created\_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
    updated\_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),  
      
    \-- Citizen Input Layer  
    raw\_description TEXT NOT NULL,  
    user\_category VARCHAR(64),  
    media\_url VARCHAR(512),  
    location GEOMETRY(Point, 4326\) NOT NULL,  
    formatted\_address VARCHAR(256),  
      
    \-- AI Intelligence Layer  
    verified\_category VARCHAR(64) NOT NULL,  
    concise\_summary VARCHAR(256),  
    is\_duplicate BOOLEAN NOT NULL DEFAULT FALSE,  
    master\_ticket\_id UUID REFERENCES reports(id) ON DELETE SET NULL,  
    duplicate\_count INT NOT NULL DEFAULT 1,  
      
    \-- Vectors & Prioritization  
    description\_embedding vector(768),  
    priority\_rank priority\_rank\_enum NOT NULL DEFAULT 'Priority 4',  
    priority\_score NUMERIC(5, 2\) NOT NULL DEFAULT 0.00,  
    priority\_rationale TEXT,  
      
    \-- Workflow & Operations  
    lifecycle\_status lifecycle\_status\_enum NOT NULL DEFAULT 'Submitted',  
    assigned\_department VARCHAR(128),  
    dispatch\_timestamp TIMESTAMPTZ,  
    resolution\_notes TEXT,  
      
    \-- Audit & Overrides  
    is\_manually\_overridden BOOLEAN NOT NULL DEFAULT FALSE,  
    override\_reason TEXT,  
    overridden\_by\_user\_id UUID  
);

\-- Spatial and Vector Indexes  
CREATE INDEX idx\_reports\_location ON reports USING GIST (location);  
CREATE INDEX idx\_reports\_embedding ON reports USING hnsw (description\_embedding vector\_cosine\_ops);  
CREATE INDEX idx\_reports\_status\_priority ON reports (lifecycle\_status, priority\_rank);

#### 5\. End-To-End System Flow Across Civic Lifecycle Stages

The system coordinates data across four discrete lifecycle stages, ensuring complete traceability from initial capture to physical resolution:

##### Stage 1: Capture (Mobile Intake)

The client application captures raw text, photographic evidence, and precise GPS location coordinates (or interactive map pins). The mobile interface submits the report to FastAPI in under 60 seconds, returning an instant submission confirmation containing a unique 12-character Tracking ID.

##### Stage 2: Understand (AI Processing)

The incoming payload is queued in Celery. The worker executes vector embedding generation, queries PostGIS for spatial duplicates within 50 meters, verifies municipal service categories (correcting misclassifications if necessary across categories like Waterlogging & Drainage, Road Failure, Waste Management, Street Lighting, and Public Utilities), generates a concise summary, and calculates the priority score and plain-language explanation.

##### Stage 3: Reveal (Spatial Triage & Clustering)

The administrative console queries active reports to render color-coded density heatmaps and spatial clusters (such as multi-issue correlations connecting blocked drains, standing water, and road erosion within a 100-meter cluster radius). Dispatchers can click any cluster to generate a sub-minute executive action brief summarizing up to dozens of underlying complaints.

##### Stage 4: Act (Workflow Execution & Feedback)

Dispatchers assign consolidated master work orders to municipal field departments (e.g., Public Works or Road Maintenance). The workflow engine updates all linked child reports across the lifecycle state machine (Submitted  \$\\rightarrow\$  Under Review  \$\\rightarrow\$  Assigned  \$\\rightarrow\$  Resolved). Citizens monitor progress using their tracking links without needing to call municipal phone queues.

#### 6\. Performance SLAs, Security & Production Scaling Roadmap

##### 6.1 Performance Evaluation Metrics & Targets

In alignment with the evaluation protocols established in the project specification, system performance is benchmarked against strict operational targets:  
The following matrix defines the operational SLA benchmarks across user experience, AI performance, processing speed, and civic transparency:  
Metric Category,Target Indicator,Baseline / Traditional Legacy,Operational Target,Measurement Methodology  
User Experience,Submission Completion Time,4–6 minutes (complex web forms),\< 60 seconds,Telemetry tracking on mobile web client screens.  
AI Performance,Duplicate Detection Precision,Manual human review,\> 85% Precision,Verified against ground truth human admin audits.  
AI Performance,Category Classification Accuracy,Manual sorting,\> 90% Accuracy,Match rate between AI classification and verified department field tags.  
Operational Speed,AI Triage Processing Speed,24–48 hours queue wait time,\< 2 minutes,Time elapsed from API intake to AI priority score assignment.  
Decision Support,Action Brief Generation Efficiency,15 minutes manual review,\< 60 seconds,Time required for LLM to compile and render cluster summary.  
Civic Trust,Report Tracking Visibility Rate,0% feedback on legacy channels,100% Tracking,"Percentage of submitted reports with accessible, live status tracking links."

##### 6.2 Security, Role-Based Access Control & Integrity Controls

* **Citizen Privacy & Public Data Stripping** : Photo uploads are automatically stripped of EXIF metadata before public display to prevent unintentional disclosure of personal identity. Public tracking interfaces display location data rounded to neighborhood block levels, whereas administrative dashboards retain exact GPS coordinates for field crews.  
* **Granular Role-Based Access Control (RBAC)** :  
* *Public Role* : Restricted to creating reports, querying status via signed tracking tokens, and viewing aggregated public map overlays.  
* *Dispatcher Role* : Authorized to link/unlink master tickets, override AI priority scores, generate action briefs, and assign department work orders.  
* *Field Lead Role* : Restricted to assigned department task queues, location routing details, and logging resolution evidence notes.  
* **Audit Logging for AI Overrides** : Whenever an administrator manually adjusts an AI-generated priority score or unlinks a duplicate report (e.g., in edge cases like adjacent vendor waste bins near a water leak), the platform logs the user ID, timestamp, original AI score, manual score, and override justification text into immutable database audit tables.

##### 6.3 Next-Phase Infrastructure Scaling Roadmap

Beyond the core architecture, the technical roadmap establishes expansion pathways for municipal scaling:

1. **Direct Citizen Messaging Channels** : Integration of WhatsApp Business API and Telegram Bots to allow citizens to submit voice notes, photos, and location pins directly through messaging apps, backed by the same FastAPI ingestion pipeline.  
2. **Predictive Infrastructure Analytics** : Deployment of historical spatial-temporal models to forecast seasonal infrastructure failure risks (such as predicting monsoon drain blockages before severe rainfall events occur).  
3. **IoT Sensor Integration** : Automated webhook ingestion connecting municipal IoT water-level sensors and smart streetlights directly into the intake engine, automatically triggering high-priority master tickets prior to citizen complaints.

