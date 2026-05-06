// ---------------- USER VARIABLE ----------------
let username = "User"


// ---------------- LOAD CURRENT USER ----------------
async function loadUser(){

    try{

        const res = await fetch("/session-user")
        const data = await res.json()

        if(data.user && data.user !== "Guest"){

            username = data.user

            const el = document.getElementById("usernameDisplay")

            if(el){
                el.innerText = username
            }

        }else{

            // if session expired redirect to login
            window.location.href = "/"

        }

    }catch(error){

        console.log("User load error:", error)

    }

}


// ---------------- CHAT FUNCTION ----------------
async function sendMessage(){

    const inputBox = document.getElementById("user-input")
    if(!inputBox) return

    const input = inputBox.value.trim()
    if(!input) return

    const chatBox = document.getElementById("chat-box")

    // show user message
    if(chatBox){
        chatBox.innerHTML += `
        <div class="message user">
            ${username}: ${input}
        </div>`
    }

    inputBox.value = ""

    try{

        const response = await fetch("/chat",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                message:input
            })
        })

        const data = await response.json()

        const reply = data.reply || "AI could not respond."

        if(chatBox){

            chatBox.innerHTML += `
            <div class="message ai">
                AI: ${reply}
            </div>`

            chatBox.scrollTop = chatBox.scrollHeight

        }

    }catch(error){

        console.log("Chat Error:",error)

        if(chatBox){
            chatBox.innerHTML += `
            <div class="message ai">
                Server connection error
            </div>`
        }

    }

}


// ---------------- LOAD AI INSIGHTS ----------------
async function loadInsights(){

    const insightElement = document.getElementById("insightText")
    if(!insightElement) return

    try{

        const res = await fetch("/insights")
        const data = await res.json()

        insightElement.innerText = data.insight || "No insights available."

    }catch(error){

        console.log("Insight Error:",error)
        insightElement.innerText = "Unable to load insights"

    }

}


// ---------------- LOAD EXPENSE CHART ----------------
let chartInstance = null

async function loadChart(){

    const chartCanvas = document.getElementById("expenseChart")
    if(!chartCanvas) return

    try{

        const res = await fetch("/expenses")
        const data = await res.json()

        const categoryTotals = {}

        data.forEach(exp=>{

            const cat = exp.category
            categoryTotals[cat] = (categoryTotals[cat] || 0) + Number(exp.amount)

        })

        const labels = Object.keys(categoryTotals)
        const values = Object.values(categoryTotals)

        if(chartInstance){
            chartInstance.destroy()
        }

        chartInstance = new Chart(chartCanvas,{
            type:"pie",
            data:{
                labels:labels,
                datasets:[{
                    data:values
                }]
            }
        })

    }catch(error){

        console.log("Chart Error:",error)

    }

}


// ---------------- LOAD AI EXPENSE PREDICTION ----------------
async function loadPrediction(){

    const predictionElement = document.getElementById("predictionText")
    if(!predictionElement) return

    try{

        const res = await fetch("/prediction")
        const data = await res.json()

        predictionElement.innerText = data.prediction || "No prediction available."

    }catch(error){

        console.log("Prediction Error:",error)

        predictionElement.innerText = "Unable to generate prediction"

    }

}


// ---------------- SIDEBAR SCROLL ----------------
function scrollToSection(sectionId){

    const section = document.getElementById(sectionId)

    if(section){

        section.scrollIntoView({
            behavior:"smooth"
        })

    }

}


// ---------------- LOGOUT ----------------
async function logout(){

    try{

        await fetch("/logout")

        window.location.href="/"

    }catch(error){

        console.log("Logout Error:",error)

    }

}


// ---------------- PAGE LOAD ----------------
window.addEventListener("load", function(){

    loadUser()
    loadInsights()
    loadChart()
    loadPrediction()

})