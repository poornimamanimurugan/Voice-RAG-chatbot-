Voice RAG Chatbot Daily Update (June 29, 2026)

1. Switched the chatbot's AI brain from Anthropic Claude to Groq's Llama 3.1 model -- this gives faster responses and is free to use
2. Added a login screen so users sign in before they can chat -- no more open access to anyone
3. Created two user roles: Admin (can upload/manage documents) and regular User (can only chat)
4. Updated all documentation and setup guides to reflect the new AI provider (Groq instead of Claude/Anthropic)
5. Explainer discussion on how vector databases work vs regular databases -- used to search documents by meaning, not just keywords
6. Explainer discussion on how to prevent AI from making up false information -- solution is to give it real documents to reference (RAG approach already in place)
7. Explainer discussion on Top P and Top K -- these are settings that control how random or focused the AI's word choices are
8. Explainer discussion on guardrails -- safety rules that check user questions and AI answers for inappropriate or unsafe content
9. Explainer discussion on how many tokens (words) each conversation uses -- roughly 900-2,250 tokens per question, 15k-25k for a full session
10. Explainer discussion on how to measure chatbot speed -- measured by time to first word and words per second

Future Updates
- Tighten requirements in the system prompt so the AI always cites document sources
- Add input guardrails to block questions that try to bypass the AI's instructions
- Add output guardrails to verify the AI only answers from the provided documents
- Improve document management to show which documents were used for each answer
- Explore adding multiple AI model options that users can switch between
