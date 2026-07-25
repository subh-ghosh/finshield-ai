export class ApplicationError extends Error {
  constructor(public message: string, public code?: string) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class NetworkError extends ApplicationError {
  constructor(message = 'A network error occurred.') {
    super(message, 'NETWORK_ERROR');
  }
}

export class FallbackActivatedError extends ApplicationError {
  constructor(message = 'Backend unavailable. Falling back to local data source.') {
    super(message, 'FALLBACK_ACTIVATED');
  }
}

export class AuthenticationError extends ApplicationError {
  constructor(message = 'Unauthorized access.') {
    super(message, 'UNAUTHORIZED');
  }
}

export class NotFoundError extends ApplicationError {
  constructor(message = 'Resource not found.') {
    super(message, 'NOT_FOUND');
  }
}
