type LogLevel = 'info' | 'warn' | 'error' | 'debug';

export class Logger {
  private static log(level: LogLevel, message: string, context?: Record<string, unknown>) {
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    // In production, this would send to Datadog/Sentry
    if (level === 'error') {
      console.error(formattedMessage, context || '');
    } else if (level === 'warn') {
      console.warn(formattedMessage, context || '');
    } else {
      console.log(formattedMessage, context || '');
    }
  }

  static info(message: string, context?: Record<string, unknown>) {
    this.log('info', message, context);
  }

  static warn(message: string, context?: Record<string, unknown>) {
    this.log('warn', message, context);
  }

  static error(message: string, error?: unknown, context?: Record<string, unknown>) {
    this.log('error', message, { error, ...context });
  }
}
