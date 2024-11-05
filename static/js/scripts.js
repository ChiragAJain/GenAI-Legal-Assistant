document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');
    const summaryText = document.getElementById('summaryText');
    const downloadLink = document.getElementById('downloadLink');
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackTextarea = document.getElementById('feedback');
    const feedbackStatus = document.getElementById('feedbackStatus');

    // Handle file upload and summary generation
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(uploadForm);

        // Hide result and feedback sections, show loader
        resultDiv.style.display = 'none';
        feedbackForm.style.display = 'none';
        loader.style.display = 'flex';

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const data = await response.json();

            // Hide loader, show results
            loader.style.display = 'none';

            if (data.summary) {
                summaryText.textContent = data.summary;
                downloadLink.href = data.download_link;
                resultDiv.style.display = 'block';
                feedbackForm.style.display = 'block';
            } else {
                alert(data.error || 'An error occurred');
            }
        } catch (error) {
            // Hide loader in case of error
            loader.style.display = 'none';
            alert('Failed to upload file and generate summary');
        }
    });

    // Handle feedback submission
    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const feedback = feedbackTextarea.value.trim();
        
        if (feedback === '') {
            feedbackStatus.textContent = 'Please enter feedback';
            feedbackStatus.style.color = 'red';
            return;
        }
        
        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback })
            });
            const data = await response.json();
            
            if (data.status) {
                feedbackStatus.textContent = 'Feedback submitted successfully';
                feedbackStatus.style.color = 'green';
                feedbackTextarea.value = '';
            } else {
                feedbackStatus.textContent = data.error || 'Failed to submit feedback';
                feedbackStatus.style.color = 'red';
            }
        } catch (error) {
            feedbackStatus.textContent = 'Error submitting feedback';
            feedbackStatus.style.color = 'red';
        }
    });
});
