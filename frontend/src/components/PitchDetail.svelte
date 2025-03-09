<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  const API_URL = "https://rocket-pitch-backend.onrender.com"; // Your backend URL
  
  export let pitchId;
  
  let pitch = null;
  let isLoading = true;
  let errorMessage = "";
  let newComment = "";
  let authorName = "";
  
  onMount(async () => {
    await loadPitchDetails();
  });
  
  async function loadPitchDetails() {
    try {
      const response = await axios.get(`${API_URL}/gallery`);
      const allPitches = response.data;
      pitch = allPitches.find(p => p.id === pitchId);
      
      if (!pitch) {
        errorMessage = "Pitch not found";
      }
      
      isLoading = false;
    } catch (error) {
      console.error("Error loading pitch details:", error);
      errorMessage = "Failed to load pitch. Please try again later.";
      isLoading = false;
    }
  }
  
  async function submitComment() {
    if (!newComment.trim() || !authorName.trim()) {
      return;
    }
    
    try {
      await axios.post(`${API_URL}/gallery/${pitchId}/comment`, {
        comment: newComment,
        author: authorName
      });
      
      newComment = "";
      await loadPitchDetails(); // Reload to get the new comment
    } catch (error) {
      console.error("Error posting comment:", error);
      errorMessage = "Failed to post comment. Please try again.";
    }
  }
  
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
  }
</script>

<div class="pitch-detail">
  <a href="/gallery" class="back-link">← Back to Gallery</a>
  
  {#if isLoading}
    <div class="loading">Loading pitch details...</div>
  {:else if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {:else if pitch}
    <div class="pitch-header">
      <h1>{pitch.title}</h1>
      <div class="pitch-score">Overall Score: <span>{pitch.overallScore}/100</span></div>
    </div>
    
    <div class="pitch-meta">
      <div class="author">By: {pitch.name}</div>
      <div class="date">Submitted on: {formatDate(pitch.dateSubmitted)}</div>
    </div>
    
    <div class="pitch-content">
      <h2>Description</h2>
      <p>{pitch.description}</p>
      
      <h2>Analysis Results</h2>
      <div class="analysis-section">
        <!-- Display key parts of the analysis -->
        <div class="score-grid">
          <div class="score-item">
            <div class="score-label">Problem</div>
            <div class="score-value">{pitch.analysisResult?.sectionScores?.problem || 0}/100</div>
          </div>
          <div class="score-item">
            <div class="score-label">Solution</div>
            <div class="score-value">{pitch.analysisResult?.sectionScores?.solution || 0}/100</div>
          </div>
          <div class="score-item">
            <div class="score-label">Business</div>
            <div class="score-value">{pitch.analysisResult?.sectionScores?.business || 0}/100</div>
          </div>
          <div class="score-item">
            <div class="score-label">Financials</div>
            <div class="score-value">{pitch.analysisResult?.sectionScores?.financials || 0}/100</div>
          </div>
          <div class="score-item">
            <div class="score-label">Delivery</div>
            <div class="score-value">{pitch.analysisResult?.sectionScores?.delivery || 0}/100</div>
          </div>
        </div>
        
        {#if pitch.analysisResult?.summary}
          <h3>Summary</h3>
          <div class="summary-box">
            {#each pitch.analysisResult.summary as paragraph}
              <p>{paragraph}</p>
            {/each}
          </div>
        {/if}
      </div>
    </div>
    
    <div class="comments-section">
      <h2>Comments ({pitch.comments.length})</h2>
      
      <div class="comments-list">
        {#if pitch.comments.length === 0}
          <p class="no-comments">No comments yet. Be the first to provide feedback!</p>
        {:else}
          {#each pitch.comments as comment}
            <div class="comment">
              <div class="comment-header">
                <span class="comment-author">{comment.author}</span>
                <span class="comment-time">{formatDate(comment.timestamp)}</span>
              </div>
              <div class="comment-content">{comment.comment}</div>
            </div>
          {/each}
        {/if}
      </div>
      
      <div class="comment-form">
        <h3>Add Your Feedback</h3>
        <div class="form-group">
          <label for="author">Your Name</label>
          <input type="text" id="author" bind:value={authorName} placeholder="Enter your name">
        </div>
        <div class="form-group">
          <label for="comment">Your Comment</label>
          <textarea id="comment" bind:value={newComment} placeholder="Share your thoughts on this pitch..."></textarea>
        </div>
        <button class="submit-comment" on:click={submitComment} disabled={!newComment.trim() || !authorName.trim()}>
          Post Comment
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .pitch-detail {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .back-link {
    display: inline-block;
    color: #3498db;
    text-decoration: none;
    margin-bottom: 20px;
    font-weight: 500;
  }
  
  .back-link:hover {
    text-decoration: underline;
  }
  
  .loading, .error-message {
    text-align: center;
    padding: 40px;
    background: #f8f9fa;
    border-radius: 8px;
    margin: 20px 0;
  }
  
  .error-message {
    color: #e74c3c;
  }
  
  .pitch-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .pitch-header h1 {
    margin: 0;
    color: #2c3e50;
    font-size: 28px;
  }
  
  .pitch-score {
    color: #7f8c8d;
    font-size: 18px;
  }
  
  .pitch-score span {
    color: #3498db;
    font-weight: bold;
  }
  
  .pitch-meta {
    display: flex;
    justify-content: space-between;
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .pitch-content h2, .comments-section h2 {
    color: #2c3e50;
    margin: 25px 0 15px;
    font-size: 22px;
  }
  
  .analysis-section {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
  }
  
  .score-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .score-item {
    background: white;
    border-radius: 6px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  }
  
  .score-label {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 5px;
  }
  
  .score-value {
    color: #2c3e50;
    font-weight: bold;
    font-size: 18px;
  }
  
  .summary-box {
    background: white;
    border-radius: 6px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  }
  
  .comments-list {
    margin-bottom: 30px;
  }
  
  .no-comments {
    font-style: italic;
    color: #7f8c8d;
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 6px;
  }
  
  .comment {
    background: white;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  }
  
  .comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
  }
  
  .comment-author {
    font-weight: 600;
    color: #2c3e50;
  }
  
  .comment-time {
    color: #95a5a6;
    font-size: 14px;
  }
  
  .comment-content {
    color: #34495e;
    line-height: 1.5;
  }
  
  .comment-form {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
  }
  
  .comment-form h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #2c3e50;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    color: #2c3e50;
    font-weight: 500;
  }
  
  .form-group input, .form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
    font-size: 14px;
  }
  
  .form-group textarea {
    min-height: 120px;
    resize: vertical;
  }
  
  .submit-comment {
    background: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .submit-comment:hover {
    background: #2980b9;
  }
  
  .submit-comment:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }
  
  @media (max-width: 768px) {
    .pitch-header {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .pitch-score {
      margin-top: 10px;
    }
    
    .score-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
