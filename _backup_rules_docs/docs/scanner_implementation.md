# Scanner Implementation
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines scanner v1 for the mobile app.

Scanner v1 is intended to help users capture paper documents from a smartphone, produce upload-ready images, and attach them to the correct packet section.

## 2. Technology Direction

- mobile platform: React Native with Expo
- use Expo-compatible libraries whenever possible
- the scanner flow may use camera capture plus lightweight image processing
- do not require custom native modules unless Expo-compatible approaches are proven insufficient and the docs are updated first

## 3. Scanner v1 Scope

Scanner v1 must support:
- camera capture from the mobile app
- basic framing guidance
- retake flow
- simple crop/cleanup workflow when supported
- upload into a selected packet section

Scanner v1 does not require:
- OCR
- automatic document classification
- AI quality scoring
- multi-document batch intelligence beyond simple repeated capture

## 4. User Flow

1. user opens a packet section
2. user selects scan document
3. app requests camera permission if needed
4. user captures one or more pages
5. user reviews each capture
6. user accepts or retakes
7. app uploads accepted pages to the backend under the selected section

## 5. Capture Rules

- prefer portrait capture for printed documents
- encourage flat, well-lit captures
- preserve original image detail sufficient for print readability
- do not over-compress images before upload
- do not permanently store captures on-device after successful upload beyond temporary cache needs

## 6. File Handling

Accepted scanner output for MVP:
- JPEG image uploads
- PNG may be supported if produced by the capture pipeline, but JPEG is the default target

Each scan upload must create or attach to a document record under:
- packet
- section
- source=`scanner`

## 7. Mobile Responsibilities

The mobile scanner is responsible for:
- requesting permissions
- capturing images
- allowing review/retake
- sending files to the backend upload flow

The mobile scanner is not responsible for:
- PDF generation
- long-term storage logic
- parole packet composition

## 8. Backend Responsibilities

The backend is responsible for:
- issuing upload targets or accepting uploads
- storing file metadata
- associating scans to packet sections
- making scanned files available for final PDF generation

## 9. Failure Handling

If permission is denied:
- show a clear explanation
- allow retry after the user changes settings

If upload fails:
- preserve local temporary reference long enough to retry in-session
- return a structured error
- allow retry without losing section context

## 10. MVP Acceptance

Scanner v1 is complete when:
- user can scan a document page from a phone
- user can retake before upload
- uploaded scan is attached to the selected section
- uploaded scan appears in the section document list
- scanned page can be included later in final PDF generation
