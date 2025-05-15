// Pipeline Panic - Game interactions

document.addEventListener('DOMContentLoaded', function() {
    // Set up pipeline progress visualization
    updatePipelineProgress();
    
    // Add clouds for background effect
    createClouds();

    // Set up choice button event listeners
    setupChoiceButtons();
    
    // This is important - ensure buttons are always reset when page loads
    resetChoiceButtons();
});

/**
 * Updates the pipeline progress visualization based on current game state
 */
function updatePipelineProgress() {
    const currentStage = document.querySelector('.stage-current');
    if (!currentStage) return; // Guard clause if no current stage is found
    
    const stageIndex = currentStage.dataset.stageIndex;
    const totalStages = document.querySelectorAll('.stage').length;
    
    // Calculate progress percentage
    const progressPercentage = (stageIndex / (totalStages - 1)) * 100;
    
    // Update progress bar width
    const progressBar = document.querySelector('.pipeline-progress');
    if (progressBar) {
        progressBar.style.width = `${progressPercentage}%`;
    }
}

/**
 * Creates cloud elements in the background for visual effect
 */
function createClouds() {
    const cloudContainer = document.querySelector('.cloud-container');
    if (!cloudContainer) return;
    
    const numberOfClouds = 5;
    
    for (let i = 0; i < numberOfClouds; i++) {
        const cloud = document.createElement('div');
        cloud.className = 'cloud';
        
        // Randomize cloud properties
        const width = Math.random() * 200 + 100;
        const height = width * 0.4;
        const top = Math.random() * 80;
        const left = Math.random() * 80;
        const animationDuration = Math.random() * 20 + 10;
        
        // Apply styles
        cloud.style.width = `${width}px`;
        cloud.style.height = `${height}px`;
        cloud.style.top = `${top}%`;
        cloud.style.left = `${left}%`;
        cloud.style.animation = `float ${animationDuration}s infinite linear alternate-reverse`;
        
        cloudContainer.appendChild(cloud);
    }
}

/**
 * Sets up choice button interaction and hover effects
 */
function setupChoiceButtons() {
    const choiceButtons = document.querySelectorAll('.choice-btn');
    
    choiceButtons.forEach(button => {
        // Store the original button text in a data attribute for reference
        const buttonText = button.innerHTML;
        button.dataset.originalText = buttonText;
        
        // Add hover sound effect (commented out for now)
        // button.addEventListener('mouseenter', () => playHoverSound());
        
        // Add click effect
        button.addEventListener('click', function() {
            // Disable all buttons to prevent multiple submissions
            choiceButtons.forEach(btn => btn.disabled = true);
            
            // Add loading spinner to clicked button
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...';
            
            // Add a timeout just in case the form submission fails
            setTimeout(() => {
                resetChoiceButtons();
            }, 3000);
        });
    });
}

/**
 * Resets all choice buttons to their original state
 */
function resetChoiceButtons() {
    const choiceButtons = document.querySelectorAll('.choice-btn');
    
    choiceButtons.forEach(button => {
        // Enable the button
        button.disabled = false;
        
        // Restore original text if it was saved
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        } else {
            // Fallback if original text wasn't saved
            const choiceText = button.getAttribute('value');
            button.innerHTML = choiceText || 'Make Choice';
        }
    });
}

/**
 * Displays a toast notification with feedback about player's choice
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error)
 */
function showNotification(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const toastContent = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toast.innerHTML = toastContent;
    
    // Add toast to container
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
        toastContainer.appendChild(toast);
        
        // Initialize and show the toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

/**
 * Simulates pipeline flow animation when advancing to next stage
 */
function animatePipelineAdvance() {
    const pipeline = document.querySelector('.pipeline-container');
    pipeline.classList.add('pulse');
    
    setTimeout(() => {
        pipeline.classList.remove('pulse');
    }, 2000);
}
