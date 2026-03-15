# PDF Specification
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the required structure and ordering of the generated parole packet PDF. Agents must not change packet ordering or composition outside this file.

## 2. Output Goal

The system generates one print-ready PDF suitable for physical mailing to the correct parole board office.

PDF generation occurs on the backend only.

## 3. Required PDF Sections

The final PDF must contain, in this order:

1. cover letter
2. photos section divider page, then photos content if populated
3. support letters section divider page, then support letters content if populated
4. reflection letter section divider page, then reflection letter content if populated
5. certificates and education section divider page, then certificates and education content if populated
6. future employment section divider page, then future employment content if populated
7. parole plan section divider page, then parole plan content if populated
8. court and case documents section divider page, then court and case documents content if populated
9. other or miscellaneous section divider page, then other or miscellaneous content if populated

Unpopulated sections must not appear in the final PDF.

## 4. Cover Letter Requirements

The cover letter must include:
- sender name
- sender phone if provided
- sender email if provided
- sender relationship if provided
- offender name
- offender SID or TDCJ number when available
- assigned facility/unit when available
- parole board office name
- mailing address for the board office

The tone must be formal, respectful, and professional.

The system must not generate legal claims about innocence.

## 5. Divider Page Requirements

Each populated packet section must begin with a divider page.

Divider page content:
- section title
- optional short subtitle such as `Supporting Materials`

Divider pages should be visually simple, professional, and easy to separate while printed.

## 6. Section Content Rules

### Photos
- include uploaded image pages in stored order

### Support Letters
- include uploaded PDFs/images and any generated text pages in stored order

### Reflection Letter
- include user-entered text rendered as formatted PDF pages and any uploaded supporting pages

### Certificates and Education
- include uploaded documents in stored order

### Future Employment
- include uploaded documents and text content in stored order

### Parole Plan
- include uploaded documents and text content in stored order

### Court and Case Documents
- include uploaded documents and text content in stored order
- if text guidance is rendered, it must remain neutral and must not argue innocence

### Other or Miscellaneous
- include uploaded documents and text content in stored order

## 7. Rendering Rules

- page size: US Letter
- orientation: portrait by default
- margins: consistent and print-safe
- fonts: standard readable serif or sans-serif fonts embeddable on the backend
- preserve image readability over aggressive resizing
- preserve document page order from the packet section record order

## 8. Metadata and File Naming

Default filename:
- `parole-packet.pdf`

Suggested metadata fields:
- title: `Texas Parole Packet`
- author: application backend service
- subject: offender parole packet

## 9. Generation Failure Rules

If any required input for generation is missing:
- return a structured error response
- do not generate a partial final PDF represented as complete

If optional section content is missing:
- omit that section entirely

## 10. Anti-Hallucination Rules

- do not reorder packet sections outside this document
- do not insert extra sections
- do not generate unofficial legal disclaimers not requested by the product docs
- do not perform client-side PDF generation
