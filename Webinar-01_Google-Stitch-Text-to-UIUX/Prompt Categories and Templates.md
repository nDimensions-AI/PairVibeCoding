# Master Prompting Guide - Google Stitch Best Practices

## Overview
A comprehensive guide to crafting effective prompts for Google Stitch, leveraging the multimodal power of Gemini 2.5 Pro to create exceptional UI and code from text, sketches, and images.

## Core Prompting Principles

### 1. The Anatomy of a Perfect Prompt

#### Essential Components:
```
[CONTEXT] + [SPECIFIC REQUIREMENTS] + [STYLE DIRECTION] + [TECHNICAL SPECIFICATIONS] + [CONSTRAINTS]
```

#### Template Structure:
```
Create/Design/Generate a [TYPE] for [PURPOSE] called '[NAME]'. 
The [AESTHETIC] should be [STYLE DESCRIPTORS] using [COLOR SPECIFICATIONS]. 
[LAYOUT REQUIREMENTS] with [SPECIFIC FEATURES]. 
[ADDITIONAL CONSTRAINTS OR PREFERENCES].
```

### 2. Specificity Hierarchy

#### Level 1 - Basic (Minimum Viable Prompt):
```
Create a landing page for a fitness app
```

#### Level 2 - Enhanced (Recommended):
```
Create a landing page for a fitness app called 'FitTrack'. 
Use a modern, energetic design with blue and white colors. 
Include a hero section with a call-to-action button and three feature cards below.
```

#### Level 3 - Detailed (Optimal):
```
Create a landing page for a fitness app called 'FitTrack'. 
The design should be modern and energetic, using navy blue (#1e3a8a) and white with orange (#f97316) accents. 
Include a hero section with the headline 'Transform Your Fitness Journey' and a prominent 'Start Free Trial' button. 
Below, display three feature cards for 'Workout Tracking', 'Nutrition Planning', and 'Progress Analytics', 
each with an icon and brief description. Use clean typography and plenty of white space.
```

## Prompt Categories and Templates

### 1. Application Type Prompts

#### Web Applications:
```
Create a [web app/dashboard/admin panel] for [specific use case]. 
Design should be [professional/modern/creative] with [responsive/desktop-first/mobile-first] layout. 
Include [navigation type], [main content area], and [sidebar/footer elements].
```

#### Mobile Applications:
```
Design a mobile app UI for [app purpose] targeting [user demographic]. 
Use [iOS/Android/cross-platform] design patterns with [gesture navigation/tab bar/drawer navigation]. 
Screen should include [specific mobile UI elements] optimized for [screen size] devices.
```

#### Landing Pages:
```
Create a landing page for [business type] that converts [target audience] to [desired action]. 
Use [brand personality] design with [trust elements] and clear [value proposition]. 
Include [social proof elements] and [conversion optimization features].
```

### 2. Style and Aesthetic Prompts

#### Modern Minimalism:
```
Use minimalist design principles with clean lines, ample white space, and a restricted color palette of [2-3 colors]. 
Typography should be sans-serif and highly legible. Focus on essential elements only.
```

#### Professional Corporate:
```
Design with a professional, trustworthy aesthetic using navy blue, gray, and white. 
Include subtle shadows, clean typography, and structured layouts that convey reliability and expertise.
```

#### Creative and Artistic:
```
Use a creative, artistic approach with [bold colors/gradients/artistic elements]. 
Include [unique layout patterns/creative typography/artistic illustrations] that showcase innovation and creativity.
```

#### Tech/SaaS Modern:
```
Implement modern SaaS design patterns with [glassmorphism/subtle gradients/clean cards]. 
Use [tech-forward color scheme] with clear information hierarchy and dashboard-style elements.
```

### 3. Layout and Structure Prompts

#### Grid-Based Layouts:
```
Use a [number]-column grid system with [consistent spacing]. 
Arrange [content elements] in a [specific pattern] with [responsive behavior] for smaller screens.
```

#### Card-Based Interfaces:
```
Organize content into card components with [shadow depth/border style]. 
Each card should contain [specific elements] with [hover effects/interactive states].
```

