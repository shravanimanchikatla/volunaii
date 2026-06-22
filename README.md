# VOLUNAI: Intelligent Crisis Response and Volunteer Mobilization Platform

VOLUNAI is a web application designed to coordinate disaster response, volunteer mobilization, emergency blood donations, and missing persons search missions. By leveraging Google Gemini models and digital signal processing, VOLUNAI automates task extraction from field reports, analyzes audio uploads for voice-based urgency detection, auto-assigns tasks to volunteers based on location and experience, and facilitates real-time communication.

---

## 1. The Full Stack Architecture

The platform is built using a decoupled architecture, with Python Flask driving the backend logic and modern, responsive frontend templates rendering live states.

### Backend Development Stack
- **Web Framework**: Flask (Python 3) provides the core application routing, middleware execution, and request lifecycle management.
- **Database ORM**: Flask-SQLAlchemy abstracts interactions with the relational database schema.
- **Real-Time Layer**: Flask-SocketIO (backed by Eventlet and Gevent websockets) handles instant two-way updates (e.g., dispatching volunteer tasks as soon as they are assigned).
- **Concurrency & WSGI**: Eventlet, Gevent, and Gunicorn are used to enable high-concurrency connections required for real-time WebSockets.
- **Acoustic Intelligence Pipeline**: Local digital signal processing is executed using `librosa`, `soundfile`, and `numpy` to extract acoustic features (RMS energy and tempo metrics) directly from uploaded audio field reports.
- **File Processing Layer**: Multi-format parsing is achieved via `pandas` (for CSV and Excel files), `openpyxl` (for Excel dependencies), and `PyPDF2` (for PDF reports).
- **Generative AI Core**: Integrates with the Google Generative AI SDK:
  - **Gemini 1.5 Flash**: Processes raw text/files and multi-modal audio files to perform semantic entity parsing and extract structured JSON lists of emergency tasks.
  - **Gemini 2.5 Flash**: Conducts multi-task analysis to synthesize high-level situation reports, geographic hotspots, and skill shortages for crisis organizers.

### Frontend Presentation Stack
- **Structure**: Semantic HTML5 elements define structures for organizer, volunteer, and profile interfaces.
- **Styling**: Responsive layouts, custom UI typography (e.g., Google Fonts), dark-themed styles, custom status badges, and interactive control panels.
- **Client-Side Real-Time Layer**: Socket.io-client scripts initialize client rooms and receive instant alert dispatches without page reloads.

### Database Layer
- **Relational Database**: MySQL / MariaDB (managed via the `PyMySQL` driver).
- **Dynamic Configuration**: Supports both local development configurations and secure SSL deployments (e.g., cloud engines like Aiven DB) with customized compiler options (e.g., requiring compiled SSL certs on Aiven hosts).
- **Auto-Migrations**: The application includes self-healing schema scripts on launch, automatically executing `ALTER TABLE` SQL operations to inject missing user profile columns (e.g., blood types and notification preferences) into existing tables safely.

---

## 2. Platform Modules and Functionalities

```mermaid
graph TD
    A[Organizer Upload / Text Input] -->|Raw Field Report| B[Multi-Format File Parser]
    B -->|Extracted Text / Audio Part| C[Google Gemini NLP Pipeline]
    A -->|Audio Upload| D[Librosa Acoustic Analysis Engine]
    D -->|RMS Energy & Tempo Urgency Score| C
    C -->|Structured JSON Array| E[Task Generation Engine]
    E --> F[Intelligent Auto-Assignment Engine]
    F -->|Location, Availability & Experience Ranking| G[Socket.io Real-Time Dispatch]
    G -->|Instant Sound & UI Alerts| H[Volunteer Dashboard]
    
    I[NGO Blood Request] -->|Donor Compatibility Matrix| J[BloodLink Donor Matcher]
    J -->|Automatic Alerts| H
    
    K[Missing Person Case Report] -->|FIR Police Verified Cases| L[RAAKSHA Command Center]
    L -->|Rescue Search Assignments| H
```

