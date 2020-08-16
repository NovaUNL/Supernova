function appendExercisePicker(elem) {
    let picker = document.createElement('div');
    picker.classList.add("subexercises-options");
    let writtenBtn = document.createElement('input');
    writtenBtn.type = "button";
    writtenBtn.value = "Desenvolvimento";
    writtenBtn.onclick = function () {
        appendWriteQuestion(elem);
        moveExercisePicker(picker);
    };
    picker.appendChild(writtenBtn);
    let msBtn = document.createElement('input');
    msBtn.type = "button";
    msBtn.value = "Escolha múltipla";
    msBtn.onclick = function () {
        appendSelectQuestion(elem);
        moveExercisePicker(picker)
    };
    picker.appendChild(msBtn);
    let groupBtn = document.createElement('input');
    groupBtn.type = "button";
    groupBtn.value = "Grupo";
    groupBtn.onclick = function () {
        appendGroupQuestion(elem);
        moveExercisePicker(picker);
    };
    picker.appendChild(groupBtn);
    elem.appendChild(picker);
}

function moveExercisePicker(picker) {
    let parent = picker.parentNode;
    parent.removeChild(picker);
    // If this is not the exercise root move to the end
    if (document.getElementById("exercise-editor") !== parent) {
        parent.appendChild(picker);
    }
}

function appendWriteQuestion(elem, enunciationVal, answerVal) {
    let exercisePart = document.createElement('div');
    exercisePart.classList.add('exercise', 'write');
    let closeBtn = document.createElement('span');
    closeBtn.classList.add('exercise-delete');
    closeBtn.onclick = function () {
        deleteQuestion(exercisePart);
    };
    exercisePart.appendChild(closeBtn);
    let enunciationLabel = document.createElement('span');
    enunciationLabel.textContent = "Questão:";
    exercisePart.appendChild(enunciationLabel);
    let enunciation = document.createElement('textarea');
    exercisePart.appendChild(enunciation);
    let answerLabel = document.createElement('span');
    answerLabel.textContent = "Resposta:";
    exercisePart.appendChild(answerLabel);
    let answer = document.createElement('textarea');
    exercisePart.appendChild(answer);
    elem.appendChild(exercisePart);
    if (enunciationVal !== undefined) {
        enunciation.value = enunciationVal;
        answer.value = answerVal;
    }
}

function appendSelectQuestion(elem, enunciationVal, candidates, answerIndex) {
    let exercisePart = document.createElement('div');
    exercisePart.classList.add('exercise', 'select');
    exercisePart.dataset.answers = '0';
    let closeBtn = document.createElement('span');
    closeBtn.classList.add('exercise-delete');
    closeBtn.onclick = function () {
        deleteQuestion(exercisePart);
    };
    exercisePart.appendChild(closeBtn);
    let label = document.createElement('span');
    label.textContent = "Questão:";
    exercisePart.appendChild(label);
    let enunciation = document.createElement('textarea');
    exercisePart.appendChild(enunciation);
    let addAnswer = document.createElement('a');
    addAnswer.innerText = "Adicionar resposta";
    exercisePart.appendChild(addAnswer);
    label = document.createElement('span');
    label.textContent = "Resposta:";
    exercisePart.appendChild(label);
    let correctAnswer = document.createElement('select');
    exercisePart.appendChild(correctAnswer);
    elem.appendChild(exercisePart);


    addAnswer.onclick = function () {
        let answerCount = parseInt(exercisePart.dataset.answers);
        exercisePart.dataset.answers = (answerCount + 1).toString();
        let newLabel = document.createElement('span');
        let letter = String.fromCharCode(97 + answerCount);
        newLabel.textContent = "Alinea " + letter + ":";
        exercisePart.insertBefore(newLabel, addAnswer);
        let newAnswer = document.createElement('input');
        newAnswer.type = "text";
        exercisePart.insertBefore(newAnswer, addAnswer);

        let option = document.createElement('option');
        option.value = answerCount.toString();
        option.innerText = "Alinea " + letter;
        correctAnswer.appendChild(option)

        if (candidates !== undefined) {
            newAnswer.value = candidates[answerCount];
        }
    };

    if (enunciationVal !== undefined) {
        enunciation.value = enunciationVal;
        for (let i = 0; i < candidates.length; i++)
            addAnswer.click();
        correctAnswer.selectedIndex = answerIndex;
    } else {
        addAnswer.click();
        addAnswer.click();
    }
}

