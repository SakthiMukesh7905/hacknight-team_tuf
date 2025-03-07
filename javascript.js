function uploadVideo(exercise) {
    let input = document.getElementById("videoInput").files[0];
    let formData = new FormData();
    formData.append("video", input);

    fetch(`/${exercise}`, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("result").innerText = data.feedback;
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("result").innerText = "Failed to analyze video.";
    });
}
