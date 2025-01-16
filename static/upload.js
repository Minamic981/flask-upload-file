// Upload Files Function
// Function to fetch the download link and display it
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
                // Display the download link
                const downloadLink = document.createElement("a");
                downloadLink.textContent = "Link";
                downloadLink.href = data.link;
                downloadLink.classList.add("d-block", "mt-2", "text-success");
                downloadLink.target = "_blank"; // Open in a new tab

                // Append the download link to the progress bar container
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

    for (let i = 0; i < files.length; i++) {
        let file = files[i];

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

        let formData = new FormData();
        formData.append("files", file);

        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/upload", true);

        xhr.upload.addEventListener("progress", function (e) {
            if (e.lengthComputable) {
                let percent = (e.loaded / e.total) * 100;
                progressBarFill.style.width = percent + "%";
                progressBarFill.setAttribute("aria-valuenow", percent);
            }
        });

        xhr.onload = function () {
            if (xhr.status === 200) {
                progressBarLabel.textContent = `${file.name} uploaded successfully!`;
                progressBarFill.classList.remove("progress-bar-animated");
                progressBarFill.classList.add("bg-success");
                progressBarFill.style.width = "100%";
                progressBarFill.setAttribute("aria-valuenow", 100);
        
                // Automatically fetch the download link
                fetchDownloadLink(file.name, progressBarContainer);
            } else {
                progressBarLabel.textContent = `Error uploading ${file.name}`;
            }
        };

        xhr.send(formData);
    }
}