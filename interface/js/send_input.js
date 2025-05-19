

document.getElementById("athleteForm").addEventListener("submit", function (e) {
    e.preventDefault();

    // Collect form data
    const formData = new FormData(e.target);
    const data = {};

    // Get regular input fields
    for (const input of document.querySelectorAll(
        'input:not([type="checkbox"])'
    )) {
        data[input.id] = input.value;
    }

    // Get select fields
    for (const select of document.querySelectorAll("select")) {
        data[select.id] = select.value;
    }

    // Get checkbox groups
    const injuries = [
        ...document.querySelectorAll('input[name="injuries"]:checked'),
    ].map((el) => el.value);
    const equipment = [
        ...document.querySelectorAll('input[name="equipment"]:checked'),
    ].map((el) => el.value);
    const focus = [
        ...document.querySelectorAll('input[name="focus"]:checked'),
    ].map((el) => el.value);

    data.injuries = injuries;
    data.equipment = equipment;
    data.focus = focus;

    // Store in localStorage for the results page
    localStorage.setItem("athleteData", JSON.stringify(data));

    console.log(data);

    fetch("backend/BFS.py", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(() => {
        window.location.href = "results.html";  // Backend stores result in session
    });

    // Redirect to results page

});