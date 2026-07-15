// ==========================================================
// Student Performance Prediction Dashboard
// main.js
// ==========================================================

// =========================
// DOM Ready
// =========================

document.addEventListener("DOMContentLoaded", () => {

    initNavbar();

    initScrollTop();

    initLoading();

    initRevealAnimation();

    initPredictionForm();

});

// =========================
// Navbar Scroll Effect
// =========================

function initNavbar(){

    const navbar = document.querySelector(".navbar");

    if(!navbar) return;

    window.addEventListener("scroll", () => {

        if(window.scrollY > 40){

            navbar.classList.add("scrolled");

        }

        else{

            navbar.classList.remove("scrolled");

        }

    });

}

// =========================
// Scroll To Top
// =========================

function initScrollTop(){

    const btn = document.getElementById("scrollTopBtn");

    if(!btn) return;

    window.addEventListener("scroll",()=>{

        if(window.scrollY > 400){

            btn.style.display="block";

        }

        else{

            btn.style.display="none";

        }

    });

    btn.addEventListener("click",()=>{

        window.scrollTo({

            top:0,

            behavior:"smooth"

        });

    });

}

// =========================
// Loading Screen
// =========================

function initLoading(){

    const loader=document.getElementById("loading");

    if(!loader) return;

    window.addEventListener("load",()=>{

        loader.style.display="none";

    });

}

// =========================
// Reveal Animation
// =========================

function initRevealAnimation(){

    const cards=document.querySelectorAll(

        ".feature-card,.workflow-card,.stat-card,.info-card,.prediction-card"

    );

    if(cards.length === 0) return;

    const observer=new IntersectionObserver((entries)=>{

        entries.forEach(entry=>{

            if(entry.isIntersecting){

                entry.target.classList.add("fade-in");

            }

        });

    },{

        threshold:.15

    });

    cards.forEach(card=>{

        observer.observe(card);

    });

}// ==========================================================
// Animated Counter
// ==========================================================

function animateCounter(element){

    const target = parseFloat(element.innerText);

    if(isNaN(target)) return;

    let current = 0;

    const increment = target / 100;

    const timer = setInterval(()=>{

        current += increment;

        if(current >= target){

            element.innerText = target;

            clearInterval(timer);

        }

        else{

            if(target % 1 === 0){

                element.innerText = Math.floor(current);

            }

            else{

                element.innerText = current.toFixed(2);

            }

        }

    },20);

}

document.querySelectorAll(".stat-card h2").forEach(counter=>{

    animateCounter(counter);

});

// ==========================================================
// Prediction Form Handling
// ==========================================================

function clampNumericInput(input){

    const min = parseFloat(input.min || "0");
    const max = parseFloat(input.max || "100");
    const rawValue = input.value;

    if(rawValue === "") return;

    let value = parseFloat(rawValue);

    if(isNaN(value)){
        input.value = "";
        return;
    }

    if(value < min){
        input.value = min;
        return;
    }

    if(value > max){
        input.value = max;
        return;
    }

    input.value = String(Math.trunc(value));
}

