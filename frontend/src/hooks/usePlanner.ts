import { useState } from 'react';
import { plannerService } from '../services';
import type { PlannerEvent, PlannerState } from "../types";

export function usePlannerChat() {
  const [state, setState] = useState<PlannerState>({
    is_running: false,
    events: [],
  });

  const sendMessage = async (message: string) => {
    setState(s => ({ ...s, is_running: true, error: undefined, final_answer: undefined }));
    
    try {
      await plannerService.sendMessage(message, (event: PlannerEvent) => {
        setState(s => {
          const newEvents = [...s.events, event];
          const newState = { ...s, events: newEvents };

          if (event.type === 'tool_start' || event.type === 'tool_end') {
            newState.current_step = event.step;
          } else if (event.type === 'final_answer') {
            newState.final_answer = event.content;
          } else if (event.type === 'error') {
            newState.error = event.content;
          }

          return newState;
        });
      });
    } catch (err: any) {
      setState(s => ({ ...s, error: err.message || 'An error occurred' }));
    } finally {
      setState(s => ({ ...s, is_running: false }));
    }
  };

  return {
    ...state,
    sendMessage,
  };
}
