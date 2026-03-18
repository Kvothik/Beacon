TDCJ HTML Parser Spec

Purpose
This document defines the exact parsing rules for the TDCJ inmate lookup integration so AI agents and backend code do not guess at HTML structure or invent selectors.

The backend must treat the TDCJ website as a server-rendered HTML source and normalize the parsed results into stable internal JSON.

Source Pages
Search form page:
POST https://inmate.tdcj.texas.gov/InmateSearch/search.action

Detail page:
GET https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid=<SID>

Parole review page:
GET https://inmate.tdcj.texas.gov/InmateSearch/reviewDetail.action?sid=<SID>&tdcj=<TDCJ>&fullName=<ENCODED_NAME>

Search Request Parameters
Use application/x-www-form-urlencoded with:
page=index
lastName=<string>
firstName=<string>
tdcj=<string>
sid=<string>
gender=ALL
race=ALL
btnSearch=Search

Search rules:
valid input is either lastName + first initial of firstName, or tdcj, or sid
do not omit page=index
use gender=ALL and race=ALL unless future requirements explicitly add filtering

Search Results Page Parsing
Page identification
A valid search results page can be identified by:
title containing: TDCJ Inmate Search - Search Result Listing
h1 containing: Inmate Information Search Result(s)

Primary results table
Use the first table with class:
table.tdcj_table

Within that table, parse:
thead for column names
tbody tr for result rows

Expected columns
Each result row contains these columns in order:
1. Name
2. TDCJ Number
3. Race
4. Gender
5. Projected Release Date
6. Unit of Assignment
7. Age

Row parsing rules
For each row:
Name is the text content of the anchor in the first cell
SID is extracted from the href in the first cell anchor
detail_url is the absolute URL built from the href
TDCJ Number is the second cell text
Race is the third cell text
Gender is the fourth cell text
Projected Release Date is the fifth cell text
Unit is the sixth cell text
Age is the seventh cell text parsed as integer when possible

Name cell selector
Preferred selector:
table.tdcj_table tbody tr th.rowHeader a

Fallback selector:
table.tdcj_table tbody tr th a

SID extraction rule
Extract SID from:
/InmateSearch/viewDetail.action?sid=<SID>

The SID must be parsed from the sid query parameter.
Do not attempt to derive SID from visible text.

Search results normalized shape
Each parsed result row must normalize to:

{
  "name": "SMITH,J C",
  "sid": "05192675",
  "tdcj_number": "02394240",
  "race": "W",
  "gender": "M",
  "projected_release_date": "2041-12-10",
  "unit": "ELLIS",
  "age": 52,
  "detail_url": "https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid=05192675"
}

Pagination Parsing
Pagination indicators
The results page contains a hidden form:
form#form_paginate

Parse these hidden inputs:
lastSearch
currentPage
totalPageCount

Pagination rules
currentPage is the current results page number
totalPageCount is the total number of pages
lastSearch contains the serialized prior search criteria
if totalPageCount > 1, the backend may fetch additional pages only when needed
do not eagerly crawl every page unless the user explicitly requests more results

Pagination request behavior
To request another page, submit the pagination form back to:
POST /InmateSearch/search.action

Use:
lastSearch
currentPage=<target page number>
totalPageCount=<known total>

Detail Page Parsing
Page identification
A valid detail page can be identified by:
title containing: TDCJ Inmate Search - Inmate Details
h1 containing: Inmate Information Details

Summary field parsing
The detail page exposes labeled values in the main content area.
Parse these labels exactly:
SID Number
TDCJ Number
Name
Race
Gender
Age
Maximum Sentence Date
Current Facility
Projected Release Date
Parole Eligibility Date
Inmate Visitation Eligible

