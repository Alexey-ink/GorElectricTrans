document.addEventListener('DOMContentLoaded', function() {
    // Найдите все кнопки по идентификаторам
    const applyButton = document.getElementById('apply-btn');
    const scheduleListButton = document.getElementById('schedule-list-btn');
    const scheduleChartButton = document.getElementById('schedule-chart-btn');
    const somethingElseButton = document.getElementById('something-else-btn');
    const logoutButton = document.getElementById('logout-btn');

    // Установите обработчики событий для активных кнопок
    applyButton.addEventListener('click', function() {
        window.location.href = '/apps/'; // URL для кнопки "Подать заявку"
    });

    scheduleListButton.addEventListener('click', function() {
        window.location.href = '/administrator/'; // URL для кнопки "Просмотреть расписание отпусков списком"
    });

    scheduleChartButton.addEventListener('click', function() {
        window.location.href = '/schedule/chart/'; // URL для кнопки "Просмотреть расписание отпусков на диаграмме"
    });

    // Для неактивной кнопки просто не добавляем обработчик событий

    // Обработчик для кнопки выхода
    logoutButton.addEventListener('click', function() {
        window.location.href = '/logout/'; // URL для выхода из системы
    });
});
