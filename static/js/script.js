function close_alert() {
    document.getElementById("alert").classList.add("hidden");
}
const bar = document.querySelector(".indeterminate-progress-bar__progress")

function active_bar() {
    bar.classList.add("actived");
}

function finish_bar() {
    bar.classList.remove("actived");
    bar.classList.add("finished");
}
