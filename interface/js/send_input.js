// const name = document.getElementById('name');
// const age = document.getElementById('age');
// const height = document.getElementById('height');
// const weight = document.getElementById('weight');
// const position = document.getElementById('position');
// const fitness = document.getElementById('fitness').value;
// const strength = document.getElementById('strength').value;
// const speed = document.getElementById('speed').value;
// const endurance = document.getElementById('endurance').value;
// const injuries = document.getElementById('injuries').value;
// const sleep = document.getElementById('sleep');
// const nutrition = document.getElementById('nutrition').value;
// const stress = document.getElementById('stress').value;


// const button = document.getElementById('button');


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

    // Redirect to results page
    // window.location.href = "results.html";
});