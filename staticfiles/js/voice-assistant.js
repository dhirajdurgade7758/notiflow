/**
 * VoiceAssistant - Based on Jarvis voice recognition patterns
 * Uses Web Speech API for browser-native speech recognition and synthesis
 */

class VoiceAssistant {
  constructor() {
    // Speech Recognition Setup (similar to sr.Recognizer from main.py)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn("Speech Recognition API not supported in this browser");
      this.supported = false;
      return;
    }
    
    this.supported = true;
    this.recognizer = new SpeechRecognition();
    this.recognizer.continuous = false;
    this.recognizer.interimResults = true;
    this.recognizer.lang = 'en-US';
    
    // Speech Synthesis Setup (similar to pyttsx3 from main.py)
    this.synth = window.speechSynthesis;
    
    // State tracking
    this.isListening = false;
    this.finalTranscript = '';
    this.interimTranscript = '';
    this.attempts = 0;
    this.maxAttempts = 3;
    
    // UI Elements (will be set by init)
    this.micBtn = null;
    this.inputField = null;
    this.statusDisplay = null;
    this.transcriptDisplay = null;
    this.modal = null;
    
    // Setup event listeners
    this._setupRecognitionListeners();
  }
  
  /**
   * Initialize voice assistant with DOM elements
   */
  init(micBtnSelector, inputSelector, statusSelector = null, transcriptSelector = null) {
    console.log('🔧 Voice Assistant init called with selectors:', { micBtnSelector, inputSelector });
    
    this.micBtn = document.querySelector(micBtnSelector);
    this.inputField = document.querySelector(inputSelector);
    this.statusDisplay = document.querySelector(statusSelector);
    this.transcriptDisplay = document.querySelector(transcriptSelector);
    
    console.log('🔍 Found elements:', {
      micBtn: !!this.micBtn,
      inputField: !!this.inputField,
      statusDisplay: !!this.statusDisplay,
      transcriptDisplay: !!this.transcriptDisplay
    });
    
    if (!this.micBtn || !this.inputField) {
      console.error("❌ Voice Assistant: Required DOM elements not found");
      console.error("  micBtn found:", !!this.micBtn);
      console.error("  inputField found:", !!this.inputField);
      return false;
    }
    
    // Remove any existing click listeners by replacing button
    const oldBtn = this.micBtn;
    const newBtn = oldBtn.cloneNode(true);
    oldBtn.parentNode.replaceChild(newBtn, oldBtn);
    this.micBtn = newBtn;
    
    // Add click listener
    this.micBtn.addEventListener('click', (e) => {
      console.log('🔘 Direct mic button click event triggered');
      e.preventDefault();
      e.stopPropagation();
      this.toggleListening();
    });
    
    console.log('✅ Voice Assistant init complete, mic listener attached');
    return true;
  }
  
  /**
   * Toggle listening state (start/stop recording)
   */
  toggleListening() {
    if (!this.supported) {
      this._showError("Speech recognition is not supported in your browser. Please try Chrome, Edge, or Safari.");
      return;
    }
    
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }
  
  /**
   * Start listening for voice input
   */
  startListening() {
    this.finalTranscript = '';
    this.interimTranscript = '';
    this.isListening = true;
    this.attempts++;
    
    this._updateMicButton('listening');
    this._updateStatus(`🎤 Listening... (Attempt ${this.attempts}/${this.maxAttempts})`);
    
    try {
      this.recognizer.start();
    } catch (e) {
      // Already listening
      console.log("Already listening...");
    }
  }
  
  /**
   * Stop listening
   */
  stopListening() {
    this.isListening = false;
    this.recognizer.stop();
    this._updateMicButton('idle');
  }
  
  /**
   * Setup speech recognition event listeners
   */
  _setupRecognitionListeners() {
    this.recognizer.onstart = () => {
      this._updateStatus("🎙️ Microphone is active...");
    };
    
    this.recognizer.onresult = (event) => {
      this.interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          this.finalTranscript += transcript + ' ';
        } else {
          this.interimTranscript += transcript;
        }
      }
      
      // Display real-time transcription
      const displayText = this.finalTranscript + this.interimTranscript;
      this._updateTranscript(displayText);
      this._updateStatus(`📝 You said: ${displayText}`);
    };
    
    this.recognizer.onerror = (event) => {
      let errorMsg = "Error: ";
      
      switch (event.error) {
        case 'no-speech':
          errorMsg += "No speech detected. Please try again.";
          break;
        case 'audio-capture':
          errorMsg += "Microphone not found. Check your device settings.";
          break;
        case 'network':
          errorMsg += "Network error. Check your internet connection.";
          break;
        case 'permission-denied':
          errorMsg += "Microphone permission denied. Check browser settings.";
          break;
        default:
          errorMsg += event.error;
      }
      
      this._showError(errorMsg);
      this.stopListening();
    };
    
    this.recognizer.onend = () => {
      this.isListening = false;
      
      if (this.finalTranscript.trim()) {
        this._processVoiceInput(this.finalTranscript.trim());
      } else {
        this._showError("I didn't catch that. Could you please say it again?");
        this._updateMicButton('idle');
        
        if (this.attempts < this.maxAttempts) {
          this._updateStatus(`Try again (${this.attempts}/${this.maxAttempts})`);
        } else {
          this._showError(`Max retries reached. Please use manual input.`);
          this.attempts = 0;
        }
      }
    };
  }
  
  /**
   * Process voice input - send to form and handle response
   */
  _processVoiceInput(transcript) {
    const trimmedText = transcript.trim();
    
    // Check for wake word "hey notiflow"
    if (trimmedText.toLowerCase().includes('hey notiflow')) {
      this.speak("I'm listening");
      // Remove wake word and continue listening
      const cleaned = trimmedText.replace(/hey\s+notiflow/i, '').trim();
      if (cleaned.length > 0) {
        this.finalTranscript = cleaned;
      } else {
        // Continue listening for actual reminder
        this._updateStatus("Waiting for reminder details...");
        setTimeout(() => this.startListening(), 500);
        return;
      }
    }
    
    // Fill the input field with transcribed text
    if (this.inputField) {
      this.inputField.value = trimmedText;
      this._updateStatus(`✅ Transcribed: "${trimmedText}"`);
      
      // Optional: Auto-submit after a short delay
      setTimeout(() => {
        this._updateStatus("Processing your reminder...");
      }, 500);
    }
    
    this._updateMicButton('complete');
  }
  
  /**
   * Speak text using browser's SpeechSynthesis API (like pyttsx3)
   */
  speak(text) {
    if (!this.synth) {
      console.warn("Speech Synthesis not supported");
      return;
    }
    
    // Cancel any ongoing speech
    this.synth.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.9; // Slower speech (similar to main.py's rate=130)
    utterance.volume = 1.0;
    
    this.synth.speak(utterance);
  }
  
  /**
   * Show confirmation message with voice
   */
  confirmReminder(reminderDetails) {
    const confirmText = `Reminder scheduled for ${reminderDetails.time || 'the specified time'} with title: ${reminderDetails.title || 'Untitled'}`;
    this._showSuccess(confirmText);
    this.speak(confirmText);
  }
  
  /**
   * Update mic button state visually
   */
  _updateMicButton(state) {
    if (!this.micBtn) return;
    
    this.micBtn.className = '';
    
    switch (state) {
      case 'listening':
        this.micBtn.classList.add('btn', 'btn-danger', 'btn-sm', 'animate-pulse');
        this.micBtn.innerHTML = '<i class="bi bi-mic-fill"></i> Listening...';
        this.micBtn.disabled = false;
        break;
      case 'complete':
        this.micBtn.classList.add('btn', 'btn-success', 'btn-sm');
        this.micBtn.innerHTML = '<i class="bi bi-check-circle"></i> Done';
        this.micBtn.disabled = false;
        break;
      case 'idle':
      default:
        this.micBtn.classList.add('btn', 'btn-outline-primary', 'btn-sm');
        this.micBtn.innerHTML = '<i class="bi bi-mic"></i> Speak';
        this.micBtn.disabled = false;
        break;
    }
  }
  
  /**
   * Update status display
   */
  _updateStatus(message) {
    if (this.statusDisplay) {
      this.statusDisplay.textContent = message;
      this.statusDisplay.style.display = 'block';
    }
  }
  
  /**
   * Update transcript display
   */
  _updateTranscript(text) {
    if (this.transcriptDisplay) {
      this.transcriptDisplay.textContent = text;
      this.transcriptDisplay.style.display = 'block';
    }
  }
  
  /**
   * Show error message
   */
  _showError(message) {
    this._updateStatus(`❌ ${message}`);
    this.speak(message);
  }
  
  /**
   * Show success message
   */
  _showSuccess(message) {
    this._updateStatus(`✅ ${message}`);
  }
  
  /**
   * Detect wake word "hey notiflow" in any transcribed text
   */
  static detectWakeWord(text) {
    return text.toLowerCase().includes('hey notiflow');
  }
}

