function toggleArrow(btn) {
    if(btn.innerText == '▼') {
        btn.innerText = '▲'
    } else {
        btn.innerText = '▼'
    }
}

$('#btnOne').click(function () {
    toggleArrow(document.getElementById('arrowOne'));
})

$('#btnTwo').click(function () {
    toggleArrow(document.getElementById('arrowTwo'));
})

$('#btnThree').click(function () {
    toggleArrow(document.getElementById('arrowThree'));
})

$('#btnFour').click(function () {
    toggleArrow(document.getElementById('arrowFour'));
})