### A. AI-Driven Task Extraction & Emergency Parsing
- **Unified Ingestion**: Organizers can input raw text descriptions, or upload files (`.txt`, `.csv`, `.xls`, `.xlsx`, `.pdf`).
- **Semantic Analysis**: The backend parses incoming text and sends it to the Gemini 1.5 Flash model.
- **Task Construction**: Gemini separates composite, raw disaster reports into separate distinct tasks. For each task, the AI determines:
  - **Title**: A concise 3-5 word identifier.
  - **Description**: A comprehensive summary of the incident.
  - **Location**: Specific geo-locations or neighborhoods.
  - **Required Skills**: Main skill required (e.g., Medical, Rescue, General Labor, Carpentry).
  - **Urgency**: A calibrated integer score from 1 to 10.
- **Fault-Tolerance**: If an upload fails parsing or lacks explicit content, fallback routines create a manual-review task ensuring no voice/text report is dropped.

### B. Digital Signal Audio Urgency Detection
- **Acoustic Processing**: When an audio field report (`.wav`, `.mp3`, `.webm`, `.ogg`) is uploaded, the Librosa engine extracts physical properties:
  - **Root-Mean-Square (RMS) Energy**: Reflects volume, physical pressure, and stress in the reporter's voice.
  - **Tempo (BPM)**: Captures tempo spikes associated with distress and panic.
- **Score Calculation**: The raw acoustic features are normalized to compute a local voice urgency score between 1 and 10.
- **Local Transcription Pipeline**: Coordinates with a simulated OpenAI Whisper background pipeline that decodes audio frame sequences and generates logs tracking spectral decoding, reinforcing auditable emergency responses.

### C. Match-Based Auto-Assignment Engine
- **Geographic Filtering**: The system matches the locations of generated tasks with the reported locations of available volunteers (using case-insensitive matching).
- **Availability Check**: Only volunteers who toggled their availability status on their profiles are queried.
- **Meritocracy and Experience Sorting**: Eligible matched volunteers are ranked by their aggregate "Urgency Points" (defined as the sum of urgency scores of their completed tasks). The task is automatically assigned to the volunteer with the highest points to ensure experienced personnel handle urgent needs first.
- **Real-Time Socket Dispatch**: Immediately upon assignment, Flask-SocketIO pushes a `new_assignment` event targeting the volunteer's private client room (`user_<id>`), playing an emergency alert and displaying details instantly.

### D. BloodLink Emergency Donor Network
- **NGO Blood Ingestion**: NGOs or organizers submit blood requests containing patient name, required blood type, hospital location, and urgency scores.
- **Donor Compatibility Matrix**: Matches donors based on a medical blood compatibility profile:
  
  | Patient Blood Type | Allowed Donor Types |
  | :---: | :--- |
  | **A+** | A+, A-, O+, O- |
  | **O+** | O+, O- |
  | **B+** | B+, B-, O+, O- |
  | **AB+** | A+, A-, B+, B-, AB+, AB-, O+, O- |
  | **A-** | A-, O- |
  | **O-**| O- |
  | **B-** | B-, O- |
  | **AB-**| AB-, A-, B-, O- |

- **Emergency Alert Broadcasts**: Eligible, available donors receive notifications about active matched requests in their areas.
- **Donation Lifespan Tracking**: Integrates multi-step lifecycle transitions:
  `Pending` $\rightarrow$ `Donor Assigned` $\rightarrow$ `Donation In Progress` $\rightarrow$ `Volunteer Arrived` $\rightarrow$ `Completed`
- **Medical Rest Periods**: Upon completion of a blood request, the donor's profile is updated with `last_donation_date` to enforce a 90-day rest period. During this window, they are excluded from emergency matches to safeguard their health.

### E. RAAKSHA Child Rescue Portal
- **Forensic Case Registration**: Organizers register active missing person cases, recording child demographic data, clothes last worn, CCTV availability, police FIR identification numbers, and contact details for investigating officers.
- **Multi-Photo Database**: Uploads and paths family photos, physical profiles, and forensic portraits to assist search parties.
- **Sighting Registration**: Active volunteers log sightings in real-time. Sightings record coordinates, clothing conditions, visual profiles of accompanying adults, and medical/health evaluations.
- **Verification Gateways**: Sightings are flagged as unverified until organizers verify them. Once verified, sightings are logged into command maps.
- **After Action Reports (AAR)**: Provides on-demand CSV exports detailing task statistics, timelines, and volunteer metrics for accountability.

