(function () {
    window.onload = function () {
        const chatbotUrl = "https://chatbot.saaheerpurav.com";
        //const chatbotUrl = "http://127.0.0.1:5000";

        const chatbotScript = document.querySelector(`script[src="${chatbotUrl}/embed"]`);
        let botId = chatbotScript.getAttribute("bot-id");
        let bubbleColor = chatbotScript.getAttribute("bubble-color");

        if(botId === null || botId.trim() === "") botId = "null";
        if(bubbleColor === null || bubbleColor.trim() === "") bubbleColor = "#007aff";


        // Create styles
        const style = document.createElement('style');
        style.innerHTML = `
            .chatbot-bubble {
                display: flex; 
                justify-content: center; 
                align-items: center; 
                border-radius: 9999px;
                border: none;
                transition-property: all;
                transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
                transition-duration: 300ms; 
                background: ${bubbleColor};
                width: 3rem;
                height: 3rem;
                cursor: pointer;
                outline: none;
                box-shadow: 0 3px 10px rgb(0,0,0,0.2);
            }
            .chatbot-bubble:hover {
                scale: 1.15;
            }
            .chatbot-bubble:active {
                scale: 1.05;
            }

            #iframe-container{
                position: fixed; 
                right: 0; 
                bottom: 0;
                display: none;
                z-index:999;
            }
            #iframe{
                height: 100vh;
                width: 100vw;
                border: none;
            }

            @media (min-width: 768px) {
                #iframe-container {
                    right: 1.25rem; 
                    bottom: 88px;
                }
                    
                #iframe {
                    width: 24rem; 
                    height: 60vh;
                }
            }
        `;

        document.head.appendChild(style);

        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'chatbot-container';

        chatbotContainer.innerHTML = `
            <div id="iframe-container">
                <iframe id="iframe" src="${chatbotUrl}/chatbot/iframe?id=${botId}" onload="showBubble()"></iframe>
            </div>

            <div id="button-container" style="position: fixed; right: 20px; bottom: 20px; z-index:99">
            </div>
        `;

        document.body.appendChild(chatbotContainer);
        var windowVis = false;

        // Show bubble function
        window.showBubble = function () {
            document.getElementById("button-container").innerHTML += `
                
                    <button id="chatbot-button" class="chatbot-bubble" onclick="toggleIframe()">
    
                        <svg id="chatbot-icon-svg" xmlns="http://www.w3.org/2000/svg" fill="${bubbleColor}" stroke="white" height="2em" width="2em"
                        stroke-linecap="round" stroke-linejoin="round" stroke-width=2 viewBox="0 0 24 24">
                            <path stroke="none" d="M0 0h24v24H0z"></path>
                            <path d="M4 21V8a3 3 0 013-3h10a3 3 0 013 3v6a3 3 0 01-3 3H8l-4 4M9.5 9h.01M14.5 9h.01M9.5 13a3.5 3.5 0 005 0"></path>
                        </svg>
                    </button>
            `
        }

        // Toggle iframe function
        window.toggleIframe = function () {
            windowVis = !windowVis;
            document.getElementById("iframe-container").style.display = windowVis ? "block" : "none";

            if (windowVis) {
                document.getElementById("chatbot-icon-svg").innerHTML = `
                    <path d="M6 9l6 6 6-6"></path>
                `;
            } else {
                document.getElementById("chatbot-icon-svg").innerHTML = `
                    <path stroke="none" d="M0 0h24v24H0z"></path>
                    <path d="M4 21V8a3 3 0 013-3h10a3 3 0 013 3v6a3 3 0 01-3 3H8l-4 4M9.5 9h.01M14.5 9h.01M9.5 13a3.5 3.5 0 005 0"></path>
                `;
            }
        }

        window.addEventListener("message", function (e) {
            if (e.data === "iframe_close") {
                toggleIframe();
            }
        });
    }
})();