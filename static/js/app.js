// Using $ as a shorthand for document.getElementById()
const $ = (id) => document.getElementById(id);

// This function handles fetch requests
async function handleFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Fetch Error =\n`, error);
        alert(`Failed to perform operation. Error: ${error.message}`);
    }
}

// This function handles visibility toggling
function toggleVisibility(id, isVisible) {
    $(id).style.display = isVisible ? 'block' : 'none';
}

// This function checks the authentication status
async function checkAuth() {
    const data = await handleFetch('/check_auth');
    if (!data || !data.authenticated) {
        console.log('User is not authenticated');
        toggleVisibility('googleAuthBtn', true);
    } else {
        toggleVisibility('formContainer', true);
        toggleVisibility('logoutBtn', true);
        toggleVisibility('googleAuthBtn', false);
        getCalendars();
    }
}

// This function fetches calendar data
async function getCalendars() {
    const calendars = await handleFetch('/calendars');
    const calendarSelect = $('calendarSelect');
    calendars.forEach((calendar) => {
        const option = document.createElement('option');
        option.value = calendar.id;
        option.textContent = calendar.summary;
        calendarSelect.appendChild(option);
    });
}

// This function creates an event
async function createEvent(eventText, calendarId) {
    await handleFetch('/create_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ eventText, calendarId }),
    });
}

// Listeners for the buttons
$('googleAuthBtn').addEventListener('click', async () => {
    const data = await handleFetch('/auth');
    if (data) window.location.href = data.authUrl;
});

$('submitEvent').addEventListener('click', () => {
    const eventText = $('eventText').value;
    const calendarId = $('calendarSelect').value;
    createEvent(eventText, calendarId);
});

$('logoutBtn').addEventListener('click', async () => {
    const data = await handleFetch('/logout');
    if (data) {
        toggleVisibility('formContainer', false);
        toggleVisibility('logoutBtn', false);
        toggleVisibility('googleAuthBtn', true);
        $('eventText').value = '';
        $('calendarSelect').innerHTML = '';
        checkAuth();
    }
});

// Check authentication status on load
checkAuth();