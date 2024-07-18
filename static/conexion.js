var socket = new WebSocket("ws://192.168.31.239:12500/ws"); 
              // cambiar IP a la del pc grande
            var respuesta,messageHolder;
            

            socket.onopen = function(e) {
                console.log("[open] Conexión establecida");
                socket.send(JSON.stringify("conexion desde javascript"));
            };
        
            socket.onmessage = function(event) {
                respuesta = event.data;
                ISRESPONDING= false;
             
                chatbox.appendChild(createChatLi(respuesta,"respuestas"))
                // console.log(event)
                console.log(respuesta);
                scrollBottom();
                // speak(respuesta)
                
                
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
var botonsend= document.getElementById("send-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input input");
var ISRESPONDING= false;

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "preguntas" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; // return chat <li> element
}


// TEXT TO SPEECH
function speak(text) {
    // Get the text from the textarea

    // Create an instance of SpeechSynthesisUtterance
    var utterance = new SpeechSynthesisUtterance(text);

    // Set the language and voice properties
    utterance.lang = 'es-ES';  // Language and accent
    utterance.pitch = 1;       // Pitch (default is 1)
    utterance.rate = 1;        // Rate (default is 1)
    utterance.volume = 1;      // Volume (default is 1)

    // Use the speechSynthesis API to speak the text
    window.speechSynthesis.speak(utterance);
}
function onSubmit(event) {
    event.preventDefault();
    if (input.value !="" & !ISRESPONDING){
        socket.send(JSON.stringify(input.value));
        ISRESPONDING= true;
        console.log("mensaje enviado");
        userMessage=chatInput.value;
        
        chatbox.appendChild(createChatLi(userMessage, "preguntas"));
        scrollBottom();
        input.value = "";
        
    }
   
}

function scrollBottom(){
    var container = document.getElementById('BOX');
    container.scrollTop = container.scrollHeight;
}

botonsend.addEventListener("click",onSubmit);


document.addEventListener('DOMContentLoaded', function() {
    // Obtener el icono del menú y el menú desplegable
    const menuIcon = document.getElementById('menuIcon');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const container = document.getElementById('mainContainer');
    let TOGGLING= false;
    
  
    // Agregar un event listener para el clic en el icono del menú
    menuIcon.addEventListener('click', function() {

      
      // Alternar la visibilidad del menú desplegable al hacer clic en el icono
      if (!TOGGLING) {
        container.classList.toggle('move-left');
        dropdownMenu.classList.toggle('appear');
        TOGGLING=true;
      }
      setTimeout(() => {
        TOGGLING=false;
      }, 500);

    });
  
    
    
  });