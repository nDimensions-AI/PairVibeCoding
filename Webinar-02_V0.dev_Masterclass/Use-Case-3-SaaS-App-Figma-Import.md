# Use Case 3: The SaaS App - Figma Import & Starters

**Goal:** Showcase the professional workflow of building a complex `App` by importing a high-fidelity design from Figma and then adding new features using starters.

---

### Scenario: "Helios" Drone Fleet Management Dashboard

**Requirement:** Build the UI for a data-dense SaaS dashboard, starting from a professional Figma design and adding an authentication form.

#### **Step 1: Generate the Core App from a Figma Design**

We start with a pixel-perfect design from S Kid, our designer. This is the source of truth.

**Action:**
1.  Click the **`Import from Figma`** button in the v0.dev interface.
2.  Paste the public URL of the Figma design file.
3.  v0.dev analyzes the file and generates a near-perfect React equivalent of the entire dashboard.

#### **Step 2: Add a New Feature with a Starter**

The app needs an authentication flow, which wasn't in the original dashboard design. We use a starter for speed.

**Action:**
1.  In the same project, click the **`Sign Up Form`** one-click starter button.
2.  A standard, well-designed sign-up form is generated as a new component.

#### **Step 3: Unify the Design with a Stylistic Prompt**

The new sign-up form has a generic theme. We use a prompt to make it match the futuristic aesthetic of our imported dashboard.

**Refinement Prompt:**
> "Apply the 'sci-fi HUD' theme from our main dashboard to this sign-up form. Make the input fields have a subtle glow, use a monospaced font, and change the button to match our primary cyan action color."
