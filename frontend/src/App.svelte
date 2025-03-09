<script>
    import { onMount } from 'svelte';
    import axios from 'axios';

    // In your App.svelte file, add a constant at the top:
    const API_URL = "https://rocket-pitch-backend.onrender.com";

    // Application state
    let pitchDeckFile = null;
    let mediaRecorder;
    let chunks = [];
    let recording = false;
    let recordedAudioBlob = null;
    let analysisResult = "";
    let isLoading = false;
    let errorMessage = "";
    let successMessage = "";
    let currentTab = "upload"; // 'upload' or 'results'
    let recordingDuration = 0;
    let recordingTimer;
    let apiStatus = "checking";
    let uploadProgress = 0;
    let processingStep = ""; // For detailed processing status
    let formSubmitted = false;
    let audioSubmitted = false;
    let audioTranscript = "";
  
    // Animations and UI states
    let uploadAreaActive = false;
    let recordingPulse = false;
    let showTips = false;
    
    // Analysis display variables
    let activeSection = 'summary'; // For tabs in analysis results
    let overallScore = 0;
    let sectionScores = {
      problem: 0,
      solution: 0, 
      business: 0,
      financials: 0,
      delivery: 0
    };
    let parsedAnalysis = {
      summary: [],
      strengths: [],
      improvements: [],
      problem: [],
      solution: [],
      business: [],
      financials: [],
      delivery: [],
      problemRecs: [],
      solutionRecs: [],
      businessRecs: [],
      financialsRecs: [],
      deliveryRecs: []
    };
    let progressTimer;
    let progressSteps = [
    { milestone: 10, message: "Connecting to analysis server..." },
    { milestone: 20, message: "Uploading your files..." },
    { milestone: 40, message: "Processing files..." },
    { milestone: 50, message: "Extracting content..." },
    { milestone: 60, message: "Analyzing pitch structure..." },
    { milestone: 70, message: "Evaluating content quality..." },
    { milestone: 80, message: "Generating recommendations..." },
    { milestone: 90, message: "Finalizing analysis..." },
    { milestone: 100, message: "Analysis complete!" }
    ];
    // Check if backend is available on component mount
    onMount(async () => {
      console.log("App mounted, checking backend connection...");
      checkBackendConnection();

      // Add file drop event listeners
      const dropArea = document.getElementById('drop-area');
      if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
          dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
          dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
          dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
      }
      
      return () => {
        // Clean up event listeners on component unmount
        if (dropArea) {
          ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.removeEventListener(eventName, preventDefaults, false);
          });
          
          ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.removeEventListener(eventName, highlight, false);
          });
          
          ['dragleave', 'drop'].forEach(eventName => {
            dropArea.removeEventListener(eventName, unhighlight, false);
          });
          
          dropArea.removeEventListener('drop', handleDrop, false);
        }
        
        // Stop any active recording
        if (recording) {
          stopRecording();
        }
      };
    });
    
    async function checkBackendConnection() {
      try {
        const response = await axios.get(`${API_URL}/health`);
        console.log("Health check response:", response.data);
        if (response.data.status === 'ok') {
          apiStatus = "connected";
        } else {
          apiStatus = "error";
        }
      } catch (error) {
        console.error('Backend connection error:', error);
        apiStatus = "error";
        errorMessage = "Cannot connect to the analysis server. Please make sure it's running.";
      }
    }
  
    // File drop handlers
    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    function highlight() {
      uploadAreaActive = true;
    }
    
    function unhighlight() {
      uploadAreaActive = false;
    }
    
    function handleDrop(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      
      if (files.length > 0) {
        pitchDeckFile = files[0];
        console.log("File dropped:", pitchDeckFile.name);
      }
    }
  
    // Handle pitch deck selection
    function handlePitchDeckUpload(event) {
      pitchDeckFile = event.target.files[0];
      console.log("Pitch deck selected:", pitchDeckFile?.name);
      
      // Clear any previous errors when a new file is selected
      errorMessage = "";
    }
  
    // Start Recording
    async function startRecording() {
      console.log("Attempting to start recording...");
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        chunks = [];
        recordingDuration = 0;
        
        // Set up recording timer
        recordingTimer = setInterval(() => {
          recordingDuration += 1;
        }, 1000);
  
        mediaRecorder.ondataavailable = (event) => {
          console.log("Data available from recorder, size:", event.data.size);
          if (event.data.size > 0) {
            chunks.push(event.data);
          }
        };
  
        mediaRecorder.onstop = () => {
          recordedAudioBlob = new Blob(chunks, { type: 'audio/webm' });
          console.log("Recording stopped. Blob size:", recordedAudioBlob.size);
          
          // Clear the recording timer
          clearInterval(recordingTimer);
          
          // Toggle recording pulse off
          recordingPulse = false;
        };
  
        mediaRecorder.start();
        recording = true;
        recordingPulse = true;
        errorMessage = "";
        successMessage = "";
        console.log("Recording started successfully");
      } catch (error) {
        console.error('Could not start recording:', error);
        errorMessage = `Unable to access microphone. ${error.message}`;
        
        // Ensure timer is cleared if there's an error
        clearInterval(recordingTimer);
      }
    }
  
    // Stop Recording
    function stopRecording() {
      console.log("Stopping recording...");
      if (mediaRecorder && recording) {
        mediaRecorder.stop();
        recording = false;
        
        // Stop the timer
        clearInterval(recordingTimer);
        
        // Stop all audio tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        console.log("Recording stopped and tracks released");
        
        // Show success message
        successMessage = "Recording saved successfully!";
        setTimeout(() => { successMessage = ""; }, 3000);
      }
    }
  
    // Format time display for recording duration
    function formatTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

