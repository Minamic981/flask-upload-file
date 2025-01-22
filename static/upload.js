const now = new Date();
function createProgressBar(labelText, containerId, bgClass = 'bg-primary') {
    const progressBarsContainer = document.getElementById(containerId);
    const progressBarContainer = document.createElement("div");
    progressBarContainer.classList.add("mb-3");
    
    let progressBarLabel = document.createElement("span");
    progressBarLabel.textContent = labelText;
    progressBarLabel.classList.add("d-block", "mb-2");
    
    let progressBar = document.createElement("div");
    progressBar.classList.add("progress");
    
    let progressBarFill = document.createElement("div");
    progressBarFill.classList.add("progress-bar", "progress-bar-striped", "progress-bar-animated", bgClass);
    progressBarFill.setAttribute("role", "progressbar");
    progressBarFill.setAttribute("aria-valuenow", 0);
    progressBarFill.setAttribute("aria-valuemin", 0);
    progressBarFill.setAttribute("aria-valuemax", 100);
    progressBarFill.style.width = "0%";
    
    progressBar.appendChild(progressBarFill);
    progressBarContainer.appendChild(progressBarLabel);
    progressBarContainer.appendChild(progressBar);
    progressBarsContainer.appendChild(progressBarContainer);
    
    return { progressBarFill, progressBarLabel, progressBarContainer };
}

function updateProgressBar(progressBarFill, percent, label = '') {
    progressBarFill.style.width = percent + "%";
    progressBarFill.setAttribute("aria-valuenow", percent);
    if (label) {
        progressBarFill.parentElement.previousElementSibling.textContent = label;
    }
}

function fetchDownloadLink(fileName, progressBarContainer) {
    fetch("/get-link", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ file_name: fileName }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.link) {
                const downloadLink = document.createElement("a");
                downloadLink.textContent = "Link";
                downloadLink.href = data.link;
                downloadLink.classList.add("d-block", "mt-2", "text-success");
                downloadLink.target = "_blank"; // Open in a new tab
                progressBarContainer.appendChild(downloadLink);
            } else {
                alert("Failed to fetch download link.");
            }
        })
        .catch((error) => {
            console.error("Error fetching download link:", error);
            alert("Failed to fetch download link.");
        });
}

function generateFileName() {
    const formattedDate = now.toISOString().slice(2, 10).replace(/-/g, ''); // Format: YYMMDD
    const randomLetters = Math.random().toString(36).substring(2, 6); // Generate 4 random letters
    return `${formattedDate}-${randomLetters}.zip`;
}


function uploadFiles() {
    const files = document.getElementById("files").files;
    const CHUNK_SIZE = 2 * 1024 * 1024; // 2MB
    const isZipChecked = document.getElementById("zip").checked;
    const isShortlinkUrlChecked = document.getElementById("shortlinkurl").checked;
    
    if (isZipChecked) {
        // Create the zipping progress bar
        const { progressBarFill, progressBarLabel, progressBarContainer } = createProgressBar("Zipping files...", "progressBars", "bg-warning");
    
        // Zip the files using JSZip
        const zip = new JSZip();
        for (let i = 0; i < files.length; i++) {
            zip.file(files[i].name, files[i]);
        }
    
        // Generate the zip file with a progress callback
        zip.generateAsync({ type: "blob" }, (metadata) => {
        }).then((content) => {
            // Zipping is complete
            updateProgressBar(progressBarFill, 100, "Zipping complete!");
            // Remove the zipping progress bar
            setTimeout(() => {
                progressBarContainer.remove();},2000)
    
            // Create a new file from the zipped content and upload it
            const zipFile = new File([content], generateFileName(), { type: "application/zip" });
            uploadSingleFile(zipFile, isShortlinkUrlChecked);
        }).catch((error) => {
            progressBarLabel.textContent = `Error zipping files: ${error}`;
        });
    } else {
        // If zip is not selected, upload files individually
        for (let i = 0; i < files.length; i++) {
            uploadSingleFile(files[i], isShortlinkUrlChecked);
        }
    }
}



function uploadSingleFile(file, isShortlinkUrlChecked) {
    // Create a progress bar for file upload
    const { progressBarFill, progressBarLabel } = createProgressBar(`Uploading ${file.name}...`, "progressBars");

    // Start uploading the file in chunks
    const CHUNK_SIZE = 2 * 1024 * 1024; // 2MB
    let offset = 0;
    let totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    
    function uploadChunk() {
        let chunk = file.slice(offset, offset + CHUNK_SIZE);
        let formData = new FormData();
        formData.append("file", chunk);
        formData.append("fileName", file.name);
        formData.append("chunkIndex", Math.floor(offset / CHUNK_SIZE));
        formData.append("totalChunks", totalChunks);
    
        // If "Shortlink URL" is checked, add the "shortlink" parameter in the first chunk
        if (isShortlinkUrlChecked && offset === totalChunks) {
            formData.append("shortlink", true);
        }
    
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload", true);
    
        xhr.onload = function () {
            if (xhr.status === 200) {
                offset += CHUNK_SIZE;
    
                // Update progress bar based on chunks uploaded
                let percent = ((offset / file.size) * 100).toFixed(2);
                updateProgressBar(progressBarFill, percent);
    
                if (offset < file.size) {
                    uploadChunk(); // Continue uploading the next chunk
                } else {
                    progressBarLabel.textContent = `${file.name} uploaded successfully!`;
                    progressBarFill.classList.remove("progress-bar-animated");
                    progressBarFill.classList.add("bg-success");
                    updateProgressBar(progressBarFill, 100);
    
                    // Fetch the download link for the fully uploaded file
                    fetchDownloadLink(file.name, progressBarLabel);
                }
            } else {
                progressBarLabel.textContent = `Error uploading chunk ${Math.floor(offset / CHUNK_SIZE)} of ${file.name}`;
            }
        };
    
        xhr.onerror = function () {
            progressBarLabel.textContent = `Network error while uploading ${file.name}`;
        };
    
        xhr.send(formData);
    }
    
    // Start uploading the first chunk
    uploadChunk();
}