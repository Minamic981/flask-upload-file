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

    // Trim whitespace from the input value
    const currentShortname = shortnameInput.value.trim();

    // Check if the shortname is empty or contains only whitespace
    if (!currentShortname) {
        shortnameError.textContent = "Shortname cannot be empty or contain only whitespace.";
        shortnameError.style.display = "block";
        createButton.disabled = true;
        return; // Exit the function early
    }

    // Check if the shortname contains any whitespace
    if (/\s/.test(currentShortname)) {
        shortnameError.textContent = "Shortname cannot contain spaces or whitespace.";
        shortnameError.style.display = "block";
        createButton.disabled = true;
        return; // Exit the function early
    }

    // Only proceed if the shortname is at least 1 character long and has no whitespace
    if (currentShortname.length >= 1) {
        if (currentShortname === lastCheckedShortname.value) {
            if (lastCheckedShortname.exists) {
                shortnameError.textContent = "Shortname already exists!";
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
                    shortnameError.textContent = "Shortname already exists!";
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