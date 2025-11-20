import React, { useState } from "react";
import "./App.css";
import UserForm from "./UserForm";
import ChatInterface from "./ChatInterface";

function App() {
  const [userData, setUserData] = useState(null);

  return (
    <div className="app">
      {!userData ? (
        <UserForm onSubmit={setUserData} />
      ) : (
        <ChatInterface userData={userData} />
      )}
    </div>
  );
}

export default App;
