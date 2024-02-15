

$(document).ready(function () {
    let startButton = $('#start-button');
    let submitButton = $('#submit-score-button');
    let currentQuestionIndex = 0;
    let score = 0;
    let questions = [];
    let timer;
    let timerSeconds = 300;
    let answerChosen = false;
    let selectedFriend;
    let fiftyFiftyUsed = false;
    let currentAudio;
    let phoneAFriendUsed = false;
    



// JavaScript function to start the quiz
// function startQuiz() {
//     // Get the timer data or set a default value (you might have a timer variable)
//     const timerData = {
//         duration: 300, // Duration of the quiz in seconds (5 minutes)
//         // Add other timer-related data if needed
//     };

//     // Make an AJAX request to start the quiz and pass timerData
//     $.ajax({
//         url: '/start_quiz',
//         method: 'GET',
//         data: timerData, // Pass timer data to the server
//         success: function (data) {
//             console.log('Quiz started successfully');
//             // Continue with the rest of your quiz initiation logic
//             // ...
//         },
//         error: function (error) {
//             console.log('Error starting quiz:', error);
//         }
//     });
// }

// // Call this function when you want to start the quiz
// startQuiz();

function startGame() {
    fetchQuestions();
    // Disable the start button
    startButton.prop('disabled', true);

    // Fetch questions and start the timer
   
    startTimer();

    
}


function updateTimer() {
    const minutes = Math.floor(timerSeconds / 60);
    const seconds = timerSeconds % 60;
    $('#timer').text(`Time left: ${pad(minutes)}:${pad(seconds)}`);
}

function startTimer() {
    if (timerSeconds > 0) {
        timer = setTimeout(function countdown() {
            timerSeconds--;

            if (timerSeconds === 30) {
                document.getElementById('warning-tone').play();
            }

            updateTimer();

            if (timerSeconds > 0) {
                startTimer(); // Call the function recursively
            } else {
                // Timer has reached 00:00
                $('#submit-score-button').trigger('click');
            }
        }, 1000); // Update every 1000 milliseconds (1 second)
    }
}

function stopTimer() {
    clearTimeout(timer);
}

    function startTimer() {
        timer = setInterval(function countdown() {
            if (timerSeconds <= 0) {
                // Stop the timer when it reaches 00:00 (0 seconds)
                stopTimer();
                // Invoke the submit button
                $('#submit-score-button').trigger('click');
                return;
            }
    
            timerSeconds--;
    
            if (timerSeconds === 30) {
                document.getElementById('warning-tone').play();
            }
    
            updateTimer();
        }, 1000); // Update every 1000 milliseconds (1 second)
    }
    
    function stopTimer() {
        clearInterval(timer); // Use clearInterval instead of clearTimeout
    }
    
    const startTime = new Date();
    function calculateTimeCompleted() {
        stopTimer(); // Stop the timer to get the final time
    
        // Calculate remaining time in seconds
        const remainingTimeInSeconds = timerSeconds;
    
        // Calculate minutes and seconds separately
        const minutes = Math.floor(remainingTimeInSeconds / 60);
        const seconds = remainingTimeInSeconds % 60;
    
        console.log('Sending time to server:', `${pad(minutes)}:${pad(seconds)}`);
    
        return `${pad(minutes)}:${pad(seconds)}`;
    }
    
    function pad(num) {
        return num.toString().padStart(2, '0');
    }
    function formatElapsedTime(seconds) {
        const pad = (num) => num.toString().padStart(2, '0');
    
        const minutes = Math.floor(seconds / 60);
        seconds %= 60;
    
        console.log('Formatted Time:', `${pad(minutes)}:${pad(seconds)}`);
    
        return `${pad(minutes)}:${pad(seconds)}`;
    }
    
    
    // function formatElapsedTime(seconds) {
    //     const pad = (num) => num.toString().padStart(2, '0');
    
    //     const days = Math.floor(seconds / (24 * 3600));
    //     seconds -= days * (24 * 3600);
    //     const hours = Math.floor(seconds / 3600);
    //     seconds -= hours * 3600;
    //     const minutes = Math.floor(seconds / 60);
    //     seconds -= minutes * 60;
    
    //     return `${pad(days)}-${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
    // }
 const eduSounds = ['edu6.mp3','edu1.mp3', 'edu2.mp3', 'edu3.mp3', 'edu4.mp3', 'edu5.mp3'];

// Function to play a random edu sound
// Function to play a random edu sound
function playRandomEduSound() {
    const randomIndex = Math.floor(Math.random() * eduSounds.length);
    const randomEduSound = eduSounds[randomIndex];

    // Pause the currently playing audio (if any)
    if (currentAudio) {
        currentAudio.pause();
    }

    // Create a new audio element and play the sound
    currentAudio = new Audio(`static/sound/${randomEduSound}`);
    currentAudio.play();
}
    
    function fetchQuestions() {
        $.ajax({
            url: '/get_questions',
            method: 'GET',
            success: function (data) {
                if (data.data.length > 0) {
                    questions = data.data;
                    displayQuestion();
                } else {
                    $('#question-container').html('<p>No questions available.</p>');
                }
            },
            error: function (error) {
                console.log('Error fetching questions:', error);
                $('#question-container').html('<p>Error fetching questions. Please try again later.</p>');
            }
        });
    }

    function shuffleOptions(question) {
        const options = [question.option1, question.option2, question.option3, question.option4];
        for (let i = options.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [options[i], options[j]] = [options[j], options[i]];
        }
        return options;
    }
    function sample(array, count) {
        const shuffled = array.slice(0);
        let i = array.length - 1;
        let len = Math.min(count, array.length);
        
        while (i > 0 && len-- > 0) {
            const rand = Math.floor((i + 1) * Math.random());
            [shuffled[i], shuffled[rand]] = [shuffled[rand], shuffled[i]];
            i--;
        }
    
        return shuffled.slice(i + 1);
    }
    

    let displayedQuestionNumber = 0; // Initialize the displayed question number
    
    function displayQuestion() {
        stopTimer(); // Stop the timer if it's running
    
        const question = questions[currentQuestionIndex];
        const shuffledOptions = shuffleOptions(question);
        
        $('#question-container').html(`
        <h2 class="text mt-5 text-center" id="question">Question ${displayedQuestionNumber}: ${question.question_text}</h2>
        <div id="timer"></div>
        <ul id="ques" class="list-unstyled text-center">
            <li class="quez d-block mx-auto" data-answer="${shuffledOptions[0]}">A. ${shuffledOptions[0]}</li>
            <li class="quez d-block mx-auto" data-answer="${shuffledOptions[1]}">B. ${shuffledOptions[1]}</li>
            <li class="quez d-block mx-auto" data-answer="${shuffledOptions[2]}">C. ${shuffledOptions[2]}</li>
            <li class="quez d-block mx-auto" data-answer="${shuffledOptions[3]}">D. ${shuffledOptions[3]}</li>
        </ul>
        <div id="cheering-cap"></div>
        <audio id="cheering-sound" src="static/sound/correct.mp3"></audio>
        <audio id="wrong-tone" src="static/sound/wrong.mp3"></audio>
    `);
    
        displayedQuestionNumber++; // Increment the displayed question number
    
        answerChosen = false;
    
        $('#ques').on('click', '.quez', function () {
            if (answerChosen) {
                return;
            }
    
            const chosenAnswer = $(this).data('answer');
            const correctAnswer = question.correct_answer;
    
            if (chosenAnswer === correctAnswer) {
                score++;
                $('#cheering-cap').html('🎉').fadeIn(500).fadeOut(500).fadeIn(500);
                playBeep('cheering-sound', 'green', $(this));
            } else {
                playBeep('wrong-tone', 'red', $(this));
            }
    
            answerChosen = true;
    
            if (!$('#next-question').length) {
                $('#question-container').append('<button id="next-question">Next Question</button>');
            }
        });
    
        $('#next-question').on('click', function () {
            currentQuestionIndex++;
            displayQuestion();
        });
    
        startTimer(); // Start the timer after displaying the question
    }

    function playBeep(soundId, backgroundColor, element) {
        const beepElement = document.getElementById(soundId);
        if (beepElement && element) {
            beepElement.play();

            element.css('background-color', backgroundColor);

            setTimeout(() => {
                element.css('background-color', '');
            }, 1000);
        }
    }

    function calculateScore() {
        return (score / questions.length) * 100;
    }

    $(document).on('click', '#start-button', function () {
        currentQuestionIndex = 0;
        score = 0;
        timerSeconds = 300;
        answerChosen = false;
        gameInProgress = true;
        startGame();
        playRandomEduSound();
        fetchQuestions();
        $('#fifty-fifty-button').show();
        $('#phone-a-friend-button').show();
    });

    $(document).on('click', '#next-question', function () {
        stopTimer();
    
        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            displayQuestion();
        } else {
            calculateScore();
            $('#submit-score-button').show(); // Show the submit button after the game is over
        }
    
        // Clear the lifeline conversation
        updateUIWithLifeline('');
    
        $(this).remove();
    });
// Function to clear stored game progress
function clearStoredProgress() {
    localStorage.removeItem('userProgress');
}

// Function to store game progress in local storage
function storeGameProgress() {
    const userProgress = {
        score: score,
        timeCompleted: calculateTimeCompleted(),
        gameStatus: gameInProgress ? 'in progress' : 'finished',
        currentQuestionIndex: currentQuestionIndex,
    };
    localStorage.setItem('userProgress', JSON.stringify(userProgress));
}

// Placeholder function to resume the game based on stored progress
function resumeGameFromStorage() {
    const storedProgress = localStorage.getItem('userProgress');

    if (storedProgress) {
        const parsedProgress = JSON.parse(storedProgress);

        // Restore game variables
        score = parsedProgress.score;
        currentQuestionIndex = parsedProgress.currentQuestionIndex;
        gameInProgress = parsedProgress.gameStatus === 'in progress';

        // Update UI and continue game logic
        updateUIWithLifeline(''); // Placeholder for updating UI, adjust as needed
        displayQuestion(); // Adjust this based on your actual UI structure
        startTimer(); // Resume the timer
    }
}

// Function to handle the logic when the submit button is clicked
$('#submit-score-button').on('click', function () {
    const timeCompletedResult = calculateTimeCompleted();
    const gameStatus = (currentQuestionIndex === questions.length - 1) ? 'finished' : 'in progress';

    // Store progress in local storage
    storeGameProgress();

    submitButton.prop('disabled', true);
    $('#fifty-fifty-button, #phone-a-friend-button').prop('disabled', true).css('opacity', 0.5);

    // Send data to the server
    submitScoreToServer(score, timeCompletedResult, gameStatus);

    if (currentAudio) {
        currentAudio.pause();
    }
    gameInProgress = false;

    if (score < 50) {
        playMuehSound();
    } else {
        playRightSound();
    }

    // Append buttons to play again and return home
    const playAgainButton = $('<button>').text('Play Again').addClass('btn btn-primary');
    const returnHomeButton = $('<button>').text('Return Home').addClass('btn btn-secondary');

    playAgainButton.on('click', function () {
        // Redirect to the /choose_category route
        window.location.href = '/choose_category';
    });

    returnHomeButton.on('click', function () {
        // Redirect to the /cust_home route
        window.location.href = '/custhome';
    });

    // Append the buttons to a container in your HTML (adjust the selector accordingly)
    $('#button-container').empty().append(playAgainButton, returnHomeButton);
});


// Function to check for stored progress and resume
function checkAndResumeProgress() {
    const storedProgress = localStorage.getItem('userProgress');

    if (storedProgress) {
        const parsedProgress = JSON.parse(storedProgress);

        // Resume the game using the stored progress
        resumeGame(parsedProgress);

        // Clear stored progress after resuming
        clearStoredProgress();
    }
}

// Function to resume the game based on stored progress
function resumeGame(progress) {
    // Update UI with stored progress
    updateUIWithLifeline(progress.lifeline_conversation);

    // Resume timer if applicable
    if (progress.gameStatus === 'in progress') {
        const remainingTime = calculateRemainingTime(progress.timeCompleted);
        startTimer(remainingTime);
    }

    // Continue game logic based on game status
    if (progress.gameStatus === 'in progress') {
        loadNextQuestion();
    } else if (progress.gameStatus === 'finished') {
        displayFinalScore();
    }
}

// Other functions (playMuehSound, playRightSound, updateUIWithLifeline, etc.) remain unchanged

    function checkAndResumeProgress() {
    const storedProgress = localStorage.getItem('userProgress');
    
    if (storedProgress) {
        const parsedProgress = JSON.parse(storedProgress);
        
        // Resume the game using the stored progress
        resumeGame(parsedProgress);

        // Clear stored progress after resuming
        clearStoredProgress();
    }
}

// Function to resume the game based on stored progress
function resumeGame(progress) {
    // Update UI with stored progress
    updateUI(progress);

    // Resume timer if applicable
    if (progress.gameStatus === 'in progress') {
        const remainingTime = calculateRemainingTime(progress.timeCompleted);
        startTimer(remainingTime);
    }

    // Continue game logic based on game status
    if (progress.gameStatus === 'in progress') {
        loadNextQuestion();
    } else if (progress.gameStatus === 'finished') {
        displayFinalScore();
    }
}
    
    function playMuehSound() {
        const audioContext = new AudioContext();

        // Load 'mueh' sound
        const muehSound = new Audio('static/sound/wah.mp3');
        const muehSource = audioContext.createMediaElementSource(muehSound);
        muehSource.connect(audioContext.destination);
    
        // Play 'mueh' sound
        muehSound.play();
    }
    
    function playRightSound() {
        const audioContext = new AudioContext();

        
        const rightSound = new Audio('static/sound/right.mp3');
        const rightSource = audioContext.createMediaElementSource(rightSound);
        rightSource.connect(audioContext.destination);
    
        
        rightSound.play();
    }

    function updateUIWithLifeline(lifeline_conversation) {
        console.log('Updating UI with lifeline conversation:', lifeline_conversation);
    
        const conversationContainer = document.getElementById('phone-friend-conversation');
    
        if (conversationContainer) {
            console.log('Clearing existing content');
            // Clear existing content
            conversationContainer.innerHTML = '';
    
            // Check if lifeline_conversation is a string
            if (typeof lifeline_conversation === 'string') {
                console.log('Appending conversation lines');
                // Split the conversation into lines
                const lines = lifeline_conversation.split('\n');
    
                // Function to append a line with delay
                const appendLineWithDelay = (index) => {
                    if (index < lines.length) {
                        const lineElement = document.createElement('div');
                        lineElement.innerHTML = lines[index];  // Use innerHTML to parse HTML tags
                        conversationContainer.appendChild(lineElement);
                        setTimeout(() => appendLineWithDelay(index + 1), 1000); // Adjust delay as needed
                    }
                };
    
                // Start appending lines with delay
                appendLineWithDelay(0);
            } else {
                // Handle the case where lifeline_conversation is not a string (e.g., log an error)
                console.error('Invalid lifeline_conversation:', lifeline_conversation);
            }
        } else {
            console.log('Conversation container not found');
        }
    }
    
    // Add this code in your JavaScript file or script tag
// Add this code in your JavaScript file or script tag
setTimeout(function(){
    var userLine = document.createElement("div");
    userLine.style = "margin-bottom: 10px; " + confidence_style;
    userLine.innerHTML = '<span style="font-weight: bold; color: ' + user_color + ';">User:</span> I\'m confident!';
    document.getElementById("user-line").parentNode.appendChild(userLine);
}, 4000);  // 1000 milliseconds (1 second) delay


    
    


 


    function getChoicesFromUI() {
        const choicesElement = $('#ques'); // Update the selector based on your HTML structure
        const choices = [];
    
        choicesElement.find('li').each(function () {
            // Assuming each choice is wrapped in an <li> element
            choices.push($(this).data('answer'));
        });
    
        return choices;
    }
let friendOptions = [
    { name: 'Mr. Guesser', accuracy: 0.6 },
    { name: 'Mrs. Joy', accuracy: 0.75 },
    { name: 'Mr. Accurate', accuracy: 1.0 }
];

// function displayPhoneAFriendOptions() {
//     const optionsContainer = $('#phone-friend-options');
//     optionsContainer.empty(); // Clear existing options

//     friendOptions.forEach((friend, index) => {
//         const optionElement = $(`<button class="friend-option" data-index="${index}">${friend.name} (${friend.accuracy * 100}%)</button>`);
//         optionsContainer.append(optionElement);
//     });

//     // Add a simplified click event for debugging
//     $('.friend-option').off('click');
//     $('.friend-option').on('click', function () {
//         const selectedIndex = $(this).data('index');
//         alert('Click event detected! Selected Index: ' + selectedIndex);
//         console.log('Selected Index:', selectedIndex);
//     });
// }

var friendModalOpen = false;

function closeFriendModal() {
    var friendModal = document.querySelector('#friend-selection-modal');
    if (friendModal) {
        friendModal.style.display = 'none';
        friendModal.parentNode.removeChild(friendModal);
        friendModalOpen = false;
    }
}

function openFriendModal() {
    if (phoneAFriendUsed) {
        console.log('Phone a friend lifeline already used.');
        return;
    }

    if (friendModalOpen) {
        closeFriendModal();
        return;
    }

    var friendModal = document.createElement('div');
    friendModal.innerHTML = `
        <div id="friend-selection-modal" class="modal">
            <div class="modal-content">
                <span class="close" id="close-friend-modal">&times;</span>
                <p>Please select a friend:</p>
            </div>
        </div>
    `;

    var friends = [
        { name: 'Mr. Guesser', accuracy: 0.5 },
        { name: 'Mrs. Joy', accuracy: 0.75 },
        { name: 'Mr. Accurate', accuracy: 1.0 }
    ];

    friends.forEach(function (friend, index) {
        var button = document.createElement('button');
        button.className = 'friend-option';
        button.setAttribute('data-index', index + 1);
        button.setAttribute('data-accuracy', friend.accuracy);
        button.textContent = friend.name + ' (accuracy: ' + friend.accuracy + ')';
        friendModal.querySelector('.modal-content').appendChild(button);
    });

    document.body.appendChild(friendModal);
    friendModal.querySelector('#friend-selection-modal').style.display = 'block';

    var closeFriendModalSpan = document.querySelector('#close-friend-modal');
    closeFriendModalSpan.addEventListener('click', closeFriendModal);

    var friendOptions = document.querySelectorAll('.friend-option');
    friendOptions.forEach(function (friendOption) {
        friendOption.addEventListener('click', function () {
            const selectedIndex = Number(friendOption.getAttribute('data-index'));
            const selectedFriend = friends[selectedIndex - 1].name;
            handleFriendOption(selectedFriend, selectedIndex);

            const accuracy = parseFloat(friendOption.getAttribute('data-accuracy'));
            const correctAnswer = getCorrectAnswerFromUI();
            const correctAnswerIndex = getCorrectAnswerIndexFromUI();
            applyLifeline('phone_a_friend', accuracy, correctAnswer, correctAnswerIndex, selectedFriend, selectedIndex);
        });
    });

    friendModalOpen = true;
}

function applyLifeline(lifelineType, accuracy, correctAnswer, correctAnswerIndex, selectedFriend, selectedIndex) {
    console.log('Applying lifeline:', lifelineType);
    
    if (fiftyFiftyUsed) {
        console.log('Phone a friend lifeline already used.');
        return;
    }

    console.log('Accuracy:', accuracy);
    console.log('Correct Answer:', correctAnswer);
    console.log('Correct Answer Index:', correctAnswerIndex);
    console.log('Selected Friend:', selectedFriend);
    console.log('Selected Friend Index:', selectedIndex);

    // Update the phoneAFriendUsed variable
    let fiftyFiftyUsed = True;

    // You can implement your logic here, e.g., update UI based on accuracy
}


function getCorrectAnswerFromUI() {
    // Replace this with your logic to get the correct answer from the UI
    return 'Correct Answer';
}

function getCorrectAnswerIndexFromUI() {
    // Replace this with your logic to get the index of the correct answer from the UI
    return 0; // Assuming the correct answer is at index 0
}

function handleFriendOption(selectedFriend, selectedIndex) {
    console.log(`Selected friend: ${selectedFriend}`);
    console.log(`Selected friend index: ${selectedIndex}`);
    closeFriendModal();
}

document.getElementById('phone-a-friend-button').addEventListener('click', openFriendModal);

// Style the modal
var style = document.createElement('style');
style.innerHTML = `
    .modal {
        display: none;
        position: fixed;
        z-index: 1;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
    }

    .modal-content {
        background-color: #fefefe;
        margin: 15% auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
        max-width: 800px;
    }

    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
    }

    .close:hover,
    .close:focus {
        color: black;
        text-decoration: none;
        cursor: pointer;
    }

    .friend-option {
        display: block;
        margin-bottom: 10px;
        padding: 10px;
        background-color: #ddd;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .friend-option:hover {
        background-color: #eee;
    }
`;
document.head.appendChild(style);


function handlePhoneAFriendLifeline(selectedFriend) {
    // Perform lifeline logic directly on the frontend
    const accuracy = selectedFriend.accuracy;
    const correctAnswer = getCorrectAnswerFromUI();
    const correctAnswerIndex = $('#choices option:selected').index();

    // Display lifeline-related UI updates
    updateUIWithLifeline([]);
    // displayPhoneAFriendConversation("I'm confident! The answer is definitely correct.");

    // Additional lifeline-specific logic if needed

    // Log the details for debugging
    console.log('Applying lifeline: phone_a_friend');
    console.log('Accuracy:', accuracy);
    console.log('Correct Answer:', correctAnswer);
    console.log('Correct Answer Index:', correctAnswerIndex);
}



function getCorrectAnswerFromUI() {
    // Assuming your currentQuestion object has a property like 'correct_answer'
    if (currentQuestionIndex >= 0 && currentQuestionIndex < questions.length) {
        const correctAnswer = questions[currentQuestionIndex].correct_answer;
        console.log('Correct Answer:', correctAnswer); // Add this line for debugging
        if (correctAnswer !== undefined && correctAnswer !== null) {
            return correctAnswer;
        } else {
            console.error('Correct answer is undefined or null:', correctAnswer);
        }
    } else {
        // Handle the case where the current question index is out of bounds
        console.error('Invalid current question index:', currentQuestionIndex);
    }
    return null;
}

function simulate_delayed_response(conversation) {
    // Split the conversation into lines
    const lines = conversation.split('\n');

    // Simulate a delayed conversation
    const delayed_lines = [];
    const initialDelay = 1; // Short delay for the first message
    const subsequentDelay = 3; // Longer delay for subsequent messages

    lines.forEach((line, index) => {
        const delay = index === 0 ? initialDelay : subsequentDelay;

        // Delay the line
        delayed_lines.push(`Friend: ${line}`);
        delayed_lines.push(`User: How confident are you?`);

        setTimeout(() => {
            // After the delay, update the UI
            updateUIWithLifeline(`${line}\nUser: How confident are you?`);
            
            if (index === lines.length - 1) {
                // Clear the UI after the conversation ends
                setTimeout(() => {
                    updateUIWithLifeline('');
                }, subsequentDelay * 1000);
            }
        }, delay * 1000); // Convert seconds to milliseconds
    });

    // Return the entire delayed conversation
    return delayed_lines.join('\n');
}



function applyLifeline(lifeline, accuracy, correctAnswer, correctAnswerIndex) {
    console.log('Applying lifeline:', lifeline);
    console.log('Accuracy:', accuracy);
    console.log('Correct Answer:', correctAnswer);
    console.log('Correct Answer Index:', correctAnswerIndex);

    const updatedChoices = getChoicesFromUI();

    // Append the correct answer to the choices array
    updatedChoices.push(correctAnswer);

    // Assuming you have an array called 'otherOptions'
    const otherOptions = ['option1', 'option2', 'option3']; // Replace this with your actual other options
    
    // Concatenate other options with the updatedChoices array
    updatedChoices.push(...otherOptions);

    $.ajax({
        url: '/apply_lifeline',
        method: 'GET',
        data: {
            choices: updatedChoices.join(','),
            correct_answer: correctAnswer,
            lifelines: lifeline,
            accuracy:accuracy,
            correct_answer_index: correctAnswerIndex,
        },
        success: function (data) {
            console.log('Received lifeline data:', data);
            console.log('Accuracy:', accuracy); // Add this line
            console.log('choices:',updatedChoices.join(','))
            

            

            // Update the UI with lifeline conversation
            updateUIWithLifeline(data.lifeline_conversation);

            if (lifeline === 'fifty_fifty' && data.hidden_options) {
                // Update the UI with hidden options
                updateUIWithHiddenOptions(data.hidden_options);
            }
        },
        error: function (error) {
            console.log(`Error applying ${lifeline} lifeline:`, error);
        }
    });
}
function updateUIWithHiddenOptions(hiddenOptions) {
    console.log('Hidden Options:', hiddenOptions);

    // Iterate through hidden options and hide corresponding elements
    hiddenOptions.forEach(hiddenOption => {
        const element = $(`li[data-answer="${hiddenOption}"]`);
        if (element.length > 0) {
            element.fadeOut(500);
        } else {
            console.error(`Element with data-answer="${hiddenOption}" not found.`);
        }
    });
}




function displayPhoneAFriendConversation(conversation, correctAnswer) {
    console.log('Displaying conversation:', conversation);
    console.log('Correct answer:', correctAnswer);

    // Check if the conversation is null
    if (conversation === null) {
        $('#phone-friend-conversation').text('No conversation available.');
    } else {
        // Clear existing content
        $('#phone-friend-conversation').html('');

        // Split the conversation into lines
        const lines = conversation.split('\n');

        // Iterate through the lines and display them with delays
        lines.forEach((line, index) => {
            // Add a longer delay before displaying each line
            setTimeout(() => {
                // Update the UI with the conversation
                $('#phone-friend-conversation').append(`<div>Phone a Friend: ${line}</div>`);
                
                // If this is not the last line, add a longer delay before the user prompt
                if (index < lines.length - 1) {
                    setTimeout(() => {
                        $('#phone-friend-conversation').append('<div>User: How confident are you?</div>');
                    }, 15000);  // Adjust the delay time as needed
                }
            }, index * 30000);  // Adjust the delay time as needed
        });

        // Update the correct answer in your UI as needed
        // For example, you can display it next to the conversation
        $('#correct-answer').text(`Correct Answer: ${correctAnswer}`);
    }
}





// // Apply 50:50 Lifeline
// $('#fifty-fifty-button').on('click', function () {
//     // Call the correct function
//     applyFiftyFifty();
// });

// Apply Phone a Friend Lifeline
// Apply Phone a Friend Lifeline
// Apply Phone a Friend Lifeline
$('#phone-a-friend-button').on('click', function () {
    // Disable the button after it's clicked to prevent multiple requests
    if (!phoneAFriendUsed) {
        phoneAFriendUsed = true;
        $(this).prop('disabled', true).css('opacity', 0.5); // Add this line to gray out the button
    } else {
        console.log('Phone a friend lifeline already used.');
        return;
    }

    // Play the thinking sound
    playThinkingSound();

    const accuracy = data-accuracy($('#accuracy').val());
    const correctAnswer = getCorrectAnswerFromUI();
    const correctAnswerIndex = $('#choices option:selected').index();

    // Apply phone a friend lifeline
    invokeLifeline();
    applyLifeline('phone_a_friend', accuracy, correctAnswer, correctAnswerIndex);
});
// Update the function name to match the correct one
function applyFiftyFifty() {
    console.log('applyFiftyFifty function called');

    const correctAnswer = questions[currentQuestionIndex].correct_answer;
    const options = document.querySelectorAll('#ques .quez'); // Updated selector

    console.log('Options:', options);

    // Create an array with indices of options
    const optionIndices = Array.from({ length: options.length }, (_, index) => index);

    // Randomly choose two indices to hide
    const optionsToHide = getRandomElements(optionIndices, 2);

    // Update the UI to hide the selected options
    options.forEach((option, index) => {
        if (optionsToHide.includes(index)) {
            option.classList.add('hidden'); // Add a 'hidden' class
        } else {
            option.classList.remove('hidden'); // Remove 'hidden' class
        }
    });

    // ...
}

// Helper function to get random elements from an array
function getRandomElements(array, numElements) {
    const shuffledArray = shuffleArray([...array]);
    return shuffledArray.slice(0, numElements);
}




// Helper function to get a random element from an array
function getRandomElement(array) {
    if (array.length === 0) {
        return null; // Handle empty array
    }
    const randomIndex = Math.floor(Math.random() * array.length);
    return array[randomIndex];
}

// Helper function to shuffle an array
function shuffleOptions(question) {
    const options = [question.option1, question.option2, question.option3, question.option4];
    const correctAnswer = question.correct_answer;

    // Add correct answer to options array
    options.push(correctAnswer);

    // Shuffle the options
    for (let i = options.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
    }

    return options;
}

$(document).on('click', '#fifty-fifty-button', function () {
    console.log('Button clicked');

    if (!fiftyFiftyUsed) {
        fiftyFiftyUsed = true;
        $(this).prop('disabled', true).css('opacity', 0.5); // Add this line to gray out the button
    } else {
        console.log('fiftyfifty lifeline already used.');
        return;
    }
    // Call the correct function
    console.log('Calling applyFiftyFifty');
    applyFiftyFifty();
});

// Add this shuffleArray function
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// function submitScoreToServer(score, timeCompleted, gameStatus) {
//     // Prepare the data to send in the AJAX request
//     const dataToSend = {
//         score: score.toFixed(2),
//         time_completed: timeCompleted.formattedTime,
//         gameStatus: gameStatus
//     };

//     // Make the AJAX request
//     $.ajax({
//         url: '/submit_score',
//         method: 'GET',
//         data: dataToSend,
//         success: function (response) {
//             console.log('Score submitted successfully:', response);
//             // Handle success if needed
//         },
//         error: function (error) {
//             console.error('Error submitting score:', error);
//             // Handle error if needed
//         }
//     });
// }


// Event listener for the 'Fifty-Fifty Lifeline' button


function submitScoreToServer(score, timeCompletedInSeconds, gameStatus) {
    const percentageScore = calculateScore();

    // Create a canvas element for the chart
    const canvas = document.createElement('canvas');
    canvas.id = 'scoreChart';
    canvas.width = 500; // Set the desired width
    canvas.height = 400; // Set the desired height

    // Create a Chart.js pie chart
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Correct', 'Incorrect'],
            datasets: [{
                data: [score, questions.length - score],
                backgroundColor: ['#36A2EB', '#FF6384'],
            }],
        },
        options: {
            animation: {
                animateRotate: true, // Enable rotation animation
            },
            responsive: false, // Disable responsiveness to maintain the fixed size
        },
    });

    // Append the canvas to the container
    $('#question-container').html(`<p>Your score: ${percentageScore.toFixed(2)}%</p>`).append(canvas);

    // Disable back button after showing the chart
    disableBackButton();

    // Submit the score to the server using AJAX
    $.ajax({
        url: '/submit_score',
        method: 'GET',
        data: {
            score: percentageScore.toFixed(2),
            time_completed: calculateTimeCompleted(),
            gameStatus: gameStatus
        },
        success: function (data) {
            console.log('Score submitted successfully');
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log('Error submitting score:', errorThrown);
        }
    });
}


