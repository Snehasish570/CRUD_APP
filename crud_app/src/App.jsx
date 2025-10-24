import { useState, useEffect } from "react";
import UserForm from "./components/UserForm";
import UserTable from "./components/UserTable";
import "./App.css";

const API_URL = "http://127.0.0.1:5000/api/items";

function App() {
  const [users, setUsers] = useState([]);
  const [editingUser, setEditingUser] = useState(null);

  // ✅ Fetch all users
  const fetchUsers = async () => {
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setUsers(data);
    } catch (err) {
      console.error("Failed to fetch users:", err);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // ✅ Add user
  const addUser = async (user) => {
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });

      const data = await res.json();

      if (!res.ok) {
        // backend sends { error: "Email already exists" }
        alert(data.error || "Error adding user");
        return;
      }

      await fetchUsers();
      alert("✅ User added successfully!");
    } catch (err) {
      alert("❌ Failed to add user");
      console.error(err);
    }
  };

  // ✅ Update user
  const updateUser = async (user) => {
    try {
      const res = await fetch(`${API_URL}/${user.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "Error updating user");
        return;
      }

      await fetchUsers();
      setEditingUser(null);
      alert("✅ User updated successfully!");
    } catch (err) {
      alert("❌ Failed to update user");
      console.error(err);
    }
  };

  // ✅ Delete user
  const deleteUser = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;

    try {
      const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete user");

      await fetchUsers();
      alert("🗑️ User deleted successfully!");
    } catch (err) {
      alert("❌ Error deleting user");
      console.error(err);
    }
  };

  // ✅ Edit user
  const editUser = (user) => {
    setEditingUser(user);
  };

  return (
    <div className="App">
      <h1>📋 Interactive User Dashboard</h1>
      <UserForm
        addUser={addUser}
        editingUser={editingUser}
        updateUser={updateUser}
      />
      <UserTable
        users={users}
        deleteUser={deleteUser}
        editUser={editUser}
      />
    </div>
  );
}

export default App;