### F. Gamified Volunteer Engagement & Dashboards
- **Urgency Points**: Completing tasks awards volunteers experience points equal to the task's urgency rating.
- **Global Leaderboard**: Gamifies humanitarian effort by tracking and displaying top volunteers, listing their skills, task counts, and points.
- **Role-Based Workspaces**:
  - **Volunteer Dashboard**: Shows active assigned tasks, matching blood requests, available missing person search assignments, and active task controls (accept, complete, release).
  - **Organizer Dashboard**: Features report submissions, multi-format upload widgets, AI situation report generations, missing person case directories, and task management panels.

---

## 3. Database Schema Models

The system architecture utilizes six relational database models configured in SQLAlchemy.

```mermaid
erDiagram
    USER ||--o{ REPORT : creates
    USER ||--o{ TASK : assigned_to
    USER ||--o{ BLOOD_REQUEST : requests_as_ngo
    USER ||--o{ BLOOD_REQUEST : responds_as_donor
    USER ||--o{ MISSING_PERSON_CASE : organizes
    USER ||--o{ SIGHTING : reports
    USER ||--o{ SEARCH_ASSIGNMENT : joins
    
    REPORT ||--o{ TASK : generates
    MISSING_PERSON_CASE ||--o{ SIGHTING : has
    MISSING_PERSON_CASE ||--o{ SEARCH_ASSIGNMENT : requires
```

### 1. User Model
Represents volunteers, organizers, and emergency blood donors.
- `id` (INT, Primary Key)
- `name` (VARCHAR 100, Required)
- `email` (VARCHAR 120, Unique, Required)
- `password_hash` (VARCHAR 256, Required)
- `role` (VARCHAR 20, Default: `'volunteer'` - Options: `'volunteer'`, `'organizer'`)
- `location` (VARCHAR 100, Optional - Zip code / City)
- `skills` (VARCHAR 255, Optional - Comma-separated values)
- `is_available` (BOOLEAN, Default: `False`)
- `blood_group` (VARCHAR 5, Optional)
- `blood_type` (VARCHAR 5, Optional)
- `is_emergency_donor` (BOOLEAN, Default: `False`)
- `last_donation_date` (DATETIME, Optional)
- `emergency_alerts_enabled` (BOOLEAN, Default: `True`)
- `city` (VARCHAR 100, Optional)
- `contact_number` (VARCHAR 20, Optional)

### 2. Report Model
Represents raw field inputs uploaded or typed by organizers.
- `id` (INT, Primary Key)
- `organizer_id` (INT, Foreign Key referencing `user.id`, Cascade Delete)
- `raw_text` (TEXT, Required)
- `submitted_at` (DATETIME, Default: UTC Now)

### 3. Task Model
Represents emergency operations parsed by AI engines.
- `id` (INT, Primary Key)
- `report_id` (INT, Foreign Key referencing `report.id`, Cascade Delete)
- `title` (VARCHAR 200, Required)
- `description` (TEXT, Required)
- `required_skills` (VARCHAR 255, Required)
- `location` (VARCHAR 100, Required)
- `urgency_score` (INT, Required)
- `status` (VARCHAR 20, Default: `'open'` - Options: `'open'`, `'assigned'`, `'completed'`)
- `assigned_volunteer_id` (INT, Foreign Key referencing `user.id`, Optional)
- `created_at` (DATETIME, Default: UTC Now)

### 4. BloodRequest Model
Tracks emergency blood supply requests.
- `id` (INT, Primary Key)
- `ngo_id` (INT, Foreign Key referencing `user.id`, Cascade Delete)
- `patient_name` (VARCHAR 100, Required)
- `blood_type_needed` (VARCHAR 5, Required)
- `units_needed` (INT, Default: `1`)
- `hospital_name` (VARCHAR 200, Required)
- `hospital_address` (TEXT, Optional)
- `city` (VARCHAR 100, Optional)
- `urgency_score` (INT, Default: `5`)
- `status` (VARCHAR 20, Default: `'Pending'`)
- `created_at` (DATETIME, Default: UTC Now)
- `accepted_at` (DATETIME, Optional)
- `completed_at` (DATETIME, Optional)
- `assigned_donor_id` (INT, Foreign Key referencing `user.id`, Optional)

