North Star Architecture Document
Audited build documentation for the Texas Parole Packet Builder
1. Mission
Build a professional mobile application that helps family members of incarcerated individuals in Texas assemble, review, and export a parole packet suitable for physical mailing to the correct parole board office. The app must reduce confusion, improve packet quality, and keep the user on a guided path from offender lookup through final PDF export.
2. Product Outcome
A successful user can identify their loved one, see the correct board office and mailing information, complete each packet section with guided instructions, scan or upload supporting materials, generate a cover letter, and export a single print-ready PDF with section divider pages in the correct order.
3. Target Users
Primary user: family members or close supporters of incarcerated individuals in Texas.
Most users are non-technical and may complete the entire workflow from a smartphone.
Users need strong guidance, plain language, and a polished but calm interface.
4. Platforms and Technology Direction
Mobile application
React Native with Expo for a shared iOS and Android codebase.
TypeScript throughout the mobile codebase.
Use Expo-compatible packages unless a documented exception is required.
Backend application
FastAPI in Python for API endpoints and server-side orchestration.
PostgreSQL as the system of record.
Cloud object storage for scans and uploaded documents.
PDF generation on the server so output is consistent across devices.
Notifications
Push notifications delivered through Firebase Cloud Messaging or equivalent Expo-compatible flow.
5. Core Functional Requirements
Offender lookup
The app must support Texas Department of Criminal Justice offender lookup. The implementation must not assume an official public JSON API exists. If scraping or proxying is required, that decision must be isolated to a backend integration layer. The UI must allow search, selection, and display of core offender details relevant to packet creation.
Parole board locator
Using the offender's assigned unit, the system must identify the correct Texas Board of Pardons and Paroles office and show mailing address and contact details required for packet submission.
Packet builder
The user must complete a structured packet made of sections. Each section includes in-app guidance that explains what to include and what to avoid.
Smart scanner
The app must allow mobile capture of paper documents with framing guidance, image cleanup, and upload into the correct packet section.
Cover letter generator
The system must generate a formal introductory cover letter using family contact details, offender details, and the correct board office information.
PDF export
The final output is a single PDF intended for printing and mailing. The packet must insert a section title page before the content of each populated section.
6. Packet Sections
Photos
Support Letters
Reflection Letter
Certificates and Education
Future Employment
Parole Plan
Court and Case Documents
Other or Miscellaneous
7. Section Guidance Requirements
Each section screen must contain concise, persuasive guidance. The guidance must help users improve packet quality without making legal claims on their behalf. For the Court and Case Documents section, the guidance must explicitly warn against using the packet to argue innocence; it should emphasize accountability and responsibility.
8. UX and Design Direction
The visual design should feel trustworthy, serious, and professional. Use large tap targets, obvious progress indicators, plain-language labels, and minimal clutter. The app should favor calm spacing and clear hierarchy over flashy design elements. The final review screen must make it obvious which sections are complete and which still need work.
9. Non-Functional Requirements
Cross-platform support for iOS and Android.
Reliable storage and retrieval of uploaded files.
High-quality PDF output suitable for printing.
Graceful handling of network failures and partial progress.
Modular architecture so AI agents can build the product incrementally.
10. Delivery Constraints for AI Agents
Do not redesign the architecture unless the documentation is updated first.
Do not invent endpoints outside api_contracts.md.
Do not invent tables outside database_schema.md.
Do not change packet ordering outside pdf_spec.md.
Do not violate system_invariants.md.
11. MVP Scope
The MVP includes authentication, offender lookup, parole board lookup, packet builder shell, section data entry, document upload, scanner v1, cover letter generation, final review, and PDF export. AI-assisted packet scoring, advanced analytics, and richer collaboration features are deferred.
12. Acceptance Definition
The audited MVP is successful when a user can create an account, select an offender, see the correct office, complete packet sections, upload or scan documents, generate a cover letter, and export a correctly ordered PDF packet that is ready to print and mail.