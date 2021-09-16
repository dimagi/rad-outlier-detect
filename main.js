function toggleArrow(txt) {
    if(btn.innerText == '▼') {
        btn.innerText = '▲'
    } else {
        btn.innerText = '▼'
    }
}

$('#collapseOne').on('shown.bs.collapse', function () {
    toggleArrow(this);
})

$('#collapseTwo').on('shown.bs.collapse', function () {
    toggleArrow(this);
})

$('#collapseThree').on('shown.bs.collapse', function () {
    toggleArrow(this);
})

$('#collapseFour').on('shown.bs.collapse', function () {
    toggleArrow(this)
});