function disableBackButton() {
    // Push a new state to the browser history
    const newUrl = window.location.pathname + window.location.search;
    history.pushState(null, null, newUrl);

    // Add an event listener to handle the back button
    window.addEventListener('popstate', function () {
        // Push another state to prevent going back
        history.pushState(null, null, newUrl);
    });

    // Return true to indicate that the back button is disabled
    return true;
}


// $(document).ready(function () {
//     let currentQuestionIndex = 0;
//     let score = 0;
//     let questions = [];
//     let timer;
//     let timerSeconds = 300; // Initial timer value
//     let answerChosen = false;

//     function updateTimer() {
//         const minutes = Math.floor(timerSeconds / 60);
//         const seconds = timerSeconds % 60;
//         $('#timer').text(`Time left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`);
//     }

//     function startTimer() {
//         timer = setInterval(function () {
//             if (timerSeconds === 0) {
//                 clearInterval(timer);
//                 calculateScore();
//                 return;
//             }

//             timerSeconds--;

//             if (timerSeconds === 30) {
//                 document.getElementById('warning-tone').play();
//             }

//             updateTimer();
//         }, 1000);
//     }

//     function stopTimer() {
//         clearInterval(timer);
//     }

//     function fetchQuestions() {
//                 $.ajax({
//                     url: '/get_questions',
//                     method: 'GET',
//                     success: function (data) {
//                         if (data.data.length > 0) {
//                             questions = data.data;
//                             displayQuestion();
//                         } else {
//                             $('#question-container').html('<p>No questions available.</p>');
//                         }
//                     },
//                     error: function (error) {
//                         console.log('Error fetching questions:', error);
//                         $('#question-container').html('<p>Error fetching questions. Please try again later.</p>');
//                     }
//                 });
//             }
        
