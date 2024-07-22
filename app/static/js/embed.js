(function () {
    window.onload = function () {
        const chatbotUrl = "https://chatbot.saaheerpurav.com";
        //const chatbotUrl = "http://127.0.0.1:5000";

        const chatbotScript = document.querySelector(`script[src="${chatbotUrl}/embed"]`);
        let botId = chatbotScript.getAttribute("bot-id");
        let bubbleColor = chatbotScript.getAttribute("bubble-color");
        let showAlert = chatbotScript.getAttribute("show-alert") === "true";

        if (botId === null || botId.trim() === "") botId = "null";
        if (bubbleColor === null || bubbleColor.trim() === "") bubbleColor = "#007aff";


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

            #iframe-container {
                position: fixed; 
                right: 0; 
                bottom: 0;
                display: none;
                z-index:999;
            }
            #iframe {
                height: 100vh;
                width: 100vw;
                border: none;
            }

            #chatbot-alert-message {
                font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
                font-size: 18px;
                display: flex; 
                position: absolute; 
                padding-top: 0.5rem;
                padding-bottom: 0.5rem; 
                padding-left: 1rem;
                padding-right: 0.5rem; 
                flex-direction: row; 
                align-items: center; 
                border-radius: 0.5rem; 
                color: #ffffff; 
                white-space: nowrap; 
                bottom: 4.5rem;
                right: 1.5rem;
                background: ${bubbleColor};
            }
            #chatbot-alert-bottom {
                border: 0 solid ${bubbleColor};
                margin: 0;
                padding: 0;
                position: absolute;
                bottom: -15px;
                right: 0;
                z-index: 999;
                height: 0;
                width: 0;
                border-radius: .25rem;
                border-width: 25px;
                border-bottom-width: 0;
                border-left-width: 25px;
                border-right-width: 0;
                border-color: transparent;
                border-top-color: ${bubbleColor};
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

        const chatbotSvgPath = `
            <path d="M18 4a3 3 0 0 1 3 3v8a3 3 0 0 1 -3 3h-5l-5 3v-3h-2a3 3 0 0 1 -3 -3v-8a3 3 0 0 1 3 -3h12z"></path>
            <path d="M9.5 9h.01"></path>
            <path d="M14.5 9h.01"></path>
            <path d="M9.5 13a3.5 3.5 0 0 0 5 0"></path>
        `;

        document.body.appendChild(chatbotContainer);
        var windowVis = false;

        // Show bubble function
        window.showBubble = function () {
            document.getElementById("button-container").innerHTML += `
                ${showAlert
                    ? `
                        <div id="chatbot-alert-message" role="alert">
                            <div id="chatbot-alert-bottom"></div>
                            <p style="margin: 0; margin-right: 0.5rem; margin-bottom: 0.1rem;">Have any questions?</p>

                            <button style="background-color: ${bubbleColor}; border: none; display: flex; justify-content: center; align-items: center; cursor: pointer;" onClick="hideAlert()">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
                                    <path fill="white" d="M2.39705176,2.55378835 L2.46966991,2.46966991 C2.73593648,2.20340335 3.15260016,2.1791973 3.44621165,2.39705176 L3.53033009,2.46966991 L8,6.939 L12.4696699,2.46966991 C12.7625631,2.1767767 13.2374369,2.1767767 13.5303301,2.46966991 C13.8232233,2.76256313 13.8232233,3.23743687 13.5303301,3.53033009 L9.061,8 L13.5303301,12.4696699 C13.7965966,12.7359365 13.8208027,13.1526002 13.6029482,13.4462117 L13.5303301,13.5303301 C13.2640635,13.7965966 12.8473998,13.8208027 12.5537883,13.6029482 L12.4696699,13.5303301 L8,9.061 L3.53033009,13.5303301 C3.23743687,13.8232233 2.76256313,13.8232233 2.46966991,13.5303301 C2.1767767,13.2374369 2.1767767,12.7625631 2.46966991,12.4696699 L6.939,8 L2.46966991,3.53033009 C2.20340335,3.26406352 2.1791973,2.84739984 2.39705176,2.55378835 L2.46966991,2.46966991 L2.39705176,2.55378835 Z">
                                    </path>
                                </svg>
                            </button>
                        </div>
                    `
                    : ""
                }
                
                <button id="chatbot-button" class="chatbot-bubble" onclick="toggleIframe()">
                    <svg id="chatbot-icon-svg" fill="${bubbleColor}" stroke="white" height="2em" width="2em" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" color="white" xmlns="http://www.w3.org/2000/svg" style="color: white;">
                        ${chatbotSvgPath}
                    </svg>
                </button>
            `
        }

        window.hideAlert = function () {
            let alertMsg = document.getElementById("chatbot-alert-message");
            if (alertMsg !== null) alertMsg.remove();

        }

        // Toggle iframe function
        window.toggleIframe = function () {
            windowVis = !windowVis;
            if (showAlert) hideAlert();
            document.getElementById("iframe-container").style.display = windowVis ? "block" : "none";

            if (windowVis) {
                document.getElementById("chatbot-icon-svg").innerHTML = `
                    <path d="M6 9l6 6 6-6"></path>
                `;
            } else {
                document.getElementById("chatbot-icon-svg").innerHTML = chatbotSvgPath;
            }
        }

        window.addEventListener("message", function (e) {
            if (e.data === "iframe_close") {
                toggleIframe();
            }
        });
    }
})();