### 5. MissingPersonCase Model
Maintains active cases registered in the RAAKSHA portal.
- `id` (INT, Primary Key)
- `organizer_id` (INT, Foreign Key referencing `user.id`, Cascade Delete)
- `name` (VARCHAR 100, Required)
- `nickname` (VARCHAR 100, Optional)
- `dob` (DATE, Optional)
- `age` (INT, Optional)
- `gender` (VARCHAR 20, Optional)
- `distinctive_features` (TEXT, Optional)
- `clothing_last_seen` (TEXT, Optional)
- `location_last_seen` (VARCHAR 200, Required)
- `latitude` (FLOAT, Optional)
- `longitude` (FLOAT, Optional)
- `last_seen_time` (DATETIME, Default: UTC Now)
- `was_child_alone` (VARCHAR 20, Optional)
- `cctv_available` (BOOLEAN, Default: `False`)
- `witness_info` (TEXT, Optional)
- `parent_name` (VARCHAR 100, Optional)
- `parent_phone` (VARCHAR 20, Optional)
- `parent_relationship` (VARCHAR 50, Optional)
- `parent_location` (VARCHAR 200, Optional)
- `fir_number` (VARCHAR 100, Optional)
- `police_station` (VARCHAR 100, Optional)
- `investigating_officer` (VARCHAR 100, Optional)
- `officer_contact` (VARCHAR 50, Optional)
- `is_fir_verified` (BOOLEAN, Default: `False`)
- `photo_url` (VARCHAR 500, Optional)
- `body_photo_url` (VARCHAR 500, Optional)
- `family_photo_url` (VARCHAR 500, Optional)
- `medical_conditions` (TEXT, Optional)
- `special_needs` (TEXT, Optional)
- `description` (TEXT, Optional)
- `urgency_score` (INT, Default: `50`)
- `status` (VARCHAR 20, Default: `'Active'`)
- `created_at` (DATETIME, Default: UTC Now)
- `resolved_at` (DATETIME, Optional)

### 6. Sighting Model
Maintains volunteer sightings reported for active RAAKSHA cases.
- `id` (INT, Primary Key)
- `case_id` (INT, Foreign Key referencing `missing_person_case.id`, Cascade Delete)
- `reporter_id` (INT, Foreign Key referencing `user.id`, Optional)
- `location_name` (VARCHAR 200, Required)
- `latitude` (FLOAT, Optional)
- `longitude` (FLOAT, Optional)
- `description` (TEXT, Required)
- `photo_url` (VARCHAR 500, Optional)
- `child_condition` (VARCHAR 100, Optional)
- `adult_description` (TEXT, Optional)
- `is_verified` (BOOLEAN, Default: `False`)
- `reported_at` (DATETIME, Default: UTC Now)

### 7. SearchAssignment Model
Links volunteers enrolled in active search missions.
- `id` (INT, Primary Key)
- `case_id` (INT, Foreign Key referencing `missing_person_case.id`, Cascade Delete)
- `volunteer_id` (INT, Foreign Key referencing `user.id`, Cascade Delete)
- `status` (VARCHAR 20, Default: `'Assigned'`)
- `assigned_at` (DATETIME, Default: UTC Now)

---

## 4. Environment and Execution Setup

### 1. Requirements Setup
Ensure python package dependencies are installed using `pip`:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables Configuration
Create a `.env` file in the root workspace directory with the following variables:
```env
# Flask Configuration
FLASK_SECRET_KEY=your_secret_cryptographic_key

# Generative AI Key
GEMINI_API_KEY=AIzaSyYourGoogleGeminiApiKey

# Database Options
# For production cloud database (e.g. Aiven MySQL):
DATABASE_URL=mysql://user:pass@host:port/dbname?ssl-mode=REQUIRED
# For local MySQL database fallback:
DB_USERNAME=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=smart_volunteer_db

# Web Server Ports
PORT=5000
```

### 3. Running the Server
Execute the Flask server using the command prompt or terminal:
```bash
python app.py
```
On startup, the system will initialize the database tables automatically, map configuration options, run column-level data migrations, verify folder permissions, and bind to `http://0.0.0.0:5000`.