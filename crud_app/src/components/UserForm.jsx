import { useState, useEffect } from "react";

export default function UserForm({ addUser, editingUser, updateUser }) {
  const [form, setForm] = useState({ name: "", mail: "" });

  useEffect(() => {
    if (editingUser) {
      setForm({ name: editingUser.name, mail: editingUser.mail, id: editingUser.id });
    } else {
      setForm({ name: "", mail: "" });
    }
  }, [editingUser]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name) return alert("Please enter a name");
    if (editingUser) updateUser(form);
    else addUser(form);
    setForm({ name: "", mail: "" });
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
      <input
        type="text"
        placeholder="Name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
      />
      <input
        type="email"
        placeholder="Email"
        value={form.mail}
        onChange={(e) => setForm({ ...form, mail: e.target.value })}
      />
      <button type="submit">{editingUser ? "Update" : "Add"}</button>
    </form>
  );
}
