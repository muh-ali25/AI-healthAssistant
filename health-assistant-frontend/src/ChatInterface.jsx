import React, { useState } from "react";

function ChatInterface({ userData }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input, top_k: 3 }),
      });

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const data = await response.json();
      const botMsg = {
        sender: "bot",
        text: data.answer || "Sorry, no answer available.",
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const botMsg = {
        sender: "bot",
        text: "Error connecting to server. Please check FastAPI is running.",
      };
      setMessages((prev) => [...prev, botMsg]);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <h2>
        Hi {userData.name}, age {userData.age}, how can I help with your health
        today?
      </h2>

      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={m.sender}>
            {m.text}
          </div>
        ))}
      </div>

      <div className="chat-controls">
        <input
          type="text"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
