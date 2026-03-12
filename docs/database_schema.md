# Database Schema
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the persistent data model for the MVP. Agents must not invent persistent tables outside this file.

## 2. Database

- Engine: PostgreSQL
- Primary keys: UUID
- Timestamp fields: UTC timestamps
- Soft delete: not required for MVP unless added here later

## 3. Tables

### users

Purpose:
Store application accounts.

Columns:
- `id` uuid primary key
- `email` text not null unique
- `password_hash` text not null
- `full_name` text not null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

### offenders

Purpose:
Store user-selected offender snapshots for packet work.

Columns:
- `id` uuid primary key
- `sid` text not null
- `tdcj_number` text null
- `name` text not null
- `race` text null
- `gender` text null
- `age` integer null
- `current_facility` text null
- `projected_release_date` text null
- `parole_eligibility_date` text null
- `maximum_sentence_date` text null
- `visitation_eligible` boolean null
- `visitation_eligible_raw` text null
- `source` text not null default `Texas Department of Criminal Justice`
- `retrieved_at` timestamptz not null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Indexes and constraints:
- index on `sid`
- unique constraint on (`sid`, `retrieved_at`)

### parole_board_offices

Purpose:
Store office lookup data used for packet mailing.

Columns:
- `id` uuid primary key
- `office_code` text not null unique
- `office_name` text not null
- `address_line_1` text not null
- `address_line_2` text null
- `city` text not null
- `state` text not null
- `postal_code` text not null
- `phone` text null
- `notes` text null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

### parole_board_unit_mappings

Purpose:
Map offender unit/facility names to a parole board office.

Columns:
- `id` uuid primary key
- `unit_name` text not null unique
- `office_id` uuid not null references `parole_board_offices(id)`
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Temporary development routing rule:
- if an upstream source maps the same unit to multiple board offices, select the first board office in alphabetical order of `office_name`
- this is a temporary placeholder rule only, used so development can continue until real TDCJ routing logic is implemented

### packets

Purpose:
Store a user-owned parole packet draft.

Columns:
- `id` uuid primary key
- `user_id` uuid not null references `users(id)`
- `offender_id` uuid not null references `offenders(id)`
- `parole_board_office_id` uuid null references `parole_board_offices(id)`
- `status` text not null
- `sender_name` text null
- `sender_phone` text null
- `sender_email` text null
- `sender_relationship` text null
- `cover_letter_text` text null
- `final_pdf_storage_key` text null
- `final_pdf_generated_at` timestamptz null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Allowed `status` values:
- `draft`
- `generating_pdf`
- `ready`

### packet_sections

Purpose:
Store section-level packet content and completion state.

Columns:
- `id` uuid primary key
- `packet_id` uuid not null references `packets(id)`
- `section_key` text not null
- `title` text not null
- `notes_text` text null
- `is_populated` boolean not null default false
- `sort_order` integer not null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Constraints:
- unique (`packet_id`, `section_key`)

Allowed `section_key` values:
- `photos`
- `support_letters`
- `reflection_letter`
- `certificates_and_education`
- `future_employment`
- `parole_plan`
- `court_and_case_documents`
- `other_miscellaneous`

### documents

Purpose:
Store uploaded or scanned files associated with packet sections.

Columns:
- `id` uuid primary key
- `packet_id` uuid not null references `packets(id)`
- `packet_section_id` uuid not null references `packet_sections(id)`
- `filename` text not null
- `content_type` text not null
- `source` text not null
- `storage_key` text null
- `upload_status` text not null
- `file_size_bytes` bigint null
- `page_count` integer null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Allowed `source` values:
- `scanner`
- `upload`

Allowed `upload_status` values:
- `pending`
- `uploaded`
- `failed`

### notification_subscriptions

Purpose:
Store push notification device registrations.

Columns:
- `id` uuid primary key
- `user_id` uuid not null references `users(id)`
- `platform` text not null
- `device_token` text not null unique
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

Allowed `platform` values:
- `ios`
- `android`

## 4. Relationships

- one `user` has many `packets`
- one `user` has many `notification_subscriptions`
- one `offender` may be linked to many `packets`
- one `parole_board_office` may be linked to many `packets`
- one `parole_board_office` may have many `parole_board_unit_mappings`
- one `packet` has many `packet_sections`
- one `packet_section` has many `documents`

## 5. Seed Requirements

The MVP should support seed data for:
- packet section definitions and sort order
- parole board office records
- parole board unit-to-office mappings

## 6. Notes

- Offender data is a snapshot for packet creation, not a permanent source-of-truth replacement for TDCJ.
- Offense history may remain transient or be added later only after this document is updated.
- No additional analytics, scoring, or collaboration tables exist in MVP.