//             function shuffleOptions(question) {
//                 const options = [question.option1, question.option2, question.option3, question.option4];
//                 for (let i = options.length - 1; i > 0; i--) {
//                     const j = Math.floor(Math.random() * (i + 1));
//                     [options[i], options[j]] = [options[j], options[i]];
//                 }
//                 return options;
//             }

//             function displayQuestion() {
//                 stopTimer(); 
            
//                 const question = questions[currentQuestionIndex];
//                 const shuffledOptions = shuffleOptions(question);
            
//                 $('#question-container').html(`
//                     <div id="question-info">
//                         <p id="question-number" style="background-color:#37003C;color:white;padding:5px; width:10%;margin-top:10px;text-align:center;">Question ${currentQuestionIndex + 1}</p>
//                         <div id="timer"></div>
//                     </div>
//                     <h2 class="text mt-5 text-center" id="question">${question.question_text}</h2>
//                 <ul id="ques" class="text-center">
//                     <li class="quez" data-answer="${shuffledOptions[0]}">A. ${shuffledOptions[0]}</li>
//                     <li class="quez" data-answer="${shuffledOptions[1]}">B. ${shuffledOptions[1]}</li>
//                     <li class="quez" data-answer="${shuffledOptions[2]}">C. ${shuffledOptions[2]}</li>
//                     <li class="quez" data-answer="${shuffledOptions[3]}">D. ${shuffledOptions[3]}</li>
//                  </ul>
                
