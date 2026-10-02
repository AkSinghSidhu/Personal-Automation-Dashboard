const input = document.getElementById("pathInput")
const button = document.getElementById("inspectButton");
const result = document.getElementById("result");

button.addEventListener("click", function(){
    const path = input.value;

    fetch("/api/inspect?path=" + encodeURIComponent(path))
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                result.innerHTML = `<p style="color: red;">${data.error}</p>`;
            } else {
                result.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            }
        });
});