function initPredictionForm(){

    const predictionForm = document.getElementById("predictionForm");

    if(!predictionForm) return;

    const resultBox = document.getElementById("predictionResult");
    const predictedScore = document.getElementById("predictedScore");
    const grade = document.getElementById("grade");
    const performance = document.getElementById("performance");
    const scoreBar = document.getElementById("scoreBar");
    const progressLabel = document.getElementById("progressLabel");
    const performanceBadge = document.getElementById("performanceBadge");
    const gradeBadge = document.getElementById("gradeBadge");
    const recommendation = document.getElementById("recommendation");
    const scoreRing = document.getElementById("scoreRing");
    const button = predictionForm.querySelector("button[type='submit']");

    if(!button || !resultBox || !predictedScore || !grade || !performance || !scoreBar || !progressLabel || !performanceBadge || !gradeBadge || !recommendation || !scoreRing) return;

    const originalButtonText = button.innerHTML;

    predictionForm.querySelectorAll('input[type="number"]').forEach((input) => {

        input.addEventListener("input", () => {
            clampNumericInput(input);
        });

        input.addEventListener("paste", (event) => {
            event.preventDefault();
            const pasted = (event.clipboardData || window.clipboardData).getData("text");
            const cleaned = pasted.replace(/[^0-9.-]/g, "");
            if(cleaned === "") return;

            const value = parseFloat(cleaned);
            if(isNaN(value)) return;

            input.value = value;
            clampNumericInput(input);
        });

    });

    predictionForm.addEventListener("submit", async (event)=>{

        event.preventDefault();

        if(!predictionForm.checkValidity()){

            predictionForm.reportValidity();
            return;

        }

        button.disabled = true;
        button.innerHTML =
            `<span class="spinner-border spinner-border-sm me-2"></span>Predicting...`;

        try{

            const formData = new FormData(predictionForm);
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if(!response.ok){
                throw new Error(data.error || "Prediction failed.");
            }

            if(data.success){

                const score = Number(data.predicted_score);
                const safeScore = Math.max(0, Math.min(100, score));
                const circumference = 2 * Math.PI * 48;
                const offset = circumference - (safeScore / 100) * circumference;

                resultBox.classList.remove("d-none");
                predictedScore.textContent = safeScore.toFixed(0);
                grade.textContent = data.grade;
                performance.textContent = data.performance;
                progressLabel.textContent = `${safeScore.toFixed(0)}%`;
                scoreBar.style.width = `${safeScore}%`;
                scoreBar.textContent = `${safeScore.toFixed(0)}%`;
                scoreRing.style.strokeDashoffset = offset;

                let badgeClass = "bg-success";
                let badgeText = "Excellent";
                let recommendationText = "Excellent academic performance. Continue maintaining study consistency.";

                if (safeScore >= 85) {
                    badgeClass = "bg-success";
                    badgeText = "Excellent";
                    recommendationText = "Excellent academic performance. Continue maintaining study consistency.";
                } else if (safeScore >= 70) {
                    badgeClass = "bg-warning text-dark";
                    badgeText = "Good";
                    recommendationText = "Strong progress. Keep improving study consistency and attendance.";
                } else {
                    badgeClass = "bg-danger";
                    badgeText = "At Risk";
                    recommendationText = "Increase attendance and study hours for better performance.";
                }

                performanceBadge.className = `badge px-3 py-2 rounded-pill ${badgeClass}`;
                performanceBadge.innerHTML = `<i class="fa-solid fa-sparkles me-2"></i>${badgeText}`;
                gradeBadge.className = `badge px-3 py-2 rounded-pill ${badgeClass}`;
                gradeBadge.textContent = data.grade;
                recommendation.textContent = recommendationText;
                resultBox.scrollIntoView({ behavior: "smooth", block: "start" });

            }

            else{

                alert(data.error || "Prediction failed. Please try again.");

            }

        }

        catch(error){

            console.error("Prediction request failed:", error);
            alert("Prediction failed. Please check your connection and try again.");

        }

        finally{

            button.disabled = false;
            button.innerHTML = originalButtonText;

        }

    });

}

// ==========================================================
// Input Focus Animation
// ==========================================================

document.querySelectorAll(

    ".form-control,.form-select"

).forEach(input=>{

    input.addEventListener("focus",()=>{

        input.style.transform="scale(1.02)";

    });

    input.addEventListener("blur",()=>{

        input.style.transform="scale(1)";

    });

});

// ==========================================================
// Card Hover Glow
// ==========================================================

document.querySelectorAll(

".feature-card,.workflow-card,.stat-card"

).forEach(card=>{

    card.addEventListener("mouseenter",()=>{

        card.classList.add("glow");

    });

    card.addEventListener("mouseleave",()=>{

        card.classList.remove("glow");

    });

});

// ==========================================================
// Smooth Anchor Links
// ==========================================================

document.querySelectorAll('a[href^="#"]').forEach(anchor=>{

    anchor.addEventListener("click",function(e){

        e.preventDefault();

        const target=document.querySelector(

            this.getAttribute("href")

        );

        if(target){

            target.scrollIntoView({

                behavior:"smooth"

            });

        }

    });

});

// ==========================================================
// Console Message
// ==========================================================

console.log(

"%cStudent Performance Prediction Dashboard",

"color:#06B6D4;font-size:18px;font-weight:bold;"

);

console.log(

"%cFlask + Machine Learning + Bootstrap",

"color:#3B82F6;font-size:14px;"

);