//                     <div id="cheering-cap"></div>
//                     <audio id="cheering-sound" src="static/sound/right.mp3"></audio>
//                     <audio id="wrong-tone" src="static/sound/wrong.mp3"></audio>
//                     <button id="next-question">Next Question</button>
//                 `);
            
//                 console.log('Cheering sound element:', document.getElementById('cheering-sound'));
//                 console.log('Wrong tone sound element:', document.getElementById('wrong-tone'));
            
//                 answerChosen = false;
            
//                 $('.quez').on('click', function () {
//                     if (answerChosen) {
//                         return;
//                     }
            
//                     const chosenAnswer = $(this).data('answer');
//                     const correctAnswer = question.correct_answer;
            
//                     if (chosenAnswer === correctAnswer) {
//                         score++;
//                         $('#cheering-cap').html('🎉').fadeIn(500).fadeOut(500).fadeIn(500);
//                         playBeep('cheering-sound', 'green', $(this));
//                     } else {
//                         playBeep('wrong-tone', 'red', $(this));
//                     }
            
//                     answerChosen = true;
//                     $('.quez').off('click');
//                 });
            
//                 $('#next-question').on('click', function () {
//                     if (currentQuestionIndex < questions.length - 1) {
//                         currentQuestionIndex++;

//                         displayQuestion();
//                     } else {
//                         calculateScore();
//                     }
//                 });
            
