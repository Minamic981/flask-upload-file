// Function to switch between Upload and Shortlink pages
document.getElementById("uploadBtn").addEventListener("click", function () {
    document.getElementById("uploadPage").classList.remove("hidden");
    document.getElementById("shortlinkPage").classList.add("hidden");
});

document.getElementById("shortlinkBtn").addEventListener("click", function () {
    document.getElementById("uploadPage").classList.add("hidden");
    document.getElementById("shortlinkPage").classList.remove("hidden");
});

// Upload Files Function
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
            } else {
                progressBarLabel.textContent = `Error uploading ${file.name}`;
            }
        };

        xhr.send(formData);
    }
}

let lastCheckedShortname = {
    value: "",
    exists: false,
};

let lastCheckedUrl = {
    value: "",
    isValid: false,
};

function checkurlformat() {
    const urlinput = document.getElementById("urlInput");
    const urlError = document.getElementById("urlError");
    const url = urlinput.value.trim();

    if (url === "") {
        lastCheckedUrl.value = "";
        lastCheckedUrl.isValid = false;
        urlError.style.display = "none";
        return;
    }

    if (url === lastCheckedUrl.value) {
        urlError.style.display = lastCheckedUrl.isValid ? "none" : "block";
        return;
    }

    const urlRegex = /^(https?:\/\/)?([a-zA-Z0-9.-]+)(:[0-9]+)?(\/[a-zA-Z0-9_.~!$&'()*+,;=:@%/-]*)*(\/[a-zA-Z0-9_.~!$&'()*+,;=:@%/-]*::[a-zA-Z0-9_.~!$&'()*+,;=:@%/-]*)?(\?[a-zA-Z0-9_.~!$&'()*+,;=:@%/?-]*)?(#[a-zA-Z0-9_.~!$&'()*+,;=:@%/?-]*)?$/;
    const isValidUrl = urlRegex.test(url);

    lastCheckedUrl.value = url;
    lastCheckedUrl.isValid = isValidUrl;

    urlError.style.display = isValidUrl ? "none" : "block";
}

document.getElementById("urlInput").addEventListener("blur", checkurlformat);

function checkShortname() {
    const shortnameInput = document.getElementById("shortnameInput");
    const shortnameError = document.getElementById("shortnameError");
    const createButton = document.querySelector("#shortlinkPage button");

    const currentShortname = shortnameInput.value;

    if (currentShortname.length >= 4) {
        if (currentShortname === lastCheckedShortname.value) {
            if (lastCheckedShortname.exists) {
                shortnameError.style.display = "block";
                createButton.disabled = true;
            } else {
                shortnameError.style.display = "none";
                createButton.disabled = false;
            }
            return;
        }

        const xhr = new XMLHttpRequest();
        xhr.open("GET", `/checkshort?shortname=${encodeURIComponent(currentShortname)}`, true);
        xhr.setRequestHeader("Accept", "application/json");

        xhr.onload = function () {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);

                lastCheckedShortname.value = currentShortname;
                lastCheckedShortname.exists = response.check;

                if (response.check) {
                    shortnameError.style.display = "block";
                    createButton.disabled = true;
                } else {
                    shortnameError.style.display = "none";
                    createButton.disabled = false;
                }
            } else {
                console.error("Error checking shortname:", xhr.statusText);
            }
        };

        xhr.onerror = function () {
            console.error("Network error while checking shortname.");
        };

        xhr.send();
    } else {
        shortnameError.style.display = "none";
        createButton.disabled = false;

        lastCheckedShortname.value = "";
        lastCheckedShortname.exists = false;
    }
}

document.getElementById("shortnameInput").addEventListener("blur", checkShortname);

function createShortlink() {
    const url = document.getElementById("urlInput").value;
    const shortname = document.getElementById("shortnameInput").value;

    if (!url) {
        alert("Please enter a valid URL.");
        return;
    }

    const payload = {
        url: url,
        shortname: shortname,
    };

    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/shortlink", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
        let response;
        try {
            response = JSON.parse(xhr.responseText);
        } catch (error) {
            alert("An error occurred while processing the response.");
            return;
        }

        if (xhr.status === 200) {
            const shortlinkContainer = document.getElementById("shortlinkContainer");
            shortlinkContainer.innerHTML = "";

            const shortlinkElement = document.createElement("a");
            shortlinkElement.href = response.shortlink;
            shortlinkElement.textContent = response.shortlink;
            shortlinkElement.classList.add("fade-in-link");
            shortlinkElement.target = "_blank";

            shortlinkContainer.appendChild(shortlinkElement);

            setTimeout(() => {
                shortlinkElement.classList.add("show");
            }, 10);
        } else {
            if (response.error) {
                alert(response.error);
            } else {
                alert("An unexpected error occurred.");
            }
        }
    };

    xhr.onerror = function () {
        alert("An error occurred while creating the shortlink. Please check your connection and try again.");
    };

    xhr.send(JSON.stringify(payload));
}