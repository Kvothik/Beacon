# TDCJ Lookup Adapter

This document defines the backend integration used to retrieve offender data from the Texas Department of Criminal Justice (TDCJ) public offender search system.

There is **no official API**. Data must be retrieved through the public search interface.

The backend implements a **server-side adapter** that:

1. submits the search form
2. parses the search results page
3. extracts SID identifiers
4. retrieves the offender detail page
5. normalizes the data into a structured offender object

This adapter is the **single source of truth** for inmate lookup.

---

# 1. Source System

TDCJ Public Offender Search

Search page:

https://inmate.tdcj.texas.gov/InmateSearch/search.action

Detail page:

https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid={SID}

---

# 2. Search Requirements

The search form requires **one of the following inputs**:

• TDCJ number  
• SID number  
• last name AND first name initial

For the application workflow we use:

```
lastName
firstName
race=ALL
gender=ALL
```

Example:

```
lastName=Smith
firstName=J
```

---

# 3. Search Request

HTTP Method:

```
POST
```

Endpoint:

```
https://inmate.tdcj.texas.gov/InmateSearch/search.action
```

Content Type:

```
application/x-www-form-urlencoded
```

Example POST body:

```
page=index
lastName=Smith
firstName=J
race=ALL
gender=ALL
tdcj=
sid=
```

---

# 4. Search Results Page

The response contains an HTML table with rows for each matching offender.

Columns include:

| Field | Description |
|------|-------------|
Name | Offender name |
TDCJ Number | Department ID |
Race | Race code |
Gender | M/F |
Projected Release Date | Expected release |
Unit of Assignment | Current facility |
Age | Current age |

Example table row:

```
<tr>
<th class='rowHeader'>
<a href="/InmateSearch/viewDetail.action?sid=05192675">SMITH,J C</a>
</th>
<td>02394240</td>
<td>W</td>
<td>M</td>
<td>2041-12-10</td>
<td>ELLIS</td>
<td>52</td>
</tr>
```

Important extraction:

```
sid=05192675
```

The **SID parameter is required to retrieve full offender details.**

---

# 5. Pagination

Search results may contain multiple pages.

Pagination form:

```
form_paginate
```

Hidden fields:

```
currentPage
totalPageCount
lastSearch
```

Next page requests POST back to:

```
/InmateSearch/search.action
```

Adapter must support pagination if needed.

---

# 6. Detail Page

Endpoint:

```
GET https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid={SID}
```

Example:

```
https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid=05192675
```

---

# 7. Fields Available From Detail Page

Primary offender fields:

| Field | Description |
|------|-------------|
SID Number | State ID |
TDCJ Number | Department ID |
Name | Offender name |
Race | Race code |
Gender | M/F |
Age | Age |
Maximum Sentence Date | Maximum term |
Current Facility | Assigned unit |
Projected Release Date | Estimated release |
Parole Eligibility Date | Eligibility |
Visitation Eligible | YES/NO |

---

# 8. Offense History

The detail page contains an offense history table.

Example row:

```
<tr>
<th>1993-11-03</th>
<td>INDECENCY W/CHILD</td>
<td>1997-07-08</td>
<td>VAN ZANDT</td>
<td>14,732</td>
<td>8-00-00</td>
</tr>
```

Fields:

| Field | Description |
|------|-------------|
Offense Date | Date offense occurred |
Offense | Offense name |
Sentence Date | Sentencing date |
County | County |
Case Number | Court case |
Sentence | Sentence length |

Multiple rows may exist.

---

# 9. Normalized Offender Object

The adapter must convert scraped data into a structured object.

Example:

```json
{
  "sid": "05192675",
  "tdcj_number": "02394240",
  "name": "SMITH,J C",
  "race": "W",
  "gender": "M",
  "age": 52,
  "facility": "ELLIS",
  "projected_release_date": "2041-12-10",
  "parole_eligibility_date": "2031-12-10",
  "visitation_eligible": true,
  "offenses": []
}
```

Offenses:

```json
{
  "offense_date": "",
  "offense": "",
  "sentence_date": "",
  "county": "",
  "case_number": "",
  "sentence": ""
}
```

---

# 10. Backend Adapter Responsibilities

The backend service must:

1. submit search request
2. parse results table
3. extract SID identifiers
4. fetch detail page
5. parse offender fields
6. parse offense history
7. normalize response object

Adapter implementation location:

```
backend/app/services/tdcj_lookup_service.py
```

---

# 11. Constraints

The adapter must:

• throttle requests  
• avoid aggressive scraping  
• handle pagination  
• handle missing data  
• handle "NOT AVAILABLE" values  

The system must **never block or crash due to parsing errors.**

---

# 12. Error Handling

The adapter must handle:

| Error | Response |
|------|----------|
No search results | return empty list |
Multiple results | require user selection |
Invalid SID | return structured error |
HTML structure change | return parser error |
Network failure | retry with backoff |

Errors must return structured API responses.

---

# 13. Data Freshness

TDCJ states that the site updates:

• daily on weekdays  
• multiple times on visitation days  

The adapter should **not cache data longer than necessary**.

---

# 14. Integration Point

Responsible backend module:

```
backend/app/services/tdcj_lookup_service.py
```

This module handles all communication with the TDCJ offender search system.