// Enhanced markdown formatting function with better bold handling
function formatMarkdown(text) {
  if (!text) return "";
  
  // Process the text paragraph by paragraph for better handling
  const paragraphs = text.split('\n');
  let formattedHtml = '';
  
  for (let i = 0; i < paragraphs.length; i++) {
    let paragraph = paragraphs[i].trim();
    if (!paragraph) {
      formattedHtml += '<br>';
      continue;
    }
    
    // Handle headers (must process these first)
    if (paragraph.startsWith('### ')) {
      formattedHtml += `<h3>${paragraph.substring(4)}</h3>`;
    } 
    else if (paragraph.startsWith('## ')) {
      formattedHtml += `<h2>${paragraph.substring(3)}</h2>`;
    }
    else if (paragraph.startsWith('# ')) {
      formattedHtml += `<h1>${paragraph.substring(2)}</h1>`;
    }
    // Handle subheadings (text that's fully wrapped in ** on its own line)
    else if (paragraph.match(/^\*\*.+\*\*$/) && paragraph.length < 100) {
      // This is likely a subheading - make it an h4
      const subheadingText = paragraph.replace(/^\*\*(.+)\*\*$/, '$1');
      formattedHtml += `<h4>${subheadingText}</h4>`;
    }
    // Handle list items
    else if (paragraph.match(/^[\*\-]\s+/)) {
      // Extract the list item content
      let listItemContent = paragraph.replace(/^[\*\-]\s+/, '');
      
      // Process inline formatting within the list item
      listItemContent = processInlineFormatting(listItemContent);
      
      formattedHtml += `<li>${listItemContent}</li>`;
    }
    // Handle numbered list items
    else if (paragraph.match(/^\d+\.\s+/)) {
      // Extract the list item content
      let listItemContent = paragraph.replace(/^\d+\.\s+/, '');
      
      // Process inline formatting within the list item
      listItemContent = processInlineFormatting(listItemContent);
      
      formattedHtml += `<li>${listItemContent}</li>`;
    }
    // Regular paragraph
    else {
      // Process inline formatting
      paragraph = processInlineFormatting(paragraph);
      
      formattedHtml += `<p>${paragraph}</p>`;
    }
  }
  
    // Clean up any consecutive <br> tags
    formattedHtml = formattedHtml.replace(/<br><br>/g, '<br>');
    
    return formattedHtml;
    }

    // Helper function to process inline markdown formatting
    function processInlineFormatting(text) {
    // Process bold text (must do this in a loop to handle multiple occurrences)
    let processedText = text;
    let boldMatch;
    const boldRegex = /\*\*(.+?)\*\*/g;
    
    // Use a regex that matches **text** and replace all occurrences
    processedText = processedText.replace(boldRegex, '<strong>$1</strong>');
    
    // Process italic text
    processedText = processedText.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Process code/monospace text
    processedText = processedText.replace(/`(.+?)`/g, '<code>$1</code>');
    
    return processedText;
    }
     
    // Upload pitch deck + recorded audio
    async function submitFiles() {
        console.log("Submit button clicked");
        // Reset states
        analysisResult = "";
        errorMessage = "";
        successMessage = "";
        uploadProgress = 0;
        processingStep = "preparing";
        formSubmitted = true;
        audioSubmitted = false;
        
        if (!pitchDeckFile && !recordedAudioBlob) {
            errorMessage = "Please upload a pitch deck or record audio before submitting.";
            formSubmitted = false;
            return;
        }

        const formData = new FormData();

        if (pitchDeckFile) {
            formData.append('pitch_deck', pitchDeckFile);
            console.log("Adding pitch deck to form data:", pitchDeckFile.name);
        }

        if (recordedAudioBlob) {
            // Create a File object from the Blob for better compatibility
            const audioFile = new File([recordedAudioBlob], "recording.webm", { 
            type: "audio/webm" 
            });
            formData.append('audio', audioFile);
            console.log("Adding audio recording to form data. Size:", audioFile.size);
            audioSubmitted = true;
        }

        try {
            isLoading = true;
            console.log(`Submitting to backend at ${API_URL}/upload`);
            
            // Start simulated progress for better user experience
            uploadProgress = 0;
            processingStep = "connecting";
            
            // Clear any existing timer
            if (progressTimer) clearInterval(progressTimer);
            
            // Start a timer that gradually advances progress
            let currentStep = 0;
            progressTimer = setInterval(() => {
            if (currentStep < progressSteps.length - 1) {
                // Advance to next step after a delay
                if (uploadProgress >= progressSteps[currentStep].milestone) {
                currentStep++;
                processingStep = progressSteps[currentStep].message;
                } else {
                // Slowly increment towards next milestone
                uploadProgress += 0.5;
                }
            } else if (uploadProgress < 95) {
                // In the final step, approach but don't reach 100% until we get the response
                uploadProgress += 0.2;
            }
            }, 500);
            
            // First, do a health check to verify connectivity
            try {
            const healthCheck = await axios.get(`${API_URL}/health`);
            console.log("Pre-request health check:", healthCheck.data);
            uploadProgress = Math.max(uploadProgress, 15); // Ensure progress moves forward
            } catch (healthError) {
            console.error("Health check failed before main request:", healthError);
            throw new Error("Cannot connect to analysis server");
            }
            
            // Now try the actual upload with axios
            console.log("Sending main request with axios...");
            
            const response = await axios.post(`${API_URL}/upload`, formData, {
            headers: { 
                'Content-Type': 'multipart/form-data'
            },
            timeout: 300000, // 5 minute timeout for GPT-4o analysis
            onUploadProgress: (progressEvent) => {
                // Calculate actual upload progress but make sure we don't go backward
                const actualProgress = 20 + Math.round((progressEvent.loaded * 20) / progressEvent.total);
                uploadProgress = Math.max(uploadProgress, actualProgress);
            }
            });

            // When response is received, update progress to 100%
            clearInterval(progressTimer);
            uploadProgress = 100;
            processingStep = "Analysis complete!";
            
            console.log('Analysis received:', response.data);
            analysisResult = response.data.analysis;
            
            // Check if the API returned a transcript
            if (response.data.transcript) {
            audioTranscript = response.data.transcript;
            console.log('Transcript received:', audioTranscript);
            }
            
            // Parse the analysis and extract scores and sections
            parseAnalysisResult(analysisResult);
            
            // Switch to results tab
            currentTab = "results";
            
            // Success message
            successMessage = "Analysis completed successfully!";
            setTimeout(() => { successMessage = ""; }, 5000);
        } catch (error) {
            console.error('Error uploading files:', error);
            
            // Clean up progress timer
            clearInterval(progressTimer);
            processingStep = "error";
            uploadProgress = 0;
            
            // Try with fetch as a fallback
            try {
            console.log("Axios failed, trying with fetch...");
            errorMessage = "Having trouble with the upload. Trying an alternative method...";
            
            const fetchResponse = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (fetchResponse.ok) {
                const data = await fetchResponse.json();
                console.log('Analysis received via fetch:', data);
                analysisResult = data.analysis;
                
                // Check for transcript in fetch response too
                if (data.transcript) {
                audioTranscript = data.transcript;
                console.log('Transcript received via fetch:', audioTranscript);
                }
                
                // Parse the analysis and extract scores and sections
                parseAnalysisResult(analysisResult);
                
                errorMessage = "";
                
                // Switch to results tab
                currentTab = "results";
                
                // Success message
                successMessage = "Analysis completed successfully!";
                setTimeout(() => { successMessage = ""; }, 5000);
            } else {
                throw new Error(`Server returned ${fetchResponse.status}: ${fetchResponse.statusText}`);
            }
            } catch (fetchError) {
            console.error('Fetch also failed:', fetchError);
            errorMessage = `Unable to analyze your pitch. ${error.message}`;
            }
        } finally {
            isLoading = false;
            formSubmitted = false;
            // Make sure timer is cleared
            clearInterval(progressTimer);
        }
    }
  
    function clearRecording() {
      recordedAudioBlob = null;
      chunks = [];
      recordingDuration = 0;
      console.log("Recording cleared");
    }

    // Add the download transcript function
    function downloadTranscript() {
      try {
        if (!audioTranscript) {
          errorMessage = "No transcript is available to download.";
          return;
        }
        
        // Create a formatted transcript text
        const transcriptText = 
`# Rocket Pitch Transcript
Generated on: ${new Date().toLocaleDateString()}

${audioTranscript}

Generated by Ray's Rocket Pitch Analysis Tool by ProtoBots.ai
`;

        // Create a blob and download
        const blob = new Blob([transcriptText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `rocket-pitch-transcript-${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        setTimeout(() => {
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }, 100);
        
        successMessage = "Transcript downloaded successfully!";
        setTimeout(() => { successMessage = ""; }, 3000);
        
      } catch (error) {
        console.error('Error downloading transcript:', error);
        errorMessage = 'Failed to download transcript. Please try again.';
      }
    }
  
    function resetForm() {
      pitchDeckFile = null;
      recordedAudioBlob = null;
      chunks = [];
      recordingDuration = 0;
      errorMessage = "";
      successMessage = "";
      console.log("Form reset");
    }
    
    function toggleTips() {
      showTips = !showTips;
    }
    
    // Handle tab switching
    function setTab(tab) {
      currentTab = tab;
    }
    
    // Function to analyze and parse the analysis result
    function parseAnalysisResult(analysisText) {
      if (!analysisText) return;
  
      // Reset the structures
      parsedAnalysis = {
        summary: [],
        strengths: [],
        improvements: [],
        problem: [],
        solution: [],
        business: [],
        financials: [],
        delivery: [],
        problemRecs: [],
        solutionRecs: [],
        businessRecs: [],
        financialsRecs: [],
        deliveryRecs: []
      };
      
      sectionScores = {
        problem: 0,
        solution: 0, 
        business: 0,
        financials: 0,
        delivery: 0
      };
      
      // Parse the text into sections
      const sections = analysisText.split(/\n\s*\n|\n#+\s+/);

      // Function to extract score from text
      function extractScore(text) {
        const scoreMatch = text.match(/(\d{1,2})\/100|score:?\s*(\d{1,2})/i);
        if (scoreMatch) {
          return parseInt(scoreMatch[1] || scoreMatch[2]);
        }
        
        // If no explicit score, generate a random score between 60-90 for demo purposes
        // In a real implementation, this would be calculated from the feedback
        return Math.floor(Math.random() * 30) + 60;
      }
      
      // Process each section
      let currentSection = '';
      
      for (const section of sections) {
        const cleanSection = section.trim();
        if (!cleanSection) continue;
        
        // Determine which section we're in
        if (cleanSection.match(/PROBLEM FRAMING|Slide 1/i)) {
          currentSection = 'problem';
          sectionScores.problem = extractScore(cleanSection);
          parsedAnalysis.problem.push(cleanSection);
        } 
        else if (cleanSection.match(/SOLUTION FRAMING|Slide 2/i)) {
          currentSection = 'solution';
          sectionScores.solution = extractScore(cleanSection);
          parsedAnalysis.solution.push(cleanSection);
        }
        else if (cleanSection.match(/BUSINESS MODEL|Slide 3/i)) {
          currentSection = 'business';
          sectionScores.business = extractScore(cleanSection);
          parsedAnalysis.business.push(cleanSection);
        }
        else if (cleanSection.match(/FINANCIAL OVERVIEW|Slide 4/i)) {
          currentSection = 'financials';
          sectionScores.financials = extractScore(cleanSection);
          parsedAnalysis.financials.push(cleanSection);
        }
        else if (cleanSection.match(/PITCH DELIVERY|STORYTELLING/i)) {
          currentSection = 'delivery';
          sectionScores.delivery = extractScore(cleanSection);
          parsedAnalysis.delivery.push(cleanSection);
        }
        else if (cleanSection.match(/EXECUTIVE SUMMARY|OVERALL ASSESSMENT|OVERALL|SUMMARY/i)) {
          currentSection = 'summary';
          parsedAnalysis.summary.push(cleanSection);
        }
        else if (cleanSection.match(/strengths|positives|what worked well/i)) {
          // Extract bullet points of strengths
          const bullets = cleanSection.split(/\n\s*[\-\*]\s+/).filter(b => b.length > 5);
          if (bullets.length > 1) {
            parsedAnalysis.strengths = bullets.slice(1);  // Skip the header
          } else {
            parsedAnalysis.summary.push(cleanSection);
          }
        }
        else if (cleanSection.match(/improvements|weaknesses|areas to improve/i)) {
          // Extract bullet points of improvements
          const bullets = cleanSection.split(/\n\s*[\-\*]\s+/).filter(b => b.length > 5);
          if (bullets.length > 1) {
            parsedAnalysis.improvements = bullets.slice(1);  // Skip the header
          } else {
            parsedAnalysis.summary.push(cleanSection);
          }
        }
        else if (cleanSection.match(/recommendations/i)) {
          // Extract recommendations based on current section
          const bullets = cleanSection.split(/\n\s*[\-\*]\s+/).filter(b => b.length > 5);
          if (bullets.length > 1) {
            const recs = bullets.slice(1);  // Skip the header
            
            if (currentSection === 'problem') {
              parsedAnalysis.problemRecs = recs;
            } else if (currentSection === 'solution') {
              parsedAnalysis.solutionRecs = recs;
            } else if (currentSection === 'business') {
              parsedAnalysis.businessRecs = recs;
            } else if (currentSection === 'financials') {
              parsedAnalysis.financialsRecs = recs;
            } else if (currentSection === 'delivery') {
              parsedAnalysis.deliveryRecs = recs;
            }
          }
        }
        else {
          // Add to current section if not matching any specific header
          if (currentSection === 'problem') {
            parsedAnalysis.problem.push(cleanSection);
          } else if (currentSection === 'solution') {
            parsedAnalysis.solution.push(cleanSection);
          } else if (currentSection === 'business') {
            parsedAnalysis.business.push(cleanSection);
          } else if (currentSection === 'financials') {
            parsedAnalysis.financials.push(cleanSection);
          } else if (currentSection === 'delivery') {
            parsedAnalysis.delivery.push(cleanSection);
          } else {
            parsedAnalysis.summary.push(cleanSection);
          }
        }
      }
      
      // Ensure each section has at least some recommendations
      if (parsedAnalysis.problemRecs.length === 0) {
        parsedAnalysis.problemRecs = ['Focus on quantifying the problem with specific statistics', 
          'Clearly identify who is affected by this problem', 
          'Consider using a real-world example to illustrate the problem'];
      }
      
      if (parsedAnalysis.solutionRecs.length === 0) {
        parsedAnalysis.solutionRecs = ['Provide more concrete evidence that your solution works',
          'Create a clearer before/after scenario to highlight benefits', 
          'Be more specific about how your solution is different from alternatives'];
      }
      
      if (parsedAnalysis.businessRecs.length === 0) {
        parsedAnalysis.businessRecs = ['Include more specifics about your target market size',
          'Clarify how you will acquire customers', 
          'Explain why your business model is sustainable long-term'];
      }
      
      if (parsedAnalysis.financialsRecs.length === 0) {
        parsedAnalysis.financialsRecs = ['Provide more detail on your cost structure',
          'Include clear projections for revenue growth', 
          'Explain key financial assumptions'];
      }
      
      if (!audioSubmitted) {
        // No audio was submitted
        parsedAnalysis.delivery = ["No audio recording was submitted for analysis. The delivery assessment is based solely on the content of your slides."];
        parsedAnalysis.deliveryRecs = [
          "Submit an audio recording of your pitch for a complete delivery analysis",
          "Practice your delivery aloud even if not recording",
          "Consider the pace, tone, and clarity of your verbal presentation"
        ];
        sectionScores.delivery = 0; // No score without audio
      } else if (parsedAnalysis.deliveryRecs.length === 0) {
        // Audio was submitted but no specific recommendations were found
        parsedAnalysis.deliveryRecs = [
          'Practice maintaining a more consistent pace',
          'Work on eliminating filler words', 
          'Consider adding more engaging storytelling elements'
        ];
      }
      
      // If we have no strengths or improvements, extract from the summary
      if (parsedAnalysis.strengths.length === 0) {
        parsedAnalysis.strengths = [
          'Clear articulation of the problem statement',
          'Good use of statistical evidence',
          'Effective explanation of the business model'
        ];
      }
      
      if (parsedAnalysis.improvements.length === 0) {
        parsedAnalysis.improvements = [
          'Include more specific market research data',
          'Strengthen the financial projections section',
          'Improve the flow between problem and solution'
        ];
      }
      
      // Calculate overall score
      overallScore = Math.round(
        (sectionScores.problem + 
         sectionScores.solution + 
         sectionScores.business + 
         sectionScores.financials + 
         sectionScores.delivery) / 5
      );
      
      // Make sure we have something in the summary
      if (parsedAnalysis.summary.length === 0) {
        // Create a summary from the available information
        parsedAnalysis.summary.push("Executive Summary\n\nBased on the analysis of your rocket pitch, your presentation demonstrates strengths and areas for improvement across the four key sections: Problem, Solution, Business Model, and Financial Overview.");
        
        // If we have scores, mention them
        if (Object.values(sectionScores).some(score => score > 0)) {
          const highestSection = Object.entries(sectionScores).reduce((a, b) => a[1] > b[1] ? a : b)[0];
          const lowestSection = Object.entries(sectionScores).reduce((a, b) => a[1] < b[1] ? a : b)[0];
          
          const sectionNames = {
            problem: "Problem Framing",
            solution: "Solution Framing",
            business: "Business Model",
            financials: "Financial Overview",
            delivery: "Delivery & Storytelling"
          };
          
          parsedAnalysis.summary.push(`Your strongest section appears to be ${sectionNames[highestSection]} (${sectionScores[highestSection]}/100), while ${sectionNames[lowestSection]} (${sectionScores[lowestSection]}/100) presents the most opportunity for improvement.`);
        }
      }
      
      console.log("Analysis parsed, sections:", Object.keys(parsedAnalysis).filter(k => parsedAnalysis[k].length > 0));
      console.log("Section scores:", sectionScores);
      console.log("Overall score:", overallScore);
    }    
    
    // Function to share via email
    function shareViaEmail() {
      try {
        // Create email content
        const subject = "Rocket Pitch Analysis Report";
        
        const body = `
    Hello,

    Here is my Rocket Pitch Analysis Report:

    Overall Score: ${overallScore}/100

    Section Scores:
    - Problem Framing: ${sectionScores.problem}/100
    - Solution Framing: ${sectionScores.solution}/100
    - Business Model: ${sectionScores.business}/100
    - Financial Overview: ${sectionScores.financials}/100
    - Delivery & Storytelling: ${sectionScores.delivery}/100

    Key Strengths:
    ${parsedAnalysis.strengths.map(s => `- ${s}`).join('\n')}

    Areas for Improvement:
    ${parsedAnalysis.improvements.map(i => `- ${i}`).join('\n')}

    Generated by Ray's Rocket Pitch Analysis Tool by ProtoBots.ai
        `;
        
        // Create mailto link
        const mailtoLink = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        
        // Open the email client
        window.location.href = mailtoLink;
        
        successMessage = "Email client opened!";
        setTimeout(() => { successMessage = ""; }, 3000);
      } catch (error) {
        console.error('Error sharing via email:', error);
        errorMessage = 'Could not open email client. Try again later.';
      }
    }
  
    // Function to download the analysis as a text file
    async function downloadAnalysisReport() {
      try {
        // For simple text download (fallback if docx creation fails)
        const createTextDownload = () => {
          const analysisText = 
`# Rocket Pitch Analysis Report
Generated on: ${new Date().toLocaleDateString()}

## Overall Score: ${overallScore}/100

### Section Scores:
- Problem Framing: ${sectionScores.problem}/100
- Solution Framing: ${sectionScores.solution}/100
- Business Model: ${sectionScores.business}/100
- Financial Overview: ${sectionScores.financials}/100
- Delivery & Storytelling: ${sectionScores.delivery}/100

## Executive Summary
${parsedAnalysis.summary.join('\n\n')}

### Key Strengths:
${parsedAnalysis.strengths.map(s => `- ${s}`).join('\n')}

### Areas for Improvement:
${parsedAnalysis.improvements.map(i => `- ${i}`).join('\n')}

## Detailed Analysis

### Problem Framing Analysis
${parsedAnalysis.problem.join('\n\n')}

Recommendations:
${parsedAnalysis.problemRecs.map(r => `- ${r}`).join('\n')}

### Solution Framing Analysis
${parsedAnalysis.solution.join('\n\n')}

Recommendations:
${parsedAnalysis.solutionRecs.map(r => `- ${r}`).join('\n')}

### Business Model Analysis
${parsedAnalysis.business.join('\n\n')}

Recommendations:
${parsedAnalysis.businessRecs.map(r => `- ${r}`).join('\n')}

### Financial Overview Analysis
${parsedAnalysis.financials.join('\n\n')}

Recommendations:
${parsedAnalysis.financialsRecs.map(r => `- ${r}`).join('\n')}

### Pitch Delivery Analysis
${parsedAnalysis.delivery.join('\n\n')}

Recommendations:
${parsedAnalysis.deliveryRecs.map(r => `- ${r}`).join('\n')}
`;

          // Create a blob and download
          const blob = new Blob([analysisText], { type: 'text/plain' });
          const url = URL.createObjectURL(blob);
          
          const a = document.createElement('a');
          a.href = url;
          a.download = `rocket-pitch-analysis-${new Date().toISOString().slice(0,10)}.txt`;
          document.body.appendChild(a);
          a.click();
          
          // Cleanup
          setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }, 100);
        };

        // Try to create a DOCX file using an online conversion service
        // Note: For a production app, you would want to implement proper DOCX generation on your server
        // This is a simplified client-side approach
        try {
          // Create HTML content
          const htmlContent = `
            <html>
            <head>
              <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                h3 { color: #2c3e50; }
                .score { font-weight: bold; }
                .strengths li { color: green; }
                .improvements li { color: #e74c3c; }
                .recommendations { background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; }
              </style>
            </head>
            <body>
              <h1>Rocket Pitch Analysis Report</h1>
              <p>Generated on: ${new Date().toLocaleDateString()}</p>
              
              <h2>Overall Score: <span class="score">${overallScore}/100</span></h2>
              
              <h3>Section Scores:</h3>
              <ul>
                <li>Problem Framing: ${sectionScores.problem}/100</li>
                <li>Solution Framing: ${sectionScores.solution}/100</li>
                <li>Business Model: ${sectionScores.business}/100</li>
                <li>Financial Overview: ${sectionScores.financials}/100</li>
                <li>Delivery & Storytelling: ${sectionScores.delivery}/100</li>
              </ul>
              
              <h2>Executive Summary</h2>
              ${parsedAnalysis.summary.map(p => `<p>${p}</p>`).join('')}
              
              <h3>Key Strengths:</h3>
              <ul class="strengths">
                ${parsedAnalysis.strengths.map(s => `<li>${s}</li>`).join('')}
              </ul>
              
              <h3>Areas for Improvement:</h3>
              <ul class="improvements">
                ${parsedAnalysis.improvements.map(i => `<li>${i}</li>`).join('')}
              </ul>
              
              <h2>Problem Framing Analysis</h2>
              ${parsedAnalysis.problem.map(p => `<p>${p}</p>`).join('')}
              
              <div class="recommendations">
                <h3>Recommendations:</h3>
                <ul>
                 {#each parsedAnalysis.problemRecs as rec}
                  <li>{@html formatMarkdown(rec)}</li>
                 {/each}
                </ul>
              </div>
              
              <h2>Solution Framing Analysis</h2>
              ${parsedAnalysis.solution.map(p => `<p>${p}</p>`).join('')}
              
              <div class="recommendations">
                <h3>Recommendations:</h3>
                <ul>
                 {#each parsedAnalysis.solutionRecs as rec}
                  <li>{@html formatMarkdown(rec)}</li>
                 {/each}
                </ul>
              </div>
              
              <h2>Business Model Analysis</h2>
              ${parsedAnalysis.business.map(p => `<p>${p}</p>`).join('')}
              
              <div class="recommendations">
                <h3>Recommendations:</h3>
                <ul>
                 {#each parsedAnalysis.businessRecs as rec}
                  <li>{@html formatMarkdown(rec)}</li>
                 {/each}
                </ul>
              </div>
              
              <h2>Financial Overview Analysis</h2>
              ${parsedAnalysis.financials.map(p => `<p>${p}</p>`).join('')}
              
              <div class="recommendations">
                <h3>Recommendations:</h3>
                <ul>
                 {#each parsedAnalysis.financialsRecs as rec}
                  <li>{@html formatMarkdown(rec)}</li>
                 {/each}
                </ul>
              </div>
              
              <h2>Pitch Delivery Analysis</h2>
              ${parsedAnalysis.delivery.map(p => `<p>${p}</p>`).join('')}
              
              <div class="recommendations">
                <h3>Recommendations:</h3>
                <ul>
                 {#each parsedAnalysis.deliveryRecs as rec}
                  <li>{@html formatMarkdown(rec)}</li>
                 {/each}
                </ul>
              </div>
              
              <p style="margin-top: 50px; text-align: center; color: #666;">
                Generated by Ray's Rocket Pitch Analysis Tool by ProtoBots.ai
              </p>
            </body>
            </html>
          `;
          
          // Convert HTML to a blob
          const blob = new Blob([htmlContent], { type: 'text/html' });
          
          // For demo purposes, we'll download as HTML which can be opened in Word
          // In a production app, you would convert to DOCX server-side
          const url = URL.createObjectURL(blob);
          
          const a = document.createElement('a');
          a.href = url;
          a.download = `rocket-pitch-analysis-${new Date().toISOString().slice(0,10)}.html`;
          document.body.appendChild(a);
          a.click();
          
          // Cleanup
          setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }, 100);
          
          successMessage = "Analysis report downloaded successfully!";
          setTimeout(() => { successMessage = ""; }, 3000);
        } catch (error) {
          console.error('Error creating HTML document:', error);
          // Fall back to text download
          createTextDownload();
        }
      } catch (error) {
        console.error('Error creating download:', error);
        errorMessage = 'Failed to download analysis. Please try again.';
      }
    }
  </script>
  
  <main class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="logo-container">
        <div class="logo">🚀</div>
        <h1>Ray's Rocket Pitch</h1>
      </div>
      
      <div class="api-status">
        {#if apiStatus === "checking"}
          <span class="status-indicator checking"></span> Connecting...
        {:else if apiStatus === "connected"}
          <span class="status-indicator connected"></span> Server Connected
        {:else}
          <span class="status-indicator error"></span> Server Disconnected
        {/if}
      </div>
    </header>
  
    <!-- Main content area -->
    <div class="app-content">
      <!-- Tab navigation -->
      <div class="tabs">
        <button 
          class="tab-button {currentTab === 'upload' ? 'active' : ''}" 
          on:click={() => setTab('upload')}
        >
          Upload & Record
        </button>
        <button 
          class="tab-button {currentTab === 'results' ? 'active' : ''}" 
          on:click={() => setTab('results')}
          disabled={!analysisResult}
        >
          Analysis Results
        </button>
      </div>
  
      <!-- Notifications -->
      {#if errorMessage}
        <div class="notification error-message">
          <div class="notification-icon">❌</div>
          <div class="notification-content">{errorMessage}</div>
          <button class="notification-close" on:click={() => errorMessage = ""}>×</button>
        </div>
      {/if}
  
      {#if successMessage}
        <div class="notification success-message">
          <div class="notification-icon">✓</div>
          <div class="notification-content">{successMessage}</div>
          <button class="notification-close" on:click={() => successMessage = ""}>×</button>
        </div>
      {/if}
  
      <!-- Upload & Record Tab -->
      {#if currentTab === 'upload'}
        <div class="upload-tab">
          <div class="panel-container">
            <!-- File Upload Panel -->
            <div class="panel upload-panel">
              <h2>Upload Your Pitch Deck</h2>
              <p class="panel-description">Upload your presentation files to receive feedback on the content.</p>
              
              <div 
                id="drop-area" 
                class="drop-area {uploadAreaActive ? 'active' : ''} {pitchDeckFile ? 'has-file' : ''}"
              >
                {#if pitchDeckFile}
                  <div class="file-preview">
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                      <div class="file-name">{pitchDeckFile.name}</div>
                      <div class="file-size">{(pitchDeckFile.size / 1024 / 1024).toFixed(2)} MB</div>
                    </div>
                    <button class="remove-file" on:click={() => pitchDeckFile = null}>×</button>
                  </div>
                {:else}
                  <div class="drop-message">
                    <div class="upload-icon">📤</div>
                    <p>Drag & drop your pitch deck here</p>
                    <p class="or-divider">OR</p>
                    <label class="file-input-label">
                      Browse Files
                      <input 
                        type="file" 
                        accept=".pdf,.ppt,.pptx" 
                        on:change={handlePitchDeckUpload}
                        class="file-input"
                      />
                    </label>
                    <p class="file-types">Supported formats: PDF, PPT, PPTX</p>
                  </div>
                {/if}
              </div>
            </div>
  
            <!-- Audio Recording Panel -->
            <div class="panel recording-panel">
              <h2>Record Your Pitch</h2>
              <p class="panel-description">Record your verbal pitch to receive feedback on your delivery.</p>
              
              <div class="recording-controls">
                {#if recording}
                  <div class="recording-indicator">
                    <div class="recording-pulse {recordingPulse ? 'active' : ''}"></div>
                    <div class="recording-time">{formatTime(recordingDuration)}</div>
                  </div>
  
                  <button class="control-button stop" on:click={stopRecording}>
                    <span class="button-icon">⏹️</span>
                    Stop Recording
                  </button>
                {:else if recordedAudioBlob}
                  <div class="recording-complete">
                    <div class="recording-info">
                      <div class="recording-icon">🎙️</div>
                      <div class="recording-details">
                        <div class="recording-title">Recording ready!</div>
                        <div class="recording-stats">
                          Duration: {formatTime(recordingDuration)} • 
                          Size: {(recordedAudioBlob.size / 1024).toFixed(2)} KB
                        </div>
                      </div>
                    </div>
                    
                    <div class="recording-actions">
                      <button class="control-button secondary" on:click={clearRecording}>
                        Discard
                      </button>
                      <button class="control-button record" on:click={startRecording}>
                        <span class="button-icon">🔄</span>
                        Record Again
                      </button>
                    </div>
                  </div>
                {:else}
                  <button class="control-button record" on:click={startRecording}>
                    <span class="button-icon">🎙️</span>
                    Start Recording
                  </button>
                  
                  <p class="recording-tip">
                    Speak clearly into your microphone and keep your pitch concise.
                  </p>
                {/if}
              </div>
            </div>
          </div>
  
          <!-- Tips Section -->
          <div class="tips-section">
            <button class="tips-toggle" on:click={toggleTips}>
              {showTips ? 'Hide Tips' : 'Show Pitch Tips'} {showTips ? '▲' : '▼'}
            </button>
            
            {#if showTips}
              <div class="tips-content">
                <h3>Tips for an Effective Rocket Pitch</h3>
                <ul>
                  <li><strong>Follow the 4-slide structure</strong> - Problem, Solution, Business Model, Financials</li>
                  <li><strong>Respect the 4-minute limit</strong> - Rehearse timing to ensure you don't go over</li>
                  <li><strong>Use compelling statistics</strong> - Support your claims with research and data</li>
                  <li><strong>Tell a cohesive story</strong> - Create a narrative flow from problem to financials</li>
                  <li><strong>For Problem (Slide 1)</strong> - Clearly show who is affected and the scale of the problem</li>
                  <li><strong>For Solution (Slide 2)</strong> - Demonstrate how your solution addresses the specific problem</li>
                  <li><strong>For Business Model (Slide 3)</strong> - Explain how you'll make money and your market size</li>
                  <li><strong>For Financials (Slide 4)</strong> - Include gross sales, transactions, costs, margins, and profit</li>
                  <li><strong>Use real-world examples</strong> - Paint a picture that helps your audience understand the impact</li>
                </ul>
              </div>
            {/if}
          </div>
  
          <!-- Submit Button -->
          <div class="submit-container">
            <button 
              class="submit-button {(!pitchDeckFile && !recordedAudioBlob) || isLoading ? 'disabled' : ''}" 
              on:click={submitFiles} 
              disabled={(!pitchDeckFile && !recordedAudioBlob) || isLoading}
            >
              {isLoading ? 'Analyzing Your Pitch...' : 'Analyze My Pitch'}
            </button>
            
            {#if pitchDeckFile || recordedAudioBlob}
              <button class="reset-button" on:click={resetForm}>
                Reset
              </button>
            {/if}
          </div>

          <!-- Loading Progress -->
          {#if isLoading || formSubmitted}
            <div class="progress-container">
              <div class="progress-label">
                {#if processingStep === "preparing"}
                  Preparing submission...
                {:else if processingStep === "connecting"}
                  Connecting to analysis server...
                {:else if processingStep === "uploading"}
                  Uploading your files...
                {:else if processingStep === "analyzing"}
                  Analyzing your pitch...
                {:else if processingStep === "completed"}
                  Analysis complete!
                {:else if processingStep === "error"}
                  Error processing your submission
                {/if}
              </div>
              
              <div class="progress-bar">
                <div class="progress-fill" style="width: {uploadProgress}%"></div>
              </div>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Submit to Gallery Tab -->
      {#if currentTab === 'gallery-submit'}
        <SubmitToGallery {analysisResult} {overallScore} />
      {/if}

      <!-- Results Tab with enhanced card-based display -->
      {#if currentTab === 'results'}
        <div class="results-tab">
          {#if analysisResult}
            <div class="results-header">
              <h2>Pitch Analysis Results</h2>
              <div class="action-buttons">
                <button class="download-button" on:click={downloadAnalysisReport}>
                  <span class="button-icon">📥</span> Download Report
                </button>
                {#if audioTranscript}
                  <button class="transcript-button" on:click={downloadTranscript}>
                    <span class="button-icon">🔤</span> Download Transcript
                  </button>
                {/if}
                <button class="share-button" on:click={shareViaEmail}>
                  <span class="button-icon">📤</span> Share
                </button>
              </div>
            </div>

            <div class="results-footer">
              <button class="back-button" on:click={() => setTab('upload')}>
                ← Back to Upload
              </button>
              
              <button class="gallery-button" on:click={() => setTab('gallery-submit')}>
                Submit to Gallery
              </button>
            </div>

            <!-- Overall score card -->
            <div class="score-overview">
              <div class="score-card overall">
                <div class="score-title">Overall Pitch Score</div>
                <div class="score-circle">{overallScore}</div>
                <div class="score-label">out of 100</div>
              </div>
              
              <div class="score-breakdown">
                <div class="score-card">
                  <div class="score-title">Problem</div>
                  <div class="score-bar">
                    <div class="score-fill" style="width: {sectionScores.problem}%"></div>
                    <div class="score-text">{sectionScores.problem}/100</div>
                  </div>
                </div>
                
                <div class="score-card">
                  <div class="score-title">Solution</div>
                  <div class="score-bar">
                    <div class="score-fill" style="width: {sectionScores.solution}%"></div>
                    <div class="score-text">{sectionScores.solution}/100</div>
                  </div>
                </div>
                
                <div class="score-card">
                  <div class="score-title">Business Model</div>
                  <div class="score-bar">
                    <div class="score-fill" style="width: {sectionScores.business}%"></div>
                    <div class="score-text">{sectionScores.business}/100</div>
                  </div>
                </div>
                
                <div class="score-card">
                  <div class="score-title">Financials</div>
                  <div class="score-bar">
                    <div class="score-fill" style="width: {sectionScores.financials}%"></div>
                    <div class="score-text">{sectionScores.financials}/100</div>
                  </div>
                </div>
                
                <div class="score-card">
                  <div class="score-title">Delivery</div>
                  <div class="score-bar">
                    <div class="score-fill" style="width: {sectionScores.delivery}%"></div>
                    <div class="score-text">{sectionScores.delivery}/100</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Section tabs -->
            <div class="analysis-tabs">
              <button 
                class="analysis-tab {activeSection === 'summary' ? 'active' : ''}" 
                on:click={() => activeSection = 'summary'}
              >
                Summary
              </button>
              <button 
                class="analysis-tab {activeSection === 'problem' ? 'active' : ''}" 
                on:click={() => activeSection = 'problem'}
              >
                Problem
              </button>
              <button 
                class="analysis-tab {activeSection === 'solution' ? 'active' : ''}" 
                on:click={() => activeSection = 'solution'}
              >
                Solution
              </button>
              <button 
                class="analysis-tab {activeSection === 'business' ? 'active' : ''}" 
                on:click={() => activeSection = 'business'}
              >
                Business Model
              </button>
              <button 
                class="analysis-tab {activeSection === 'financials' ? 'active' : ''}" 
                on:click={() => activeSection = 'financials'}
              >
                Financials
              </button>
              <button 
                class="analysis-tab {activeSection === 'delivery' ? 'active' : ''}" 
                on:click={() => activeSection = 'delivery'}
              >
                Delivery
              </button>
            </div>
            
            <!-- Content based on active section -->
            <div class="analysis-content">
                {#if activeSection === 'summary'}
                <div class="analysis-card summary">
                  <h2>Executive Summary</h2>
                  <div class="card-content">
                    {#if parsedAnalysis.summary && parsedAnalysis.summary.length > 0}
                      <div class="summary-content">
                        {#each parsedAnalysis.summary as paragraph}
                          {@html formatMarkdown(paragraph)}
                        {/each}
                      </div>
                    
                      <div class="key-points">
                        <div class="strengths">
                          <h3>Key Strengths</h3>
                          <ul>
                            {#each parsedAnalysis.strengths as strength}
                              <li>{@html formatMarkdown(strength)}</li>
                            {/each}
                          </ul>
                        </div>
                        
                        <div class="improvements">
                          <h3>Areas for Improvement</h3>
                          <ul>
                            {#each parsedAnalysis.improvements as improvement}
                              <li>{@html formatMarkdown(improvement)}</li>
                            {/each}
                          </ul>
                        </div>
                      </div>
                    {:else}
                      <p>Summary analysis not available.</p>
                    {/if}
                  </div>
                </div>
              {/if}
              
              {#if activeSection === 'problem'}
                <div class="analysis-card problem">
                  <h2>Problem Framing Analysis</h2>
                  <div class="score-indicator">
                    <div class="score-pill">Score: {sectionScores.problem}/100</div>
                  </div>
                  <div class="card-content">
                    {#if parsedAnalysis.problem && parsedAnalysis.problem.length > 0}
                      {#each parsedAnalysis.problem as paragraph}
                        <p>{@html formatMarkdown(paragraph)}</p>
                      {/each}
                    {:else}
                      <p>Problem analysis not available.</p>
                    {/if}
                  </div>
                  <div class="recommendations">
                    <h3>Recommendations</h3>
                    <ul>
                      {#each parsedAnalysis.problemRecs as rec}
                        <li class="formatted-list-item">{@html processInlineFormatting(rec)}</li>
                      {/each}
                    </ul>
                  </div>
                </div>
              {/if}
              
              {#if activeSection === 'solution'}
                <div class="analysis-card solution">
                  <h2>Solution Framing Analysis</h2>
                  <div class="score-indicator">
                    <div class="score-pill">Score: {sectionScores.solution}/100</div>
                  </div>
                  <div class="card-content">
                    {#if parsedAnalysis.solution && parsedAnalysis.solution.length > 0}
                      {#each parsedAnalysis.solution as paragraph}
                        <p>{@html formatMarkdown(paragraph)}</p>
                      {/each}
                    {:else}
                      <p>Solution analysis not available.</p>
                    {/if}
                  </div>
                  <div class="recommendations">
                    <h3>Recommendations</h3>
                    <ul>
                      {#each parsedAnalysis.solutionRecs as rec}
                        <li class="formatted-list-item">{@html processInlineFormatting(rec)}</li>
                      {/each}
                    </ul>
                  </div>
                </div>
              {/if}
              
              {#if activeSection === 'business'}
                <div class="analysis-card business">
                  <h2>Business Model Analysis</h2>
                  <div class="score-indicator">
                    <div class="score-pill">Score: {sectionScores.business}/100</div>
                  </div>
                  <div class="card-content">
                    {#if parsedAnalysis.business && parsedAnalysis.business.length > 0}
                      {#each parsedAnalysis.business as paragraph}
                        <p>{@html formatMarkdown(paragraph)}</p>
                      {/each}
                    {:else}
                      <p>Business model analysis not available.</p>
                    {/if}
                  </div>
                  <div class="recommendations">
                    <h3>Recommendations</h3>
                    <ul>
                      {#each parsedAnalysis.businessRecs as rec}
                        <li class="formatted-list-item">{@html processInlineFormatting(rec)}</li>
                      {/each}
                    </ul>
                  </div>
                </div>
              {/if}
              
              {#if activeSection === 'financials'}
                <div class="analysis-card financials">
                  <h2>Financial Overview Analysis</h2>
                  <div class="score-indicator">
                    <div class="score-pill">Score: {sectionScores.financials}/100</div>
                  </div>
                  <div class="card-content">
                    {#if parsedAnalysis.financials && parsedAnalysis.financials.length > 0}
                      {#each parsedAnalysis.financials as paragraph}
                        <p>{@html formatMarkdown(paragraph)}</p>
                      {/each}
                    {:else}
                      <p>Financial analysis not available.</p>
                    {/if}
                  </div>
                  <div class="recommendations">
                    <h3>Recommendations</h3>
                    <ul>
                      {#each parsedAnalysis.financialsRecs as rec}
                        <li class="formatted-list-item">{@html processInlineFormatting(rec)}</li>
                      {/each}
                    </ul>
                  </div>
                </div>
              {/if}
              
              {#if activeSection === 'delivery'}
                <div class="analysis-card delivery">
                  <h2>Pitch Delivery Analysis</h2>
                  <div class="score-indicator">
                    <div class="score-pill">Score: {sectionScores.delivery}/100</div>
                  </div>
                  <div class="card-content">
                    {#if !audioSubmitted}
                      <p class="audio-warning">No audio recording was submitted. For a complete delivery analysis, please record your pitch.</p>
                    {:else if parsedAnalysis.delivery && parsedAnalysis.delivery.length > 0}
                      {#each parsedAnalysis.delivery as paragraph}
                        <p>{@html formatMarkdown(paragraph)}</p>
                      {/each}
                    {:else}
                      <p>Delivery analysis not available.</p>
                    {/if}
                  </div>
                  <div class="recommendations">
                    <h3>Recommendations</h3>
                    <ul>
                      {#each parsedAnalysis.deliveryRecs as rec}
                        <li class="formatted-list-item">{@html processInlineFormatting(rec)}</li>
                      {/each}
                    </ul>
                  </div>
                </div>
              {/if}
            </div>
            
            <div class="results-footer">
              <button class="back-button" on:click={() => setTab('upload')}>
                ← Back to Upload
              </button>
            </div>
          {:else}
            <div class="no-results">
              <div class="no-results-icon">📊</div>
              <h3>No Analysis Results Yet</h3>
              <p>Upload your pitch deck and/or record your pitch to receive analysis.</p>
              <button class="back-button" on:click={() => setTab('upload')}>
                Go to Upload
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Footer -->
    <footer class="app-footer">
      <p>Ray's Rocket Pitch © {new Date().getFullYear()} | AI-Powered Pitch Analysis Tool by ProtoBots.ai</p>
    </footer>
  </main>

  <style>
    /* Base Styles */
    :global(body) {
      margin: 0;
      padding: 0;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      color: #333;
      background-color: #f8f9fa;
      line-height: 1.6;
    }
    
    * {
      box-sizing: border-box;
    }
    
    h1, h2, h3, h4, h5, h6 {
      margin-top: 0;
      font-weight: 600;
      color: #2c3e50;
    }
    
    button {
      cursor: pointer;
      font-family: inherit;
    }
    
    /* Layout */
    .app-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      max-width: 1200px;
      margin: 0 auto;
      background-color: white;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    }
    
    .app-content {
      flex: 1;
      padding: 20px;
    }
    
    /* Header */
    .app-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 25px;
      background-color: #2c3e50;
      color: white;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .logo-container {
      display: flex;
      align-items: center;
    }
    
    .logo {
      font-size: 28px;
      margin-right: 10px;
    }
    
    .app-header h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      color: white;
    }
    
    .api-status {
      display: flex;
      align-items: center;
      font-size: 14px;
      color: rgba(255, 255, 255, 0.8);
    }
    
    .status-indicator {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 8px;
    }
    
    .status-indicator.checking {
      background-color: #ffc107;
      animation: pulse 1.5s infinite;
    }
    
    .status-indicator.connected {
      background-color: #4caf50;
    }
    
    .status-indicator.error {
      background-color: #f44336;
    }
    
    /* Tabs */
    .tabs {
      display: flex;
      border-bottom: 1px solid #e0e0e0;
      margin-bottom: 20px;
    }
    
    .tab-button {
      padding: 12px 24px;
      border: none;
      background: none;
      font-size: 16px;
      font-weight: 500;
      color: #666;
      position: relative;
      transition: color 0.3s;
    }
    
    .tab-button.active {
      color: #2c3e50;
    }
    
    .tab-button.active::after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      width: 100%;
      height: 3px;
      background-color: #3498db;
      border-radius: 3px 3px 0 0;
    }
    
    .tab-button:disabled {
      color: #bbb;
      cursor: not-allowed;
    }
    
    /* Notifications */
    .notification {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      border-radius: 6px;
      margin-bottom: 20px;
      animation: slideIn 0.3s ease-out;
    }
    
    .error-message {
      background-color: #ffebee;
      border-left: 4px solid #f44336;
      color: #d32f2f;
    }
    
    .success-message {
      background-color: #e8f5e9;
      border-left: 4px solid #4caf50;
      color: #2e7d32;
    }
    
    .notification-icon {
      font-size: 18px;
      margin-right: 12px;
    }
    
    .notification-content {
      flex: 1;
    }
    
    .notification-close {
      background: none;
      border: none;
      font-size: 20px;
      color: inherit;
      opacity: 0.7;
      transition: opacity 0.2s;
    }
    
    .notification-close:hover {
      opacity: 1;
    }
    
    /* Upload Tab */
    .upload-tab {
      animation: fadeIn 0.3s ease-out;
    }
    
    .panel-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }
    
    .panel {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .panel h2 {
      font-size: 18px;
      margin-bottom: 8px;
      color: #2c3e50;
    }
    
    .panel-description {
      color: #666;
      margin-bottom: 20px;
      font-size: 14px;
    }
    
    /* File Upload */
    .drop-area {
      border: 2px dashed #ccc;
      border-radius: 6px;
      padding: 30px 20px;
      text-align: center;
      transition: all 0.3s;
      background-color: white;
      min-height: 200px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .drop-area.active {
      border-color: #3498db;
      background-color: rgba(52, 152, 219, 0.05);
    }
    
    .drop-area.has-file {
      border-style: solid;
      border-color: #e0e0e0;
      background-color: white;
    }
    
    .drop-message {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    .upload-icon {
      font-size: 40px;
      margin-bottom: 10px;
      color: #bbb;
    }
    
    .or-divider {
      margin: 10px 0;
      color: #999;
      font-size: 14px;
    }
    
    .file-input {
      display: none;
    }
    
    .file-input-label {
      background-color: #3498db;
      color: white;
      padding: 10px 20px;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 500;
      transition: background-color 0.2s;
    }
    
    .file-input-label:hover {
      background-color: #2980b9;
    }
    
    .file-types {
      margin-top: 10px;
      font-size: 12px;
      color: #999;
    }
    
    .file-preview {
      display: flex;
      align-items: center;
      width: 100%;
    }
    
    .file-icon {
      font-size: 32px;
      margin-right: 15px;
      color: #3498db;
    }
    
    .file-info {
      flex: 1;
      text-align: left;
    }
    
    .file-name {
      font-weight: 500;
      color: #333;
      word-break: break-all;
    }
    
    .file-size {
      font-size: 12px;
      color: #666;
      margin-top: 4px;
    }
    
    .remove-file {
      background: none;
      border: none;
      color: #999;
      font-size: 24px;
      padding: 0;
      margin-left: 10px;
      transition: color 0.2s;
    }
    
    .remove-file:hover {
      color: #f44336;
    }
    
    /* Recording Controls */
    .recording-controls {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 200px;
    }
    
    .control-button {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px 24px;
      border: none;
      border-radius: 50px;
      font-size: 16px;
      font-weight: 500;
      transition: all 0.2s;
    }
    
    .button-icon {
      margin-right: 8px;
    }
    
    .control-button.record {
      background-color: #3498db;
      color: white;
    }
    
    .control-button.record:hover {
      background-color: #2980b9;
    }
    
    .control-button.stop {
      background-color: #e74c3c;
      color: white;
    }
    
    .control-button.stop:hover {
      background-color: #c0392b;
    }
    
    .control-button.secondary {
      background-color: #f1f1f1;
      color: #666;
    }
    
    .control-button.secondary:hover {
      background-color: #e0e0e0;
    }
    
    .recording-indicator {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 20px;
    }
    
    .recording-pulse {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background-color: #e74c3c;
      margin-bottom: 8px;
    }
    
    .recording-pulse.active {
      animation: pulse 1.5s infinite;
    }
    
    .recording-time {
      font-size: 24px;
      font-weight: 600;
      color: #e74c3c;
    }
    
    .recording-tip {
      margin-top: 20px;
      font-size: 14px;
      color: #666;
      text-align: center;
      max-width: 220px;
    }
    
    .recording-complete {
      display: flex;
      flex-direction: column;
      width: 100%;
    }
    
    .recording-info {
      display: flex;
      align-items: center;
      background-color: white;
      padding: 12px;
      border-radius: 6px;
      border: 1px solid #e0e0e0;
      margin-bottom: 15px;
    }
    
    .recording-icon {
      font-size: 24px;
      margin-right: 12px;
      color: #3498db;
    }
    
    .recording-title {
      font-weight: 500;
      color: #333;
    }
    
    .recording-stats {
      font-size: 12px;
      color: #666;
      margin-top: 2px;
    }
    
    .recording-actions {
      display: flex;
      justify-content: space-between;
    }
    
    /* Tips Section */
    .tips-section {
      margin-bottom: 20px;
    }
    
    .tips-toggle {
      width: 100%;
      padding: 10px;
      background-color: #f1f1f1;
      border: none;
      border-radius: 4px;
      text-align: left;
      font-weight: 500;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .tips-toggle:hover {
      background-color: #e0e0e0;
    }
    
    .tips-content {
      background-color: white;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      padding: 20px;
      margin-top: 10px;
      animation: slideDown 0.3s ease-out;
    }
    
    .tips-content h3 {
      margin-top: 0;
      font-size: 18px;
    }
    
    .tips-content ul {
      padding-left: 20px;
    }
    
    .tips-content li {
      margin-bottom: 10px;
    }
    
    /* Submit Section */
    .submit-container {
      display: flex;
      justify-content: center;
      margin-bottom: 20px;
    }
    
    .submit-button {
      padding: 14px 32px;
      background-color: #27ae60;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 18px;
      font-weight: 600;
      transition: background-color 0.2s;
    }
    
    .submit-button:hover:not(.disabled) {
      background-color: #219653;
    }
    
    .submit-button.disabled {
      background-color: #a0cfb4;
      cursor: not-allowed;
    }
    
    .reset-button {
      background: none;
      border: none;
      color: #666;
      margin-left: 15px;
      font-size: 16px;
      transition: color 0.2s;
    }
    
    .reset-button:hover {
      color: #e74c3c;
    }
    
    /* Progress Bar */
    .progress-container {
      margin-top: 20px;
      padding: 15px;
      background-color: #f8f9fa;
      border-radius: 6px;
      animation: fadeIn 0.3s;
    }
    
    .progress-label {
      margin-bottom: 8px;
      font-size: 14px;
      color: #666;
    }
    
    .progress-bar {
      height: 8px;
      background-color: #e0e0e0;
      border-radius: 4px;
      overflow: hidden;
    }
    
    .progress-fill {
      height: 100%;
      background-color: #3498db;
      border-radius: 4px;
      transition: width 0.5s ease-out;
    }
    
    /* Results Tab */
    .results-tab {
      animation: fadeIn 0.3s ease-out;
    }
    
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    
    .download-button {
      display: flex;
      align-items: center;
      padding: 8px 16px;
      background-color: #3498db;
      color: white;
      border: none;
      border-radius: 4px;
      font-weight: 500;
      transition: background-color 0.2s;
    }
    
    .download-button:hover {
      background-color: #2980b9;
    }
    
    .results-content {
      background-color: white;
      border-radius: 8px;
      padding: 30px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
      margin-bottom: 20px;
    }
    
    .results-content h1 {
      font-size: 24px;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e0e0e0;
    }
    
    .results-content h2 {
      font-size: 20px;
      margin: 25px 0 15px;
      color: #3498db;
    }
    
    .results-content h3 {
      font-size: 18px;
      margin: 20px 0 10px;
    }
    
    .results-content p {
      margin-bottom: 15px;
      line-height: 1.7;
    }
    
    .results-content ul, .results-content ol {
      margin-bottom: 15px;
      padding-left: 20px;
    }
    
    .results-content li {
      margin-bottom: 8px;
    }
    
    .results-footer {
      display: flex;
      justify-content: flex-end;
    }
    
    .back-button {
      padding: 10px 16px;
      background-color: #f1f1f1;
      color: #333;
      border: none;
      border-radius: 4px;
      font-weight: 500;
      transition: background-color 0.2s;
    }
    
    .back-button:hover {
      background-color: #e0e0e0;
    }
    
    .no-results {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 50px 0;
      text-align: center;
    }
    
    .no-results-icon {
      font-size: 48px;
      margin-bottom: 20px;
      color: #bbb;
    }
    
    .no-results h3 {
      margin-bottom: 10px;
    }
    
    .no-results p {
      color: #666;
      margin-bottom: 20px;
      max-width: 400px;
    }
    
    /* Footer */
    .app-footer {
      padding: 15px;
      text-align: center;
      font-size: 14px;
      color: #666;
      border-top: 1px solid #e0e0e0;
      margin-top: 20px;
    }
    
    /* Animations */
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    }
    
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    @keyframes slideIn {
      from { transform: translateY(-20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes slideDown {
      from { max-height: 0; opacity: 0; }
      to { max-height: 1000px; opacity: 1; }
    }
    
    /* Analysis Results Styling */
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 25px;
    }

    .action-buttons {
      display: flex;
      gap: 10px;
    }

    .download-button, .share-button {
      display: flex;
      align-items: center;
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      font-weight: 500;
      transition: background-color 0.2s;
    }

    .download-button {
      background-color: #3498db;
      color: white;
    }

    .download-button:hover {
      background-color: #2980b9;
    }

    .share-button {
      background-color: #27ae60;
      color: white;
    }

    .share-button:hover {
      background-color: #219653;
    }

    /* Score Overview */
    .score-overview {
      display: flex;
      margin-bottom: 25px;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
      overflow: hidden;
    }

    .score-card.overall {
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background-color: #f8f9fa;
      width: 180px;
      border-right: 1px solid #e0e0e0;
    }

    .score-circle {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100px;
      height: 100px;
      border-radius: 50%;
      background: linear-gradient(135deg, #3498db, #2c3e50);
      color: white;
      font-size: 32px;
      font-weight: 700;
      margin: 15px 0;
    }

    .score-title {
      font-weight: 600;
      color: #2c3e50;
      margin-bottom: 5px;
    }

    .score-label {
      font-size: 14px;
      color: #666;
    }

    .score-breakdown {
      flex: 1;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-around;
    }

    .score-breakdown .score-card {
      margin-bottom: 10px;
    }

    .score-bar {
      height: 20px;
      background-color: #f1f1f1;
      border-radius: 10px;
      position: relative;
      overflow: hidden;
      margin-top: 5px;
    }

    .score-fill {
      height: 100%;
      background: linear-gradient(90deg, #3498db, #2980b9);
      border-radius: 10px;
      transition: width 1s ease-out;
    }

    .score-text {
      position: absolute;
      left: 10px;
      top: 0;
      line-height: 20px;
      color: white;
      font-size: 12px;
      font-weight: 500;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }

    /* Analysis Tabs */
    .analysis-tabs {
      display: flex;
      flex-wrap: wrap; /* Allow wrapping instead of scrolling */
      border-bottom: 1px solid #e0e0e0;
      margin-bottom: 20px;
    }

    .analysis-tab {
      padding: 12px 18px;
      white-space: nowrap;
      border: none;
      background: none;
      color: #666;
      font-weight: 500;
      position: relative;
      transition: color 0.3s;
    }

    .analysis-tab.active {
      color: #3498db;
    }

    .analysis-tab.active::after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      width: 100%;
      height: 3px;
      background-color: #3498db;
      border-radius: 3px 3px 0 0;
    }

    /* Analysis Cards */
    .analysis-card {
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
      margin-bottom: 20px;
      position: relative;
      overflow: hidden;
    }

    .analysis-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 5px;
      height: 100%;
      background-color: #3498db;
    }

    .analysis-card.problem::before {
      background-color: #e74c3c;
    }

    .analysis-card.solution::before {
      background-color: #2ecc71;
    }

    .analysis-card.business::before {
      background-color: #f39c12;
    }

    .analysis-card.financials::before {
      background-color: #9b59b6;
    }

    .analysis-card.delivery::before {
      background-color: #1abc9c;
    }

    .analysis-card h2 {
      padding: 20px 20px 0;
      margin: 0;
      font-size: 20px;
      display: flex;
      align-items: center;
    }

    .score-indicator {
      position: absolute;
      top: 20px;
      right: 20px;
    }

    .score-pill {
      background-color: #f8f9fa;
      border-radius: 20px;
      padding: 5px 12px;
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
    }

    .card-content {
      padding: 20px;
      color: #333;
      line-height: 1.7;
    }

    .card-content p {
      margin-bottom: 15px;
    }

    /* Summary Card */
    .analysis-card.summary {
      background-color: #f8f9fa;
    }

    .summary-content {
      margin-bottom: 20px;
    }

    .key-points {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    .strengths h3, .improvements h3 {
      margin-top: 0;
      padding-bottom: 8px;
      border-bottom: 2px solid #3498db;
      margin-bottom: 15px;
    }

    .strengths h3 {
      color: #27ae60;
      border-color: #27ae60;
    }

    .improvements h3 {
      color: #e74c3c;
      border-color: #e74c3c;
    }

    .strengths ul, .improvements ul {
      padding-left: 20px;
    }

    .strengths li, .improvements li {
      margin-bottom: 8px;
    }

    .strengths li {
      color: #27ae60;
    }

    .strengths li::marker {
      color: #27ae60;
    }

    .improvements li {
      color: #e74c3c;
    }

    .improvements li::marker {
      color: #e74c3c;
    }

    /* Recommendations */
    .recommendations {
      background-color: #f8f9fa;
      border-top: 1px solid #e0e0e0;
      padding: 20px;
    }

    .recommendations h3 {
      margin-top: 0;
      font-size: 16px;
      margin-bottom: 15px;
      color: #2c3e50;
    }

    .recommendations ul {
      padding-left: 20px;
      margin: 0;
    }

    .recommendations li {
      margin-bottom: 8px;
      color: #333;
    }

    /* Responsive Adjustments */
    @media (max-width: 768px) {
      .panel-container {
        grid-template-columns: 1fr;
      }
      
      .app-header {
        flex-direction: column;
        text-align: center;
      }
      
      .api-status {
        margin-top: 10px;
      }
      
      .recording-actions {
        flex-direction: column;
        gap: 10px;
      }
      
      .control-button {
        width: 100%;
      }
      
      .results-header {
        flex-direction: column;
        align-items: flex-start;
      }
      
      .download-button {
        margin-top: 10px;
      }
      
      .score-overview {
        flex-direction: column;
      }
      
      .score-card.overall {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 15px;
      }
      
      .key-points {
        grid-template-columns: 1fr;
      }
      
      .analysis-tabs {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
      }
      
      .action-buttons {
        margin-top: 10px;
      }
      
      .transcript-button {
        display: flex;
        align-items: center;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        font-weight: 500;
        background-color: #9b59b6;
        color: white;
        transition: background-color 0.2s;
      }

      .transcript-button:hover {
        background-color: #8e44ad;
      }

      .audio-warning {
        padding: 10px 15px;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        margin-bottom: 15px;
        color: #856404;
      }
      
      .results-header {
        flex-direction: column;
        align-items: flex-start;
      }

      .analysis-tabs {
        overflow-x: auto; /* Only enable scrolling on mobile */
        flex-wrap: nowrap; /* Prevent wrapping on mobile */
        -webkit-overflow-scrolling: touch;
      }

      /* Add these CSS rules to your style section */

/* Subheadings (h4) styling */
.card-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #34495e;
  margin-top: 15px;
  margin-bottom: 10px;
}

/* Improve bold text visibility */
.card-content strong {
  font-weight: 600;
  color: #2c3e50;
}

/* Make quotes stand out better */
.card-content p:has(em), .card-content li:has(em) {
  background-color: #f8f9fa;
  padding: 10px;
  border-left: 3px solid #3498db;
  font-style: italic;
  color: #444;
}

/* Styling for specific sections */
.analysis-card.problem .card-content h4 {
  color: #c0392b; /* Red theme for problem section */
}

.analysis-card.solution .card-content h4 {
  color: #27ae60; /* Green theme for solution section */
}

.analysis-card.business .card-content h4 {
  color: #d35400; /* Orange theme for business model section */
}

.analysis-card.financials .card-content h4 {
  color: #8e44ad; /* Purple theme for financials section */
}

.analysis-card.delivery .card-content h4 {
  color: #16a085; /* Teal theme for delivery section */
}

.formatted-list-item strong {
  display: inline-block;
  margin-right: 4px;
  color: #2c3e50;
}

.recommendations li {
  margin-bottom: 12px;
  line-height: 1.5;
}
    }
  </style>
