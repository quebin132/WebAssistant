var socket = new WebSocket("ws://192.168.31.187:12500/ws");
              
            var respuesta,messageHolder;
            

            socket.onopen = function(e) {
                console.log("[open] Conexión establecida");
                socket.send(JSON.stringify("conexion desde javascript"));
            };
        
            socket.onmessage = function(event) {
                respuesta = event.data;
             
                let respuestita= document.getElementById("mensajes");
                let listaresp= document.createElement('li');
                listaresp.textContent= respuesta
                respuestita.appendChild(listaresp);
                listaresp.classList.add("respuestas")
                // console.log(event)
                console.log(respuesta);
                scrollBottom();
            };
            

        
            socket.onclose = function(event) {
                if (event.wasClean) {
                    console.log(`[close] Conexión cerrada limpiamente, código=${event.code} motivo=${event.reason}`);
                } else {
                    // Ejemplo: El servidor cierra la conexión o se pierde la conexión
                    console.log(`[close] Conexión cerrada abruptamente`);
                }
            };
        
            socket.onerror = function(error) {
                console.log(`[error] ${error.message}`);
            };

var input = document.getElementById("messageText");
// const chatinput= document.getElementById("inputchat");
// chatinput.addEventListener("input",function(event){
//     onSubmit();
// });
// const postOptions = {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({"pregunta":input.value}) // Convert the JavaScript object to a JSON string
//   };
// // POST A /PREGUNTAS/
// function sendMessage(event) {
//     event.preventDefault(); //IMPORTANTE PARA QUE FUNCIONE, HACE QUE NO SE RECARGUE LA PAGINA AL HACE SUBMIT
//     console.log(typeof(JSON.stringify({"pregunta":input.value})))
//     console.log(typeof({"pregunta":input.value}))    
//     console.log(JSON.stringify({"pregunta":input.value}))    
//     fetch('http://192.168.0.18:12500/preguntas/', postOptions)
//         .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
        
        
//         return response.json(); // Parse the JSON response
//         })
//         .then(data => {
//         console.log('Response received:', data);
//         })
//         .catch(error => {
//         console.error('There was a problem with the POST request:', error);
//         });
// }

function onSubmit(event) {
    event.preventDefault();
    if (input.value !=""){
        socket.send(JSON.stringify(input.value));
        console.log("mensaje enviado");
        let preguntita= document.getElementById("mensajes");
        let lista= document.createElement('li');
        lista.textContent= input.value
        preguntita.appendChild(lista);
        lista.classList.add("preguntas")
        scrollBottom();
        inputbar = document.getElementById("messageText");
        console.log(inputbar.value)
        inputbar.value = "";
    }
   
}

function scrollBottom(){
    var container = document.getElementById('chatBox');
    container.scrollTop = container.scrollHeight;
}
