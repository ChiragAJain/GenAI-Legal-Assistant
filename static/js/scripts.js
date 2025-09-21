document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('fileInfo');
    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');
    const summaryText = document.getElementById('summaryText');
    const downloadLink = document.getElementById('downloadLink');
    const feedbackSection = document.getElementById('feedbackSection');
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackTextarea = document.getElementById('feedback');
    const feedbackStatus = document.getElementById('feedbackStatus');
    
    // Q&A elements
    const qaSection = document.getElementById('qaSection');
    const qaForm = document.getElementById('qaForm');
    const questionInput = document.getElementById('questionInput');
    const qaHistory = document.getElementById('qaHistory');

    // File input handling with drag and drop
    const fileUploadLabel = document.querySelector('.file-upload-label');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileUploadLabel.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        fileUploadLabel.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileUploadLabel.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    fileUploadLabel.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        fileUploadLabel.style.borderColor = 'var(--primary-color)';
        fileUploadLabel.style.backgroundColor = '#f1f5f9';
    }

    function unhighlight(e) {
        fileUploadLabel.style.borderColor = 'var(--border-color)';
        fileUploadLabel.style.backgroundColor = '#f8fafc';
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            displayFileInfo(files[0]);
        }
    }

    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            displayFileInfo(e.target.files[0]);
        }
    });

    function displayFileInfo(file) {
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        const maxSize = 8; // 8MB limit
        
        if (fileSize > maxSize) {
            fileInfo.innerHTML = `
                <div style="color: var(--error-color);">
                    ⚠️ File too large: ${fileSize}MB (max ${maxSize}MB)
                </div>
            `;
            fileInfo.style.display = 'block';
            fileInfo.style.background = '#fef2f2';
            fileInfo.style.borderColor = 'var(--error-color)';
            return;
        }

        fileInfo.innerHTML = `
            <div style="color: var(--success-color);">
                ✓ ${file.name} (${fileSize}MB)
            </div>
        `;
        fileInfo.style.display = 'block';
        fileInfo.style.background = '#ecfdf5';
        fileInfo.style.borderColor = 'var(--success-color)';
    }

    // Handle form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files.length) {
            showNotification('Please select a file first', 'error');
            return;
        }

        const formData = new FormData(uploadForm);

        // Hide previous results and show loader
        resultDiv.style.display = 'none';
        qaSection.style.display = 'none';
        feedbackSection.style.display = 'none';
        loader.style.display = 'flex';
        
        // Clear previous Q&A history
        qaHistory.innerHTML = '';

        // Scroll to loader
        loader.scrollIntoView({ behavior: 'smooth', block: 'center' });

        try {
            const response = await fetch('/upload', { 
                method: 'POST', 
                body: formData 
            });
            
            const data = await response.json();

            // Hide loader
            loader.style.display = 'none';

            if (response.ok && data.summary) {
                // Format and show results
                summaryText.innerHTML = formatSummaryText(data.summary);
                downloadLink.href = data.download_link;
                resultDiv.style.display = 'block';
                
                // Show Q&A section if document is available
                if (data.has_document) {
                    qaSection.style.display = 'block';
                }
                
                feedbackSection.style.display = 'block';
                
                // Scroll to results
                resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                showNotification('Analysis generated successfully!', 'success');
            } else {
                showNotification(data.error || 'An error occurred while processing your file', 'error');
            }
        } catch (error) {
            loader.style.display = 'none';
            showNotification('Network error. Please check your connection and try again.', 'error');
            console.error('Upload error:', error);
        }
    });

    // Handle Q&A form submission
    qaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        if (!question) {
            showNotification('Please enter a question', 'error');
            return;
        }
        
        // Add question to history immediately
        const qaItem = document.createElement('div');
        qaItem.className = 'qa-item';
        qaItem.innerHTML = `
            <div class="qa-question">Q: ${question}</div>
            <div class="qa-loading">
                <div class="spinner"></div>
                <span>Getting answer...</span>
            </div>
        `;
        qaHistory.appendChild(qaItem);
        
        // Clear input and disable form
        const askBtn = qaForm.querySelector('.ask-btn');
        const originalText = askBtn.querySelector('.btn-text').textContent;
        askBtn.querySelector('.btn-text').textContent = 'Asking...';
        askBtn.disabled = true;
        questionInput.value = '';
        
        // Scroll to the new question
        qaItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            
            const data = await response.json();
            
            // Replace loading with answer
            const loadingDiv = qaItem.querySelector('.qa-loading');
            if (response.ok && data.answer) {
                loadingDiv.outerHTML = `<div class="qa-answer">${data.answer}</div>`;
            } else {
                loadingDiv.outerHTML = `<div class="qa-answer" style="color: var(--error-color);">Error: ${data.error || 'Failed to get answer'}</div>`;
            }
            
        } catch (error) {
            // Replace loading with error
            const loadingDiv = qaItem.querySelector('.qa-loading');
            loadingDiv.outerHTML = `<div class="qa-answer" style="color: var(--error-color);">Network error. Please try again.</div>`;
            console.error('Q&A error:', error);
        } finally {
            // Re-enable form
            askBtn.querySelector('.btn-text').textContent = originalText;
            askBtn.disabled = false;
        }
    });

    // Handle feedback submission
    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const feedback = feedbackTextarea.value.trim();
        
        if (feedback === '') {
            showFeedbackStatus('Please enter your feedback', 'error');
            return;
        }
        
        // Disable submit button during submission
        const submitBtn = feedbackForm.querySelector('.feedback-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Submitting...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback })
            });
            
            const data = await response.json();
            
            if (response.ok && data.status) {
                showFeedbackStatus('Thank you for your feedback!', 'success');
                feedbackTextarea.value = '';
            } else {
                showFeedbackStatus(data.error || 'Failed to submit feedback', 'error');
            }
        } catch (error) {
            showFeedbackStatus('Network error. Please try again.', 'error');
            console.error('Feedback error:', error);
        } finally {
            // Re-enable submit button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });

    function showFeedbackStatus(message, type) {
        feedbackStatus.textContent = message;
        feedbackStatus.className = `feedback-status ${type}`;
        feedbackStatus.style.display = 'block';
        
        // Hide status after 5 seconds
        setTimeout(() => {
            feedbackStatus.style.display = 'none';
        }, 5000);
    }

    function formatSummaryText(rawText) {
        /**
         * Enhanced text formatting for better readability
         */
        let formattedText = rawText;
        
        // Format main headers (surrounded by =)
        formattedText = formattedText.replace(
            /={10,}\s*\n([^=\n]+)\n={10,}/g,
            '<h1>$1</h1>'
        );
        
        // Format section headers (📋 or 🔍 followed by text)
        formattedText = formattedText.replace(
            /^(📋|🔍)\s*([^\n]+)$/gm,
            '<div class="section-header">$2</div>'
        );
        
        // Format numbered points (1. 2. 3. etc.)
        formattedText = formattedText.replace(
            /^(\d+\.\s+)(.+)$/gm,
            '<div class="numbered-point"><strong>$1</strong>$2</div>'
        );
        
        // Format key terms
        formattedText = formattedText.replace(
            /^(📋\s*)?Key Terms:\s*(.+)$/gm,
            '<div class="key-terms"><strong>🔑 Key Terms:</strong> $2</div>'
        );
        
        // Format disclaimers and warnings
        formattedText = formattedText.replace(
            /^⚠️\s*(.+)$/gm,
            '<div class="disclaimer"><strong>⚠️ $1</strong></div>'
        );
        
        // Format separators
        formattedText = formattedText.replace(
            /^-{10,}$/gm,
            '<hr class="separator">'
        );
        
        // Format subsection headers (lines ending with colon and in caps)
        formattedText = formattedText.replace(
            /^([A-Z\s&]{3,}):$/gm,
            '<h3>$1</h3>'
        );
        
        // Convert line breaks to proper HTML
        formattedText = formattedText.replace(/\n\n/g, '</p><p>');
        formattedText = formattedText.replace(/\n/g, '<br>');
        
        // Wrap in paragraphs
        if (!formattedText.startsWith('<')) {
            formattedText = '<p>' + formattedText + '</p>';
        }
        
        // Clean up empty paragraphs
        formattedText = formattedText.replace(/<p><\/p>/g, '');
        formattedText = formattedText.replace(/<p><br><\/p>/g, '');
        
        return formattedText;
    }

    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${type === 'success' ? '✓' : '⚠️'}</span>
                <span class="notification-message">${message}</span>
            </div>
        `;
        
        // Add notification styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? 'var(--success-color)' : 'var(--error-color)'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 400px;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    }

    // Add some additional CSS for notifications
    const style = document.createElement('style');
    style.textContent = `
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .notification-icon {
            font-size: 1.25rem;
        }
        
        .notification-message {
            font-weight: 500;
        }
        
        @media (max-width: 480px) {
            .notification {
                right: 10px;
                left: 10px;
                max-width: none;
            }
        }
    `;
    document.head.appendChild(style);
});