Detail parsing rules
SID Number is the canonical sid
TDCJ Number is the canonical tdcj_number
Current Facility should be captured as plain text, not as the linked URL only
Projected Release Date should preserve values like actual dates or text when present
Parole Eligibility Date should preserve text exactly as displayed
Inmate Visitation Eligible should normalize to true for YES and false for NO when possible, while preserving raw text too

Scheduled release section
Parse these text blocks:
Scheduled Release Date
Scheduled Release Type
Scheduled Release Location

These may contain “Will be determined...” or “Inmate is not scheduled...” text.
Preserve them as raw text fields.

Parole review link
Extract the parole review link from the anchor text:
Parole Review Information

Store:
parole_review_url as absolute URL

Offense History Table Parsing
Table identification
Parse the offense history table following the heading:
Offense History:

Expected columns:
1. Offense Date
2. Offense
3. Sentence Date
4. County
5. Case No.
6. Sentence (YY-MM-DD)

Offense row rules
For each offense row normalize to:

{
  "offense_date": "1993-11-03",
  "offense": "INDECENCY W/CHILD",
  "sentence_date": "1997-07-08",
  "county": "VAN ZANDT",
  "case_number": "14,732",
  "sentence_length": "8-00-00"
}

Cleanup rules
trim whitespace
remove stray template remnants such as closing tags displayed in text if present
preserve text exactly when uncertainty exists instead of guessing

Normalized Detail Shape
A fully parsed offender detail should normalize to:

{
  "sid": "05192675",
  "tdcj_number": "02394240",
  "name": "SMITH,J C",
  "race": "W",
  "gender": "M",
  "age": 52,
  "maximum_sentence_date": "2041-12-10",
  "current_facility": "ELLIS",
  "projected_release_date": "2041-12-10",
  "parole_eligibility_date": "2031-12-10",
  "visitation_eligible": true,
  "visitation_eligible_raw": "YES",
  "scheduled_release_date_text": "Inmate is not scheduled for release at this time.",
  "scheduled_release_type_text": "Will be determined when release date is scheduled.",
  "scheduled_release_location_text": "Will be determined when release date is scheduled.",
  "parole_review_url": "https://inmate.tdcj.texas.gov/InmateSearch/reviewDetail.action?sid=05192675&tdcj=02394240&fullName=SMITH%2CJ+C",
  "offense_history": []
}

Freshness and Source Metadata
Every normalized response should also include:
source = "Texas Department of Criminal Justice"
retrieved_at = ISO timestamp
source_note = "Information provided is updated once daily during weekdays and may not reflect the true current status or location."

Error Handling
No results
If the page returns no offender rows:
return an empty results array
preserve original search criteria
do not throw a parser exception

Parser mismatch
If expected tables or labels are missing:
return a structured parser error
log the raw HTML snapshot internally
do not invent missing fields

Partial data
If some fields are missing:
return null for the normalized field
preserve any raw text that was found
do not infer or fabricate values

Anti-Hallucination Rules
Never invent fields not present in the TDCJ HTML
Never derive SID from name or TDCJ number
Never guess parole board office from HTML on these pages
Never assume projected release date equals maximum sentence date
Never assume the offense history table is complete legal case history beyond what is shown
Never change selector strategy without updating this document

Recommended Backend Parsing Flow
1. Submit search request to search.action
2. Parse result rows from table.tdcj_table
3. Return a candidate list to the app
4. After user selects a candidate, fetch viewDetail.action using sid
5. Parse labeled summary fields
6. Parse offense history table
7. Extract parole review link
8. Normalize to internal JSON
9. Attach source metadata and timestamps

Recommended Libraries
Python backend recommendations:
httpx or requests for HTTP
beautifulsoup4 or lxml for HTML parsing
urllib.parse for SID extraction from href values

Avoid:
regex-only HTML parsing for full-page extraction
client-side scraping in the mobile app
speculative selector inference by AI agents

Documentation Update Rule
If TDCJ changes the HTML structure:
update this file first
then update parser code
then update tests
do not silently patch selectors without documentation changes