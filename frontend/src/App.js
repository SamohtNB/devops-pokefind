// src/App.js
import { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setResult('');
    setError('');
    if (selected) {
      setFile(selected);
      setPreviewUrl(URL.createObjectURL(selected));
    }
  };

  const handlePredict = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    setResult('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('http://localhost:8000/predict/', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error(`Erreur ${res.status}`);
      const data = await res.json();
      setResult(data.pokemon);
    } catch (err) {
      setError("Impossible de contacter le service de prédiction.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>PokeDux</h1>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="file-input"
      />
      {previewUrl && (
        <img
          src={previewUrl}
          alt="Aperçu"
          className="preview-image"
        />
      )}
      <button
        onClick={handlePredict}
        disabled={!file || loading}
        className="btn-predict"
      >
        {loading ? 'Chargement...' : 'Prédire'}
      </button>
      {result && <p className="result">Il s'agit de : {result}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default App;