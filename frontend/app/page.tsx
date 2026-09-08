"use client";

import { useChat } from "ai/react";

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } =
    useChat({
      api: "/api/chat",
      streamProtocol: "text",
    });

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>AI Chatbot Sample</h1>
      </header>

      <div className="chat-messages">
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            {m.content}
          </div>
        ))}
        {isLoading && <div className="message assistant">…</div>}
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
