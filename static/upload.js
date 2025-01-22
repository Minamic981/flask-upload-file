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
    
    function uploadFiles() {
        const files = document.getElementById("files").files;
        const progressBarsContainer = document.getElementById("progressBars");
        const CHUNK_SIZE = 2 * 1024 * 1024; // 2MB
        const isZipChecked = document.getElementById("zip").checked;
        const isShortlinkUrlChecked = document.getElementById("shortlinkurl").checked;
        
        if (isZipChecked) {
            // Zip the files using JSZip
            const zip = new JSZip();
            for (let i = 0; i < files.length; i++) {
                zip.file(files[i].name, files[i]);
            }
        
            // Generate the zip file
            zip.generateAsync({ type: "blob" }).then(function (content) {
                // Create a new file from the zipped content and upload it
                const zipFile = new File([content], "files.zip", { type: "application/zip" });
                uploadSingleFile(zipFile, isShortlinkUrlChecked);
            });
        } else {
            // If zip is not selected, upload files individually
            for (let i = 0; i < files.length; i++) {
                uploadSingleFile(files[i], isShortlinkUrlChecked);
            }
        }
    }
    
    function uploadSingleFile(file, isShortlinkUrlChecked) {
    const progressBarsContainer = document.getElementById("progressBars");
    let progressBarContainer = document.createElement("div");
    progressBarContainer.classList.add("mb-3");
    
    let progressBarLabel = document.createElement("span");
    progressBarLabel.textContent = `Uploading ${file.name}...`;
    progressBarLabel.classList.add("d-block", "mb-2");
    
    let progressBar = document.createElement("div");
    progressBar.classList.add("progress");
    
    let progressBarFill = document.createElement("div");
    progressBarFill.classList.add("progress-bar", "progress-bar-striped", "progress-bar-animated");
    progressBarFill.setAttribute("role", "progressbar");
    progressBarFill.setAttribute("aria-valuenow", 0);
    progressBarFill.setAttribute("aria-valuemin", 0);
    progressBarFill.setAttribute("aria-valuemax", 100);
    progressBarFill.style.width = "0%";
    
    progressBar.appendChild(progressBarFill);
    progressBarContainer.appendChild(progressBarLabel);
    progressBarContainer.appendChild(progressBar);
    progressBarsContainer.appendChild(progressBarContainer);
    
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
        if (isShortlinkUrlChecked && offset === 0) {
            formData.append("shortlink", true);
        }
    
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload", true);
    
        xhr.onload = function () {
            if (xhr.status === 200) {
                offset += CHUNK_SIZE;
    
                // Update progress bar based on chunks uploaded
                let percent = ((offset / file.size) * 100).toFixed(2);
                progressBarFill.style.width = percent + "%";
                progressBarFill.setAttribute("aria-valuenow", percent);
    
                if (offset < file.size) {
                    uploadChunk(); // Continue uploading the next chunk
                } else {
                    progressBarLabel.textContent = `${file.name} uploaded successfully!`;
                    progressBarFill.classList.remove("progress-bar-animated");
                    progressBarFill.classList.add("bg-success");
                    progressBarFill.style.width = "100%";
                    progressBarFill.setAttribute("aria-valuenow", 100);
    
                    // Fetch the download link for the fully uploaded file
                    fetchDownloadLink(file.name, progressBarContainer);
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