<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  const API_URL = "https://rocket-pitch-backend.onrender.com"; // Your backend URL
  
  let pitches = [];
  let isLoading = true;
  let errorMessage = "";
  
  onMount(async () => {
    try {
      const response = await axios.get(`${API_URL}/gallery`);
      pitches = response.data;
      isLoading = false;
    } catch (error) {
      console.error("Error loading gallery:", error);
      errorMessage = "Failed to load pitches. Please try again later.";
      isLoading = false;
    }
  });
  
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }
</script>

<div class="gallery-container">
  <h1>Student Pitch Gallery</h1>
  
  {#if isLoading}
    <div class="loading">Loading pitches...</div>
  {:else if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {:else if pitches.length === 0}
    <div class="empty-gallery">
      <p>No pitches have been submitted yet. Be the first to share your pitch!</p>
    </div>
  {:else}
    <div class="pitch-grid">
      {#each pitches as pitch}
        <div class="pitch-card">
          <div class="pitch-header">
            <h3>{pitch.title}</h3>
            <div class="score-badge">{pitch.overallScore}/100</div>
          </div>
          <div class="pitch-metadata">
            <span>By: {pitch.name}</span>
            <span>Date: {formatDate(pitch.dateSubmitted)}</span>
          </div>
          <p class="pitch-description">{pitch.description}</p>
          <div class="pitch-footer">
            <a href={`/gallery/${pitch.id}`} class="view-button">View Details</a>
            <span class="comment-count">{pitch.comments.length} Comments</span>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .gallery-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  h1 {
    color: #2c3e50;
    margin-bottom: 30px;
    text-align: center;
  }
  
  .loading, .error-message, .empty-gallery {
    text-align: center;
    padding: 40px;
    background: #f8f9fa;
    border-radius: 8px;
    margin: 20px 0;
  }
  
  .error-message {
    color: #e74c3c;
  }
  
  .pitch-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  .pitch-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    padding: 20px;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .pitch-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }
  
  .pitch-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .pitch-header h3 {
    margin: 0;
    color: #2c3e50;
  }
  
  .score-badge {
    background: #3498db;
    color: white;
    font-weight: bold;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 14px;
  }
  
  .pitch-metadata {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
  }
  
  .pitch-description {
    color: #34495e;
    margin-bottom: 20px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .pitch-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .view-button {
    background: #3498db;
    color: white;
    padding: 8px 15px;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 500;
    transition: background 0.2s;
  }
  
  .view-button:hover {
    background: #2980b9;
  }
  
  .comment-count {
    color: #7f8c8d;
    font-size: 14px;
  }
  
  @media (max-width: 768px) {
    .pitch-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