function appendGroupQuestion(elem, enunciationVal) {
    let exercisePart = document.createElement('div');
    exercisePart.classList.add('exercise', 'group');
    let closeBtn = document.createElement('span');
    closeBtn.classList.add('exercise-delete');
    closeBtn.onclick = function () {
        deleteQuestion(exercisePart)
    };
    exercisePart.appendChild(closeBtn);
    let enunciationLabel = document.createElement('span');
    enunciationLabel.textContent = "Enunciado:";
    exercisePart.appendChild(enunciationLabel);
    let enunciation = document.createElement('textarea');
    exercisePart.appendChild(enunciation);
    let answerLabel = document.createElement('span');
    answerLabel.textContent = "Questões:";
    exercisePart.appendChild(answerLabel);
    let subExercises = document.createElement('div');
    subExercises.classList.add("subexercises");
    appendExercisePicker(subExercises);
    exercisePart.appendChild(subExercises);
    elem.appendChild(exercisePart);
    if (enunciationVal !== undefined)
        enunciation.value = enunciationVal;
    return subExercises;
}

function deleteQuestion(elem) {
    let root = document.getElementById("exercise-editor");
    if (elem.parentNode === root) {
        appendExercisePicker(root);
    }
    elem.remove();
}

function extractSubProblem(node) {
    if (node.classList.contains("group")) {
        let enunciation = node.querySelector("textarea");
        let subproblems = [].slice.call(node.querySelectorAll(":scope > .subexercises > .exercise")).map(extractSubProblem);
        return {type: "group", enunciation: enunciation.value, subproblems: subproblems};
    } else if (node.classList.contains("write")) {
        let textareas = node.querySelectorAll("textarea");
        return {type: "write", enunciation: textareas[0].value, answer: textareas[1].value};
    } else if (node.classList.contains("select")) {
        let enunciation = node.querySelector("textarea").value;
        let candidates = [].slice.call(
            document.getElementById("exercise-editor").querySelectorAll("input[type='text']")
        ).map(x => x.value);
        let answerSelector = node.querySelector("select");
        let answerIndex = parseInt(answerSelector.options[answerSelector.selectedIndex].value);
        return {type: "select", enunciation: enunciation, candidates: candidates, answerIndex: answerIndex};
    }
}

function previewExercise() {
    let exercise = extractSubProblem(document.getElementById("exercise-editor").querySelector(".exercise"));
    let root = document.createElement('div');
    root.id = "exercise-preview";
    let popup = window.open("", "Exercício", "width=800,height=640");
    previewSubExercise(exercise, root, "1");
    popup.document.querySelector('body').appendChild(root);
}


function previewSubExercise(exercise, root, prefix) {
    let title = document.createElement('h3');
    title.innerText = prefix;
    root.appendChild(title);
    let enunciation = document.createElement('blockquote');
    enunciation.innerText = exercise.enunciation;
    root.appendChild(enunciation);
    switch (exercise.type) {
        case "group":
            let groupContainer = document.createElement('div');
            groupContainer.style.paddingLeft = "20px";
            for (const [i, problem] of exercise.subproblems.entries()) {
                previewSubExercise(problem, groupContainer, prefix + "." + i);
            }
            root.appendChild(groupContainer);
            break;
        case "write":
            let answer = document.createElement('span');
            answer.innerText = "Resposta:" + exercise.answer;
            root.appendChild(answer);
            break;
        case "select":
            let container = document.createElement('div');
            for (const [i, candidate] of exercise.candidates.entries()) {
                let id = "ex-" + prefix + i;
                let option = document.createElement('input');
                option.id = id;
                option.name = "ex-" + prefix;
                option.type = "radio";
                container.appendChild(option);
                let label = document.createElement('label');
                label.htmlFor = id;
                label.innerText = candidate;
                container.appendChild(label);
                container.appendChild(document.createElement('br'));
            }
            root.appendChild(container);
            break;
    }
}

function loadNode(root, exercise) {
    switch (exercise.type) {
        case "group":
            let subproblemNode = appendGroupQuestion(root, exercise.enunciation);
            for (let subproblem of exercise.subproblems) {
                loadNode(subproblemNode, subproblem);
            }
            moveExercisePicker(subproblemNode.querySelector('.subexercises-options'));
            break;
        case "write":
            appendWriteQuestion(root, exercise.enunciation, exercise.answer);
            break;
        case "select":
            appendSelectQuestion(root, exercise.enunciation, exercise.candidates, exercise.answerIndex);
            break;
    }
}

(load = function () {
    let editor = document.getElementById("exercise-editor");
    let form = document.querySelector("form");
    let dataField = document.getElementById("exercise").querySelector('input[type="hidden"]');
    if (dataField.value === "null") {
        appendExercisePicker(editor);
    } else {
        loadNode(editor, JSON.parse(dataField.value));
        // previewExercise();
    }
    let submissionCleanup = function (e) {
        // if (e.preventDefault) e.preventDefault();
        dataField.value = JSON.stringify(
            extractSubProblem(document.getElementById("exercise-editor").querySelector(".exercise")));
        return true;
    }

    if (form.attachEvent) {
        form.attachEvent("submit", submissionCleanup);
    } else {
        form.addEventListener("submit", submissionCleanup);
    }
})();