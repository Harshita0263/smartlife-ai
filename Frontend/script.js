// ---------------- CHAT FUNCTION ----------------
async function sendMessage() {

    let inputBox = document.getElementById("user-input")
    if(!inputBox) return

    let input = inputBox.value.trim()

    if (!input) return

    let chatBox = document.getElementById("chat-box")

    if(chatBox){
        chatBox.innerHTML += `<div class="message user">You: ${input}</div>`
    }

    try {

        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: input })
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

    try {

        const res = await fetch("http://127.0.0.1:5000/insights")

        const data = await res.json()

        const insightElement = document.getElementById("insightText")

        if(insightElement){
            insightElement.innerText = data.insight
        }

    } catch (error) {

        console.log("Insight Error:", error)

        const insightElement = document.getElementById("insightText")

        if(insightElement){
            insightElement.innerText = "Unable to load insights"
        }
    }

}


// ---------------- LOAD EXPENSE CHART ----------------
let chartInstance = null

async function loadChart(){

    const chartCanvas = document.getElementById("expenseChart")

    if(!chartCanvas) return

    try{

        const res = await fetch("http://127.0.0.1:5000/expenses")

        const data = await res.json()

        const categoryTotals = {}

        data.forEach(exp => {

            const cat = exp.category

            categoryTotals[cat] = (categoryTotals[cat] || 0) + Number(exp.amount)

        })

        const labels = Object.keys(categoryTotals)
        const values = Object.values(categoryTotals)

        // Destroy previous chart
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

    try{

        const res = await fetch("http://127.0.0.1:5000/prediction")

        const data = await res.json()

        const predictionElement = document.getElementById("predictionText")

        if(predictionElement){
            predictionElement.innerText = data.prediction
        }

    }catch(error){

        console.log("Prediction Error:", error)

        const predictionElement = document.getElementById("predictionText")

        if(predictionElement){
            predictionElement.innerText = "Unable to generate prediction"
        }

    }

}


// ---------------- PAGE LOAD ----------------
window.onload = function(){

    loadInsights()

    loadChart()

    loadPrediction()

}
function scrollToSection(sectionId){

    const section = document.getElementById(sectionId)

    if(section){
        section.scrollIntoView({
            behavior:"smooth"
        })
    }

}