# Use Case 5: The Full-Stack Starter

**Goal:** Showcase the most advanced capability of v0.dev: scaffolding a complete, production-ready, full-stack `Starter` application with a database and authentication.

---

### Scenario: Architecting the "Helios" Drone App Backend

**Requirement:** Create the entire backend foundation for the "Helios" Drone Fleet Management app, which requires a real-time database and user authentication.

#### **Step 1: Choose the Right Architectural Template**

We need more than just UI. We need a full-stack architecture.

**Action:**
1.  Navigate to the v0.dev new project screen.
2.  Instead of prompting for UI, select the **Supabase** starter template from the `Starter Templates` section.

#### **Step 2: Generate the Full-Stack Foundation**

v0.dev will now generate an entire Next.js project, not just a component.

**What is Generated:**
* A complete Next.js 14 application structure with the App Router.
* The Supabase SDK is integrated as a dependency.
* A pre-configured Supabase client for connecting to the database.
* Environment variable files (`.env.local.example`) for API keys.
* Fully functional, server-side login and sign-up pages already wired up to Supabase Auth.
* Example server and client components demonstrating how to fetch data and subscribe to real-time updates.

**Outcome:**
With a single click, we have a secure, data-driven, and production-ready foundation. We can now take the "Helios" dashboard UI we generated in Use Case 3, paste it into this project, and connect it to the pre-configured Supabase functions to create a fully functional application.
