import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const App = () => {
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("");
  const [attackType, setAttackType] = useState("");
  const [results, setResults] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [newIncident, setNewIncident] = useState({
    title: "",
    description: "",
    severity: "",
    attack_type: "",
  });
  const [incidentIdToUpdate, setIncidentIdToUpdate] = useState("");
  const [updatedIncident, setUpdatedIncident] = useState({
    title: "",
    description: "",
    severity: "",
    attack_type: "",
  });

    // Update the document title when the page loads or the app changes
    useEffect(() => {
        document.title = "Incident Dashboard - Manage Incidents";
      }, []);

  useEffect(() => {
    searchIncidents();
  }, [page]);

  const searchIncidents = async () => {
    const response = await axios.get("http://localhost:8001/search", {
      params: { query, severity, attack_type: attackType, page, size: 10 },
    });
    setResults(response.data.results);
    setTotalPages(response.data.total_pages);
  };

  const handleAddIncident = async () => {
    // Validation for required fields
    if (!newIncident.title || !newIncident.description || !newIncident.severity || !newIncident.attack_type) {
      alert("All fields are required!");
      return;
    }

    const response = await axios.post("http://localhost:8001/incidents", newIncident);
    alert("Incident added: " + response.data.title);
    setNewIncident({ title: "", description: "", severity: "", attack_type: "" });
    searchIncidents();
  };

  const handleUpdateIncident = async () => {
    const response = await axios.put(`http://localhost:8001/incidents/${incidentIdToUpdate}`, updatedIncident);
    alert("Incident updated: " + response.data.title);
    setUpdatedIncident({ title: "", description: "", severity: "", attack_type: "" });
    setIncidentIdToUpdate("");
    searchIncidents();
  };

  const handleDeleteIncident = async (id) => {
    console.log("Deleting incident with ID:", id); // Check the ID here
    try {
        await axios.delete(`http://localhost:8001/incidents/${id}`);
        alert("Incident deleted.");
        searchIncidents(); // Refresh the list of incidents
    } catch (error) {
        console.error("Error deleting incident:", error);
        alert("Failed to delete incident.");
    }
};

  return (
    <div className="app-container">
      <h1 className="app-title">Incident Dashboard</h1>
      
      <div className="filters-container">
        <input
          className="search-input"
          type="text"
          placeholder="Search title"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select className="dropdown" onChange={(e) => setSeverity(e.target.value)}>
          <option value="">All Severities</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Critical">Critical</option>
        </select>
        <select className="dropdown" onChange={(e) => setAttackType(e.target.value)}>
            <option value="">All Attack Types</option>
            <option value="Unauthorized Access">Unauthorized Access</option>
            <option value="Phishing">Phishing</option>
            <option value="DoS">DoS (Denial of Service)</option>
            <option value="Privilege Escalation">Privilege Escalation</option>
            <option value="SQL Injection">SQL Injection</option>
            <option value="Cross-Site Scripting (XSS)">Cross-Site Scripting (XSS)</option>
            <option value="Malware">Malware</option>
            <option value="Man-in-the-Middle">Man-in-the-Middle</option>
            <option value="Cross-Site Request Forgery (CSRF)">Cross-Site Request Forgery (CSRF)</option>
            <option value="Social Engineering">Social Engineering</option>
        </select>
        <button className="search-button" onClick={searchIncidents}>Search</button>
      </div>

      <div className="incident-forms">
        <h3 className="form-title"><center>Add New Incident</center></h3>
        <div className="form-container">
          <input
            className="form-input"
            type="text"
            placeholder="Title"
            value={newIncident.title}
            onChange={(e) => setNewIncident({ ...newIncident, title: e.target.value })}
          />
          <textarea
            className="form-textarea"
            placeholder="Description"
            value={newIncident.description}
            onChange={(e) => setNewIncident({ ...newIncident, description: e.target.value })}
          />
          <input
            className="form-input"
            type="text"
            placeholder="Severity"
            value={newIncident.severity}
            onChange={(e) => setNewIncident({ ...newIncident, severity: e.target.value })}
          />
          <input
            className="form-input"
            type="text"
            placeholder="Attack Type"
            value={newIncident.attack_type}
            onChange={(e) => setNewIncident({ ...newIncident, attack_type: e.target.value })}
          />
          <button 
            className="form-button" 
            onClick={handleAddIncident} 
            disabled={!newIncident.title || !newIncident.description || !newIncident.severity || !newIncident.attack_type}
          >
            Add Incident
          </button>
        </div>
      </div>

      <h3 className="incident-list-title">Incidents</h3>
      <div className="incident-cards">
        {results.map((incident) => (
          <div key={incident.incident_id} className="incident-card">
            <h4 className="incident-title">{incident.title}</h4>
            <p className="incident-description">{incident.description}</p>
            <p className="incident-severity">Severity: {incident.severity}</p>
            <p className="incident-attack-type">Attack Type: {incident.attack_type}</p>
            <button className="delete-button" onClick={() => handleDeleteIncident(incident.incident_id)}>Delete</button>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button className="pagination-button" disabled={page <= 1} onClick={() => setPage(page - 1)}>
          Prev
        </button>
        <span className="pagination-info">{page} of {totalPages}</span>
        <button className="pagination-button" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
          Next
        </button>
      </div>
    </div>
  );
};

export default App;
