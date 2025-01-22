let lastChecked = {
    url: {
        value: "",
        isValid: false,
    },
    shortname: {
        value: "",
        exists: false,
    },
};

function checkUrlFormat() {
    const urlinput = document.getElementById("urlInput");
    const urlError = document.getElementById("urlError");
    const createButton = document.querySelector("#shortlinkPage button");
    let url = urlinput.value.trim();  // Automatically trim whitespace and newlines

    // Reset for empty input
    if (url === "") {
        resetUrlCheck();
        createButton.disabled = true; // Disable button when URL is empty
        return;
    }

    // If URL is unchanged from last check, update error state
    if (url === lastChecked.url.value) {
        urlError.style.display = lastChecked.url.isValid ? "none" : "block";
        createButton.disabled = !lastChecked.url.isValid; // Disable button if URL is invalid
        return;
    }

    // If URL starts with "test-", skip protocol check and allow submission
    let modifiedUrl = url;
    if (url.startsWith("test-")) {
        modifiedUrl = url.slice(5); // Remove the "test-" prefix
        lastChecked.url.value = modifiedUrl;
        lastChecked.url.isValid = true;
        urlError.style.display = "none";
        createButton.disabled = false; // Enable button if it's test URL
        return;  // Skip further checks for test- URLs
    }

    // Check if the URL has a protocol (http:// or https://)
    const hasProtocol = /^https?:\/\//i.test(url);
    if (!hasProtocol) {
        displayUrlError("Error: URL must include a protocol (http:// or https://).");
        createButton.disabled = true; // Disable button if protocol is missing
        return;
    }

    // Validate the URL format after removing the "test-" prefix (if any)
    const validation = validateUrl(modifiedUrl);
    if (!validation.isValid) {
        displayUrlError(validation.message);
        createButton.disabled = true; // Disable button if URL is invalid
        return;
    }

    // If validation passes, update lastChecked
    lastChecked.url.value = modifiedUrl;
    lastChecked.url.isValid = true;
    urlError.style.display = "none";
    createButton.disabled = false; // Enable button if URL is valid
}

function validateUrl(url) {
    const urlRegex = /^(https?:\/\/)?([a-zA-Z0-9.-]+)(:[0-9]+)?(\/[a-zA-Z0-9_.~!$&'()*+,;=:@%/-]*)*(\/[a-zA-Z0-9_.~!$&'()*+,;=:@%/-]*::[a-zA-Z0-9_.~!$&'()*+,;=:@%/-]*)?(\?[a-zA-Z0-9_.~!$&'()*+,;=:@%/?-]*)?(#[a-zA-Z0-9_.~!$&'()*+,;=:@%/?-]*)?$/;
    if (urlRegex.test(url)) {
        return { isValid: true, message: "" };
    }
    return { isValid: false, message: "Error: Invalid URL format." };
}

function displayUrlError(message) {
    const urlError = document.getElementById("urlError");
    urlError.textContent = message;
    urlError.style.display = "block";
}

function resetUrlCheck() {
    const urlError = document.getElementById("urlError");
    urlError.style.display = "none";
    lastChecked.url.value = "";
    lastChecked.url.isValid = false;
}

function checkShortname() {
    const shortnameInput = document.getElementById("shortnameInput");
    const shortnameError = document.getElementById("shortnameError");
    const createButton = document.querySelector("#shortlinkPage button");
    let currentShortname = shortnameInput.value.trim();  // Automatically trim whitespace and newlines

    // Shortname is optional, but if provided, ensure it does not contain spaces in the middle
    if (currentShortname && /\s/.test(currentShortname)) {
        shortnameError.textContent = "Shortname cannot contain spaces.";
        shortnameError.style.display = "block";
        createButton.disabled = true; // Disable button if there are spaces
        return;
    }

    // Handle shortname checks for existence (only if the shortname is not empty)
    if (currentShortname.length > 0) {
        if (currentShortname === lastChecked.shortname.value) {
            if (lastChecked.shortname.exists) {
                shortnameError.textContent = "Shortname already exists!";
                shortnameError.style.display = "block";
                createButton.disabled = true; // Disable button if shortname exists
            } else {
                shortnameError.style.display = "none";
                createButton.disabled = false; // Enable button if shortname is valid
            }
            return;
        }

        checkShortnameExistence(currentShortname, shortnameError, createButton);
    } else {
        resetShortnameCheck(shortnameError, createButton);
    }
}

function checkShortnameExistence(shortname, shortnameError, createButton) {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", `/checkshort?shortname=${encodeURIComponent(shortname)}`, true);
    xhr.setRequestHeader("Accept", "application/json");

    xhr.onload = function () {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            lastChecked.shortname.value = shortname;
            lastChecked.shortname.exists = response.check;

            if (response.check) {
                shortnameError.textContent = "Shortname already exists!";
                shortnameError.style.display = "block";
                createButton.disabled = true; // Disable button if shortname exists
            } else {
                shortnameError.style.display = "none";
                createButton.disabled = false; // Enable button if shortname is valid
            }
        } else {
            console.error("Error checking shortname:", xhr.statusText);
            createButton.disabled = true; // Disable button on error
        }
    };

    xhr.onerror = function () {
        console.error("Network error while checking shortname.");
        createButton.disabled = true; // Disable button on network error
    };

    xhr.send();
}

function resetShortnameCheck(shortnameError, createButton) {
    shortnameError.style.display = "none";
    createButton.disabled = false; // Enable button if no shortname
    lastChecked.shortname.value = "";
    lastChecked.shortname.exists = false;
}

document.getElementById("urlInput").addEventListener("blur", checkUrlFormat);
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