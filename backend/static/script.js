// ---------------- GET USERNAME ----------------
let username = localStorage.getItem("username")

if(!username){
    username = prompt("Enter your name")
    localStorage.setItem("username", username)
}


// ---------------- CHAT FUNCTION ----------------
async function sendMessage() {

    const inputBox = document.getElementById("user-input")
    if(!inputBox) return

    const input = inputBox.value.trim()
    if(!input) return

    const chatBox = document.getElementById("chat-box")

    if(chatBox){
        chatBox.innerHTML += `<div class="message user">${username}: ${input}</div>`
    }

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: input,
                username: username
            })
        })

        const data = await response.json()

        if(chatBox){
            chatBox.innerHTML += `<div class="message ai">AI: ${data.reply}</div>`
            chatBox.scrollTop = chatBox.scrollHeight
        }

    } catch (error) {

        console.log("Chat Error:", error)

        if(chatBox){
            chatBox.innerHTML += `<div class="message ai">Server connection error</div>`
        }
    }

    inputBox.value = ""
}


// ---------------- LOAD AI INSIGHTS ----------------
async function loadInsights(){

    const insightElement = document.getElementById("insightText")
    if(!insightElement) return

    try {

        const res = await fetch("/insights?username=" + username)
        const data = await res.json()

        insightElement.innerText = data.insight

    } catch (error) {

        console.log("Insight Error:", error)
        insightElement.innerText = "Unable to load insights"
    }

}


// ---------------- LOAD EXPENSE CHART ----------------
let chartInstance = null

async function loadChart(){

    const chartCanvas = document.getElementById("expenseChart")
    if(!chartCanvas) return

    try{

        const res = await fetch("/expenses?username=" + username)
        const data = await res.json()

        const categoryTotals = {}

        data.forEach(exp => {
            const cat = exp.category
            categoryTotals[cat] = (categoryTotals[cat] || 0) + Number(exp.amount)
        })

        const labels = Object.keys(categoryTotals)
        const values = Object.values(categoryTotals)

        if(chartInstance){
            chartInstance.destroy()
        }

        chartInstance = new Chart(chartCanvas, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [{
                    data: values
                }]
            }
        })

    }catch(error){

        console.log("Chart Error:", error)

    }

}


// ---------------- LOAD AI EXPENSE PREDICTION ----------------
async function loadPrediction(){

    const predictionElement = document.getElementById("predictionText")
    if(!predictionElement) return

    try{

        const res = await fetch("/prediction?username=" + username)
        const data = await res.json()

        predictionElement.innerText = data.prediction

    }catch(error){

        console.log("Prediction Error:", error)
        predictionElement.innerText = "Unable to generate prediction"

    }

}


// ---------------- PAGE LOAD ----------------
window.onload = function(){
    loadUser()
    loadInsights()
    loadChart()
    loadPrediction()

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

// ---------------- LOAD CURRENT USER ----------------
async function loadUser(){

    try{

        const res = await fetch("/current-user")
        const data = await res.json()

        if(data.user){

            const el = document.getElementById("welcomeUser")

            if(el){
                el.innerText = "Welcome, " + data.user
            }

        }

    }catch(error){

        console.log("User load error:", error)

    }

}


// ---------------- LOGOUT ----------------
async function logout(){

    await fetch("/logout")

    window.location.href = "/"

}