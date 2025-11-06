// ===== TELEGRAM WEBAPP INTEGRATION FOR FLY CATCHER =====
// Add this to your flycatcher.html file

// Initialize Telegram WebApp
let tg = window.Telegram?.WebApp;
let telegramEnabled = false;

if (tg) {
    tg.ready();
    tg.expand();
    telegramEnabled = true;
    console.log("Telegram WebApp initialized");
}

// Function to send score to bot
function sendScoreToTelegram(finalScore) {
    if (!telegramEnabled || !tg) {
        console.log("Not in Telegram, score not sent");
        return false;
    }

    try {
        tg.sendData(JSON.stringify({
            score: finalScore
        }));
        console.log("Score sent to bot:", finalScore);

        // Optional: Show a brief message
        tg.showAlert("Score submitted: " + finalScore + " points!");

        // Optional: Close game after 2 seconds
        setTimeout(() => {
            tg.close();
        }, 2000);

        return true;
    } catch (e) {
        console.error("Error sending score:", e);
        return false;
    }
}

// ===== INTEGRATION INSTRUCTIONS =====
//
// STEP 1: Add this entire file to your flycatcher.html in a <script> tag
//         OR include it as: <script src="telegram-integration.js"></script>
//
// STEP 2: Find where your game ends (game over function)
//
// STEP 3: Call sendScoreToTelegram(yourScoreVariable) when game ends
//
// EXAMPLE:
// function gameOver() {
//     // Your existing code...
//     showGameOverScreen();
//
//     // ADD THIS LINE:
//     sendScoreToTelegram(score);  // Use your actual score variable name
// }
//
// COMMON VARIABLE NAMES TO LOOK FOR:
// - score
// - totalScore
// - finalScore
// - points
// - playerScore
//
// The game will still work normally in browsers,
// it only sends scores when opened in Telegram!
