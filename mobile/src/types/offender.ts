export type OffenderSearchRequest = {
  last_name?: string | null;
  first_name_initial?: string | null;
  tdcj_number?: string | null;
  sid?: string | null;
  page?: number;
};

export type OffenderSummary = {
  sid: string;
  name: string;
  tdcj_number: string | null;
  race: string | null;
  gender: string | null;
  projected_release_date: string | null;
  unit: string | null;
  age: number | null;
  detail_url: string;
};

export type OffenderSearchPagination = {
  current_page: number;
  total_pages: number;
  has_more: boolean;
};

export type OffenderSearchResponse = {
  results: OffenderSummary[];
  pagination: OffenderSearchPagination;
  source: string;
  retrieved_at: string;
};

export type OffenseHistoryEntry = {
  offense_date: string | null;
  offense: string | null;
  sentence_date: string | null;
  county: string | null;
  case_number: string | null;
  sentence_length: string | null;
};

export type OffenderDetail = {
  sid: string;
  tdcj_number: string | null;
  name: string | null;
  race: string | null;
  gender: string | null;
  age: number | null;
  maximum_sentence_date: string | null;
  current_facility: string | null;
  projected_release_date: string | null;
  parole_eligibility_date: string | null;
  visitation_eligible: boolean | null;
  visitation_eligible_raw: string | null;
  scheduled_release_date_text: string | null;
  scheduled_release_type_text: string | null;
  scheduled_release_location_text: string | null;
  parole_review_url: string | null;
  offense_history: OffenseHistoryEntry[];
  source: string;
  retrieved_at: string;
  source_note: string;
};

export type ParoleBoardOffice = {
  office_code: string;
  office_name: string;
  address_lines: string[];
  city: string;
  state: string;
  postal_code: string;
  phone: string | null;
  notes: string | null;
};
