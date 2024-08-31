document.addEventListener('DOMContentLoaded', function () {

    var tabs = document.querySelectorAll('.tab');
    var tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            // Удаляем активный класс у всех вкладок и контентов
            tabs.forEach(function (t) { t.classList.remove('active'); });
            tabContents.forEach(function (content) { content.classList.remove('active'); });

            // Добавляем активный класс к выбранной вкладке и контенту
            tab.classList.add('active');
            document.getElementById(tab.getAttribute('data-target')).classList.add('active');
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    function setRowNumbers(className) {
        var rows = document.querySelectorAll(className);
        var counter = 1;
        rows.forEach(function(row) {
            row.querySelector('.row-number').textContent = counter++;
        });
    }

    setRowNumbers('.under-consideration-row');
    setRowNumbers('.other-row');
});