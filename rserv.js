async function rserv(d, code, nocors = false) {
  var data = new FormData();

  data.set("data", d);
  data.set("code", code);
  return fetch("http://127.0.0.1:8080/r", {
    method: "POST",
    mode: nocors ? "no-cors" : "cors",
    headers: {
      Accept: "text/plain",
    },
    body: data,
  })
    .then((response) => response.text())
    .then((result) => {
      console.log("Success:", result);
      //out.innerHTML = result;
      return result;
    })
    .catch((error) => {
      console.error("Error:", error);
      //out.innerHTML = 'Error: ' + error;
      return false
    });
}
