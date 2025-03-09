<script>
  import { onMount } from 'svelte';
  import axios from 'axios';
  
  const API_URL = "https://rocket-pitch-backend.onrender.com"; // Your backend URL
  
  export let analysisResult;
  export let overallScore;
  
  let studentName = "";
  let pitchTitle = "";
  let pitchDescription = "";
  let isSubmitting = false;
  let errorMessage = "";
  let successMessage = "";
  
  async function submitToGallery() {
    if (!studentName.trim() || !pitchTitle.trim() || !pitchDescription.trim()) {
      errorMessage = "Please fill out all fields";
      return;
    }
    
    isSubmitting = true;
    errorMessage = "";
    successMessage = "";
    
    try {
      const analysisId = new Date().getTime().toString(); // Generate a simple ID
      
      const submission = {
        name: studentName,
        title: pitchTitle,
        description: pitchDescription,
        analysisId: analysisId,
        analysisResult: analysisResult,
        overallScore: overallScore
      };
      
      await axios.post(`${API_URL}/gallery/submit`, submission);
      
      successMessage = "Your pitch has been successfully submitted to the gallery!";
      // Reset form
      studentName = "";
      pitchTitle = "";
      pitchDescription = "";
      
    } catch (error) {
      console.error("Error submitting to gallery:", error);
      errorMessage = "Failed to submit your pitch. Please try again later.";
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="gallery-submission">
  <h2>Share Your Pitch in the Gallery</h2>
  <p class="form-description">
    Submit your pitch to the gallery to share with other students and receive feedback.
  </p>
  
  {#if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {/if}
  
  {#if successMessage}
    <div class="success-message">
      {successMessage}
      <a href="/gallery" class="view-gallery-link">View Gallery</a>
    </div>
  {/if}
  
  <div class="form-container">
    <div class="form-group">
      <label for="name">Your Name</label>
      <input type="text" id="name" bind:value={studentName} placeholder="Enter your name">
    </div>
    
    <div class="form-group">
      <label for="title">Pitch Title</label>
      <input type="text" id="title" bind:value={pitchTitle} placeholder="Enter a title for your pitch">
    </div>
    
    <div class="form-group">
      <label for="description">Description</label>
      <textarea 
        id="description" 
        bind:value={pitchDescription} 
        placeholder="Briefly describe your pitch (e.g., industry, problem you're solving, target audience)"
      ></textarea>
    </div>
    
    <div class="form-actions">
      <button 
        class="submit-button" 
        on:click={submitToGallery} 
        disabled={isSubmitting || !studentName.trim() || !pitchTitle.trim() || !pitchDescription.trim()}
      >
        {isSubmitting ? 'Submitting...' : 'Submit to Gallery'}
      </button>
    </div>
  </div>
</div>

<style>
  .gallery-submission {
    background: white;
    border-radius: 8px;
    padding: 25px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-top: 30px;
  }
  
  h2 {
    color: #2c3e50;
    margin-top: 0;
    margin-bottom: 15px;
  }
  
  .form-description {
    color: #7f8c8d;
    margin-bottom: 20px;
  }
  
  .error-message {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    color: #d32f2f;
    padding: 12px;
    margin-bottom: 20px;
    border-radius: 4px;
  }
  
  .success-message {
    background-color: #e8f5e9;
    border-left: 4px solid #4caf50;
    color: #2e7d32;
    padding: 12px;
    margin-bottom: 20px;
    border-radius: 4px;
  }
  
  .view-gallery-link {
    display: inline-block;
    margin-left: 10px;
    color: #3498db;
    text-decoration: none;
    font-weight: 500;
  }
  
  .view-gallery-link:hover {
    text-decoration: underline;
  }
  
  .form-container {
    display: grid;
    gap: 15px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
  }
  
  .form-group label {
    margin-bottom: 5px;
    color: #2c3e50;
    font-weight: 500;
  }
  
  .form-group input, .form-group textarea {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
    font-size: 14px;
  }
  
  .form-group textarea {
    min-height: 120px;
    resize: vertical;
  }
  
  .form-actions {
    margin-top: 10px;
  }
  
  .submit-button {
    background: #3498db;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .submit-button:hover:not(:disabled) {
    background: #2980b9;
  }
  
  .submit-button:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }
</style>
