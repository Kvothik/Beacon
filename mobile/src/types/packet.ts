export type PacketSummary = {
  id: string;
  status: 'draft' | 'generating_pdf' | 'ready';
  offender_sid: string;
  offender_name: string;
  offender_tdcj_number: string | null;
  current_facility: string | null;
  parole_board_office_code: string | null;
  created_at: string;
  updated_at: string;
};

export type PacketCreateRequest = {
  offender_sid: string;
  offender_name: string;
  offender_tdcj_number?: string | null;
  current_facility?: string | null;
  parole_board_office_code?: string | null;
};

export type PacketSectionState = {
  section_key:
    | 'photos'
    | 'support_letters'
    | 'reflection_letter'
    | 'certificates_and_education'
    | 'future_employment'
    | 'parole_plan'
    | 'court_and_case_documents'
    | 'other_miscellaneous';
  title: string;
  is_populated: boolean;
  sort_order: number;
};