#### Hero-Driven Designs:
```
Start with a prominent hero section featuring [hero content type] with [overlay text/CTA placement]. 
Below the hero, organize content in [specific sections] with [clear visual hierarchy].
```

### 4. Color and Branding Prompts

#### Specific Color Implementation:
```
Use [primary color name/hex code] as the main brand color, [secondary color] for accents, 
and [neutral color] for text and backgrounds. Ensure [accessibility compliance/contrast ratios].
```

#### Brand Personality Integration:
```
Reflect [brand personality traits] through color choices, typography, and visual elements. 
The design should feel [emotional descriptors] and appeal to [target audience characteristics].
```

#### Color Psychology Application:
```
Use colors that convey [desired emotions/associations]. [Color] to suggest [meaning], 
[color] for [energy/trust/creativity], creating an overall feeling of [desired user emotion].
```

### 5. Functional Requirement Prompts

#### Navigation Systems:
```
Implement [navigation type: sticky header/hamburger menu/mega menu/sidebar] with [number] main sections. 
Include [search functionality/user account access/mobile optimization] and [breadcrumb/active state indicators].
```

#### Form Interfaces:
```
Create a [form type] with [field types] arranged in [layout pattern]. 
Include [validation indicators/progress tracking/error states] and [accessibility features].
```

#### Data Display Components:
```
Design components for displaying [data type] with [visualization method]. 
Include [filtering/sorting/pagination] capabilities and [empty states/loading indicators].
```

## Advanced Prompting Techniques

### 1. Iterative Refinement Strategy

#### Initial Broad Prompt:
```
Create a dashboard for project management
```

#### Progressive Refinement:
```
1. "Make it more suitable for software development teams"
2. "Add a kanban board section and recent activity feed"
3. "Use a dark theme with blue accents"
4. "Make the navigation sidebar collapsible"
5. "Add team member avatars and online status indicators"
```

### 2. Reference-Based Prompting

#### Style References:
```
Create a [app type] with an aesthetic similar to [well-known app/website], 
but adapted for [your specific use case]. Maintain the [specific design elements] 
while incorporating [your unique requirements].
```

#### Functional References:
```
Design a [component type] that works like [reference app's feature] but for [your context]. 
Include similar [interaction patterns/visual feedback] while adapting for [your specific needs].
```

### 3. Constraint-Driven Prompting

#### Technical Constraints:
```
Design for [specific browser/device limitations] with [performance requirements]. 
Optimize for [specific user contexts] and ensure [accessibility/compatibility standards].
```

#### Content Constraints:
```
Account for [variable content lengths/multilingual support/dynamic data]. 
Design should handle [edge cases] gracefully and maintain [visual consistency].
```

### 4. User Experience Focused Prompts

#### User Journey Integration:
```
Design for users who are [user state/goal] and need to [complete specific task]. 
The interface should guide them from [starting point] to [end goal] with [specific UX patterns].
```

#### Emotional Design:
```
Create an interface that makes users feel [desired emotions] when [performing key actions]. 
Use [design elements] to reinforce [brand values] and [user confidence].
```

## Refinement and Chat Commands

### 1. Visual Adjustments

#### Color Modifications:
```
- "Change [element] color to [specific color/hex code]"
- "Make the overall palette more [warm/cool/vibrant/muted]"
- "Increase contrast for better accessibility"
- "Add [color] accents to [specific elements]"
```

#### Layout Refinements:
```
- "Increase spacing between [elements] by [amount]"
- "Make the layout more [compact/spacious]"
- "Align [elements] to [left/center/right]"
- "Reorganize [section] to prioritize [specific element]"
```

#### Typography Improvements:
```
- "Make headings more [bold/elegant/modern]"
- "Increase text size for better readability"
- "Use [specific font family] for [text elements]"
- "Improve typography hierarchy with [size/weight variations]"
```

### 2. Interactive Element Enhancements

#### Button and CTA Optimization:
```
- "Make buttons more prominent with [styling changes]"
- "Add hover effects to interactive elements"
- "Change button shape to [rounded/square/pill]"
- "Increase button size for better touch targets"
```

#### Navigation Improvements:
```
- "Make navigation more intuitive with [changes]"
- "Add visual indicators for [current page/section]"
- "Improve mobile navigation with [specific pattern]"
- "Add [breadcrumbs/search/user menu] to navigation"
```

