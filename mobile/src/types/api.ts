export type ApiError = {
  error: {
    code: string;
    message: string;
    details: unknown;
    retryable: boolean;
  };
};
