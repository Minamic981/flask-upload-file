let stopwatchInterval;
let elapsedTime = 0;

function startStopwatch() {
    elapsedTime = 0;
    const stopwatchDisplay = document.getElementById('stopwatch');
    stopwatchDisplay.textContent = `Elapsed Time: 0 seconds`;

    stopwatchInterval = setInterval(() => {
        elapsedTime++;
        stopwatchDisplay.textContent = `Elapsed Time: ${elapsedTime} seconds`;
    }, 1000);
}

function stopStopwatch() {
    clearInterval(stopwatchInterval);
}

async function uploadChunk(chunk, fileName, chunkNumber, totalChunks) {
    const formData = new FormData();
    formData.append('file', chunk);
    formData.append('filename', fileName);
    formData.append('chunkNumber', chunkNumber);
    formData.append('totalChunks', totalChunks);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Failed to upload chunk ${chunkNumber} of file ${fileName}.`);
    }

    return await response.text();
}

async function handleFileUpload(file) {
    const chunkSize = 2 * 1024 * 1024; // 2MB
    const totalChunks = Math.ceil(file.size / chunkSize);
    const fileName = file.name;
    const chunks = [];

    for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);

        chunks.push(() => uploadChunk(chunk, fileName, i + 1, totalChunks));
    }

    return { fileName, chunks };
}

async function uploadChunksInBatches(chunks, batchSize) {
    for (let i = 0; i < chunks.length; i += batchSize) {
        const batch = chunks.slice(i, i + batchSize).map(fn => fn());
        await Promise.all(batch);
    }
}

async function getDownloadLink(filename) {
    try {
        const response = await fetch(`/getlink?filename=${encodeURIComponent(filename)}`);
        if (!response.ok) {
            throw new Error('Failed to get download link.');
        }
        const link = await response.text();
        return link;
    } catch (error) {
        console.error('Error fetching download link:', error);
        return null;
    }
}

async function handleSubmit(event) {
    event.preventDefault();
    const fileInput = document.getElementById('file');
    const files = Array.from(fileInput.files);
    const linksContainer = document.getElementById('download-links');
    linksContainer.innerHTML = ''; // Clear previous links

    if (files.length === 0) {
        document.getElementById('message').textContent = 'Please select files to upload.';
        return;
    }

    startStopwatch();

    try {
        const allChunks = [];
        const uploadedFiles = [];

        for (const file of files) {
            const { fileName, chunks } = await handleFileUpload(file);
            allChunks.push(...chunks);
            uploadedFiles.push(fileName);
        }

        await uploadChunksInBatches(allChunks, 4); // Upload 4 chunks at a time

        stopStopwatch();
        document.getElementById('message').textContent = 'All files uploaded successfully!';

        // Display download links
        for (const fileName of uploadedFiles) {
            const link = await getDownloadLink(fileName);
            if (link) {
                const linkElement = document.createElement('a');
                linkElement.href = link;
                linkElement.textContent = 'Link';
                linkElement.target = '_blank';

                const listItem = document.createElement('div');
                listItem.textContent = `Download ${fileName}: `;
                listItem.appendChild(linkElement);

                linksContainer.appendChild(listItem);
            }
        }
    } catch (error) {
        stopStopwatch();
        document.getElementById('message').textContent = `Error: ${error.message}`;
    }
}