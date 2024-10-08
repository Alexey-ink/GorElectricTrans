document.addEventListener('DOMContentLoaded', function() {
    // Найдите все кнопки по идентификаторам
    const applyButton = document.getElementById('apply-btn');
    const scheduleListButton = document.getElementById('schedule-list-btn');
    const logoutButton = document.getElementById('logout-btn');

    // Установите обработчики событий для активных кнопок
    applyButton.addEventListener('click', function() {
        window.location.href = '/apps/'; // URL для кнопки "Подать заявку"
    });

    scheduleListButton.addEventListener('click', function() {
        window.location.href = '/user_apps/'; // URL для кнопки "Просмотреть расписание отпусков списком"
    });


    // Для неактивной кнопки просто не добавляем обработчик событий

    // Обработчик для кнопки выхода
    logoutButton.addEventListener('click', function() {
        window.location.href = '/logout/'; // URL для выхода из системы
    });
});


window.addEventListener('load', function() {
    const preloader = document.querySelector('.preloader');
    preloader.classList.add('hidden');

    const menu = document.querySelector('.menu');
    setTimeout(() => {
        menu.style.opacity = 1;
        menu.style.transform = 'translateY(0)';
    }, 1000); // Задержка для завершения анимации экрана загрузки
});
