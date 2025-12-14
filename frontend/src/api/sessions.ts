import { apiClient } from './client';

export interface CreateSessionResponse {
  session_id: string;
  status: string;
}

export interface Review {
    id: string;
    agent_name: string;
    target_draft_id: string;
    summary: string;
    line_level_comments: any[];
    safety_score?: number;
    empathy_score?: number;
    clinical_score?: number;
    rationale: string;
}

export interface Draft {
    id: string;
    content: string;
    created_at: string;
    created_by: string;
    version_number: number;
}

export interface FoundryState {
    session_id: string;
    user_intent: string;
    current_draft?: Draft;
    draft_history: Draft[];
    reviews: Review[];
    safety_score?: number;
    empathy_score?: number;
    clinical_score?: number;
    iteration: number;
    max_iterations: number;
    status: "INIT" | "DRAFTING" | "REVIEWING" | "REVISING" | "AWAITING_HUMAN" | "APPROVED" | "FAILED" | "REJECTED";
    error?: string;
    scratchpads: { notes: Record<string, string> };
}

export const createSession = async (userIntent: string, userContext?: string): Promise<CreateSessionResponse> => {
  const response = await apiClient.post<CreateSessionResponse>('/sessions', {
    user_intent: userIntent,
    user_context: userContext,
  });
  return response.data;
};

export const getSessionState = async (sessionId: string): Promise<FoundryState> => {
  const response = await apiClient.get<FoundryState>(`/sessions/${sessionId}/state`);
  return response.data;
};

export const humanApprove = async (
    sessionId: string, 
    newContent: string, 
    action: "APPROVE_FINAL" | "APPROVE_CONTINUE" | "REQUEST_REVISION" | "REJECT",
    comments?: string
): Promise<{ status: string, session_id: string }> => {
    const response = await apiClient.post(`/sessions/${sessionId}/human_approve`, {
        new_content: newContent,
        action,
        comments
    });
    return response.data;
}