### 3. Content and Structure Adjustments

#### Information Architecture:
```
- "Reorganize content to highlight [priority elements]"
- "Group related [elements] together"
- "Create clear visual separation between [sections]"
- "Add [call-out boxes/sidebars] for [secondary information]"
```

#### Visual Hierarchy:
```
- "Make [element] more prominent in the visual hierarchy"
- "Reduce emphasis on [less important elements]"
- "Create better flow from [element A] to [element B]"
- "Add visual cues to guide user attention to [key areas]"
```

## Platform-Specific Prompting

### 1. Mobile-First Prompting

#### Mobile Optimization:
```
Design primarily for mobile devices with [screen size] constraints. 
Use [touch-friendly elements] with [appropriate sizing] and [mobile navigation patterns]. 
Ensure [fast loading] and [thumb-friendly interactions].
```

#### Progressive Enhancement:
```
Start with mobile design and enhance for larger screens. 
Add [desktop-specific features] while maintaining [core mobile functionality]. 
Use [responsive breakpoints] to optimize for [different screen sizes].
```

### 2. Desktop Application Prompting

#### Desktop Patterns:
```
Design for desktop with [keyboard shortcuts/hover states/multi-window support]. 
Include [desktop-specific UI patterns] and optimize for [mouse/trackpad interactions]. 
Consider [power user features] and [professional workflows].
```

#### Productivity Focus:
```
Optimize for productivity with [efficient layouts/quick actions/keyboard navigation]. 
Include [customizable interfaces/saved states/batch operations] for power users.
```

### 3. Cross-Platform Consistency

#### Unified Design System:
```
Create a design that works across [platforms] while respecting [platform conventions]. 
Maintain [brand consistency] while adapting [interaction patterns] for each platform.
```

## Quality Assurance Prompts

### 1. Accessibility Integration

#### WCAG Compliance:
```
Ensure the design meets WCAG 2.1 AA standards with [proper contrast ratios/keyboard navigation/screen reader support]. 
Include [alt text considerations/focus indicators/semantic structure].
```

#### Inclusive Design:
```
Design for users with [specific accessibility needs] including [visual/motor/cognitive considerations]. 
Ensure [multiple interaction methods] and [clear, simple interfaces].
```

### 2. Performance Considerations

#### Optimization Prompts:
```
Design with performance in mind, minimizing [heavy elements/complex animations/large assets]. 
Prioritize [critical content] and design for [progressive loading/fast interactions].
```

### 3. Responsive Design Validation

#### Multi-Device Testing:
```
Ensure the design works effectively on [device types] with [screen sizes] and [different orientations]. 
Test [touch interactions/hover states/navigation patterns] across platforms.
```

## Common Prompting Mistakes to Avoid

### 1. Vague Requirements
❌ **Bad**: "Make it look good"  
✅ **Good**: "Use a modern, professional aesthetic with clean lines and plenty of white space"

### 2. Missing Context
❌ **Bad**: "Create a form"  
✅ **Good**: "Create a contact form for a law firm website that builds trust and encourages inquiries"

### 3. Conflicting Instructions
❌ **Bad**: "Make it minimalist but also include lots of features and information"  
✅ **Good**: "Use minimalist design principles while organizing extensive features into clear, scannable sections"

### 4. Technology Assumptions
❌ **Bad**: "Make it work everywhere"  
✅ **Good**: "Design for modern browsers with progressive enhancement for older versions"

## Time Investment by Prompt Quality

### Basic Prompts (5-10 minutes):
- Simple, single-purpose interfaces
- Standard design patterns
- Minimal customization needed

### Enhanced Prompts (10-20 minutes):
- Multi-section applications
- Brand-specific styling
- Moderate interaction complexity

### Detailed Prompts (20-40 minutes):
- Complex, multi-page applications
- Custom design systems
- Advanced interactive features

### Experimental Prompts (40+ minutes):
- Innovative interface concepts
- Complex data visualizations
- Cutting-edge design exploration

Remember: The quality of your output is directly proportional to the specificity and clarity of your prompts. Invest time in crafting detailed, well-structured prompts for the best results.
