import React, { useState } from "react";

function UserForm({ onSubmit }) {
  const [name, setName] = useState("");
  const [gender, setGender] = useState("");
  const [age, setAge] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !gender || !age) {
      alert("Please fill all fields");
      return;
    }
    onSubmit({ name, gender, age });
  };

  return (
    <div className="form-container">
      <h2>Welcome to AI Health Assistant</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <select value={gender} onChange={(e) => setGender(e.target.value)}>
          <option value="">Select gender</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select>

        <input
          type="number"
          placeholder="Enter your age"
          value={age}
          onChange={(e) => setAge(e.target.value)}
        />

        <button type="submit">Continue</button>
      </form>
    </div>
  );
}

export default UserForm;
