document.addEventListener("DOMContentLoaded", function () {
  function toggleMode(mode) {
    if (mode === "live") {
      document.getElementById("liveFeed").src = "/live_feed";
      document.getElementById("liveSection").style.display = "block";
      document.getElementById("uploadSection").style.display = "none";
    } else {
      fetch("/stop_live", { method: "POST" }).then(() => {
        document.getElementById("liveFeed").src = "";
        document.getElementById("liveSection").style.display = "none";
        document.getElementById("uploadSection").style.display = "block";
      });
    }
  }

  function uploadVideo(workoutType) {
    let fileInput = document.getElementById("videoUpload").files[0];
    let formData = new FormData();
    formData.append("video", fileInput);

    fetch(`/upload_${workoutType}`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.video_path) {
          document.getElementById("videoFeed").src = `/video_${workoutType}`;
          document.getElementById("videoFeed").style.display = "block";
        }
        document.getElementById("feedback").innerText = data.feedback;
      });
  }

  function storeWorkout(workoutName) {
    let reps = 10;
    let duration = 30;

    fetch("/store_workout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        workout_name: workoutName,
        reps: reps,
        duration: duration,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message);
        window.location.href = "/";
      })
      .catch((error) => console.error("Error:", error));
  }

  window.toggleMode = toggleMode;
  window.uploadVideo = uploadVideo;
  window.storeWorkout = storeWorkout;
});