// Global instance
let voiceAssistant = null;

/**
 * Initialize voice assistant when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
  // Create global instance
  voiceAssistant = new VoiceAssistant();
  
  // Log if supported
  if (voiceAssistant.supported) {
    console.log("✅ Voice Assistant initialized successfully");
  } else {
    console.log("⚠️ Voice Assistant not supported in this browser");
  }
});

/**
 * Event delegation for mic button clicks (works with HTMX-loaded modals)
 */
document.addEventListener('click', function(e) {
  console.log('🖱️ Click detected on:', e.target.id, e.target.className);
  
  const micBtn = e.target.closest('#voice-mic-btn');
  if (micBtn && voiceAssistant) {
    console.log('🔘✅ Mic button clicked via delegation');
    e.preventDefault();
    e.stopPropagation();
    voiceAssistant.toggleListening();
    return;
  }
}, true); // useCapture = true to catch all clicks

// Also monitor when modal is shown
document.addEventListener('shown.bs.modal', function(e) {
  console.log('📢 Bootstrap modal shown:', e.target.id);
  const micBtn = document.getElementById('voice-mic-btn');
  console.log('🎤 Mic button found:', !!micBtn);
  if (micBtn && voiceAssistant && !voiceAssistant.micBtn) {
    console.log('🔧 Manually initializing voice assistant after modal shown');
    voiceAssistant.init(
      '#voice-mic-btn',
      '#smart-input',
      '#voice-status',
      '#voice-transcript'
    );
  }
});

// Monitor HTMX events more aggressively
document.addEventListener('htmx:afterSwap', function(evt) {
  console.log('📦 HTMX afterSwap event:', evt.detail.target.id, evt.detail.target);
  
  // Check for modal content or any element with mic button
  const micBtn = document.getElementById('voice-mic-btn');
  if (micBtn) {
    console.log('✅ Found mic button after HTMX swap, reinitializing...');
    if (voiceAssistant) {
      voiceAssistant.init(
        '#voice-mic-btn',
        '#smart-input',
        '#voice-status',
        '#voice-transcript'
      );
    }
  }
});
