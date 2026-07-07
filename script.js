let statusSource = null;

const API_BASE_URL = window.location.origin;



// remove the slug input value and reset its validity state
//  after the book is donwnloaded
function resetSlugInput() {
    const slugInput = document.getElementById('slug-input');
    if (!slugInput) return;

    slugInput.value = '';
    slugInput.setCustomValidity('');
    slugInput.blur();
}

// continously apply the updates on frontend
function applyStatusUpdate(data) {
    const progressText = document.getElementById('progress-text');
    const progressBar = document.getElementById('progress-bar');
    const rawImg = document.getElementById('raw-img');
    const restoredImg = document.getElementById('restored-img');
    const bookName = document.getElementById('slug-input');

    // update progress bar
    if (data.total_pages > 0) {
        const percentage = Math.min(100, ((data.completed_count / data.total_pages) * 100).toFixed(0));
        progressText.innerText = `Processing: ${data.completed_count} / ${data.total_pages} Pages (${percentage}%)`;
        progressBar.value = Number(percentage);
    }
// update images if available
    if (data.raw_latest_page) {
        rawImg.src = `raw/${data.latest_page}`;
    }

    if (data.restored_latest_page) {
        restoredImg.src = `restored/${data.restored_latest_page}`;
    }

    if (data.status === 'completed') {
        closeStatusStream();
        progressText.innerText = `Completed! Book ${bookName.value} downloaded successfully.`;

        const downloadBtn = document.getElementById('download-button');
        downloadBtn.disabled = false;
        downloadBtn.innerText = 'Download';
        rawImg.src = "raw/urdu-scrambled.png";
        restoredImg.src = "restored/urdu-restored.png";
        progressBar.value = 0;
        resetSlugInput();

    }
    if (data.status === 'pdf_creation_failed') {
        closeStatusStream();
        progressText.innerText ='Failed to create PDF. Invalid book name. Make sure you have entered the correct slug and try again.';

        const downloadBtn = document.getElementById('download-button');
        downloadBtn.disabled = false;
        downloadBtn.innerText = 'Download';
        rawImg.src = "raw/urdu-scrambled.png";
        restoredImg.src = "restored/urdu-restored.png";
        progressBar.value = 0;
        resetSlugInput();

    }
}

function closeStatusStream() {
    if (statusSource) {
        statusSource.close();
        statusSource = null;
    }
}

function startStatusStream() {
    closeStatusStream();

    statusSource = new EventSource(`${API_BASE_URL}/status-stream`);

    statusSource.addEventListener('status', (event) => {
      
        const data = JSON.parse(event.data);
        try {
           applyStatusUpdate(data);
        }
        catch (error) {
            console.error('Failed to parse status update:', error);
        }
    });

    statusSource.onerror = (event) => {
        console.error('Status stream error:', event);
    };
}

function placeSlugHelpForViewport() {
    const slugHelp = document.getElementById('slug-help');
    const instructionBox = document.getElementById('instruction');
    const downloader = document.getElementById('downloader');
    const imagesContainer = document.getElementById('images-container');

    if (!slugHelp || !instructionBox || !downloader || !imagesContainer) {
        return;
    }

    if (window.innerWidth <= 768) {
        imagesContainer.insertAdjacentElement('afterend', slugHelp);
        slugHelp.insertAdjacentElement('afterend', instructionBox);
    } else {
        downloader.appendChild(slugHelp);
        downloader.appendChild(instructionBox);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const downloadBtn = document.getElementById('download-button');
    const slugInput = document.getElementById('slug-input');
    const slugHelp = document.getElementById('slug-help');
    const slugInstruction = document.getElementById('slug-instruction');
    const instructionBox = document.getElementById('instruction');
    const hideInstructionBtn = document.getElementById('hide-instruction-btn');

    const openInstructions = () => {
        instructionBox.style.display = 'block';
    };

    const closeInstructions = () => {
        instructionBox.style.display = 'none';
    };

    downloadBtn.addEventListener('click', async (event) => {
        event.preventDefault();

        const slugValue = slugInput.value.trim();
        const progressText = document.getElementById('progress-text');

        if (/[\\/]/.test(slugValue)) {
            alert('Invalid slug: remove / or \\ characters before downloading.');
            progressText.innerText = 'Invalid slug. Remove / or \\ and try again.';
            return;
        }

        if (!slugValue) {
            alert('Please enter a book name first!');
            return;
        }

        downloadBtn.disabled = true;
        downloadBtn.innerText = 'Downloading...';
        progressText.innerText = 'Starting task...';

        try {
            const response = await fetch(`${API_BASE_URL}/download`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slug: slugValue })
            });

            const data = await response.json();

            if (response.ok) {
                const initialStatusResponse = await fetch(`${API_BASE_URL}/status`);
                const initialStatus = await initialStatusResponse.json();
                applyStatusUpdate(initialStatus);
                startStatusStream();
            } else {
                alert('Error from script: ' + data.message);
                downloadBtn.disabled = false;
                downloadBtn.innerText = 'Download';
            }

        } catch (error) {
            console.error('Failed to connect to server:', error);
            alert('Could not connect to the Python server. Make sure server.py is running!');
            downloadBtn.disabled = false;
            downloadBtn.innerText = 'Download';
        }
    });

    if (slugHelp) {
        slugHelp.style.cursor = 'pointer';
        slugHelp.addEventListener('click', openInstructions);
    }

    if (slugInstruction) {
        slugInstruction.addEventListener('click', (event) => {
            event.stopPropagation();
            openInstructions();
        });
    }

    hideInstructionBtn.addEventListener('click', closeInstructions);

    placeSlugHelpForViewport();
    window.addEventListener('resize', placeSlugHelpForViewport, { passive: true });
});