//                 startTimer(); 
//             }
            
//             // Shuffle the questions array
//             function shuffleQuestions() {
//                 for (let i = questions.length - 1; i > 0; i--) {
//                     const j = Math.floor(Math.random() * (i + 1));
//                     [questions[i], questions[j]] = [questions[j], questions[i]];
//                 }
//             }
            
//             // Call shuffleQuestions before starting the game
//             $(document).on('click', '#start-button', function () {
//                 currentQuestionIndex = 0;
//                 score = 0;
//                 timerSeconds = 300;
//                 answerChosen = false;
//                 shuffleQuestions();
//                 fetchQuestions();
//             });
            
//             function playBeep(soundId, backgroundColor, element) {
//                 const beepElement = document.getElementById(soundId);
//                 if (beepElement && element) {
//                     beepElement.play();
            
//                     // Change the background color of the clicked option
//                     element.css('background-color', backgroundColor);
            
//                     setTimeout(() => {
//                         element.css('background-color', ''); 
//                     }, 1000);
//                 }
//             }
//             $(document).ready(function () {
//                 // Define calculateScore function
//                 function calculateScore() {
//                     const percentageScore = (score / questions.length) * 100;
            
//                     // Get the CSRF token from the meta tag
//                     // const csrfToken = $('meta[name=csrf-token]').attr('content');
//                     var csrf = "{{csrf_token()}}"
            
//                     $.ajax({
//                         url: '/submit_score',
//                         method: 'POST',
//                         // headers: {
//                         //     'X-CSRFToken': csrfToken
//                         // },
//                         data: { score: percentageScore, csrf_token: csrf },
//                         success: function (data) {
//                             console.log('Score submitted successfully');
//                             $('#question-container').html(`<p>Your score: ${percentageScore.toFixed(2)}%</p>`);
//                             disableBackButton();
//                         },
//                         error: function (error) {
//                             console.log('Error submitting score:', error);
//                             $('#question-container').html('<p>Error submitting score. Please try again later.</p>');
//                         }
//                     });
//                 }
            
//                 // Define disableBackButton function
//                 function disableBackButton() {
//                     history.pushState(null, null, location.href);
//                     window.onpopstate = function (event) {
//                         history.go(1);
//                     };
//                 }
            
//                 $('#submit-score-button').on('click', function () {
//                     const form = $('#quiz-form');
//                     const formData = form.serialize();
                    
//                     calculateScore();
               });
