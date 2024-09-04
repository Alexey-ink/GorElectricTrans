document.addEventListener('DOMContentLoaded', function() {
    // Найдите все кнопки по идентификаторам
    const applyButton = document.getElementById('apply-btn');
    const vacationCalculationButton = document.getElementById('vacation-calculation-btn');
    const logoutButton = document.getElementById('logout');

    // Установите обработчики событий для активных кнопок
    applyButton.addEventListener('click', function() {
        window.location.href = '/administrator'; // URL для кнопки "Подать заявку"
    });

    vacationCalculationButton.addEventListener('click', function() {
        window.location.href = '/settings'; // URL для кнопки "Ваши заявки"
    });

    // Обработчик для кнопки выхода
    logoutButton.addEventListener('click', function() {
        window.location.href = '/logout/'; // URL для кнопки "Выйти"
    });
});

// Ожидание полной загрузки страницы
window.addEventListener('load', function() {
    const preloader = document.querySelector('.preloader');
    preloader.classList.add('hidden');

    const menu = document.querySelector('.menu');
    setTimeout(() => {
        menu.style.opacity = 1;
        menu.style.transform = 'translateY(0)';
    }, 1000); // Задержка для завершения анимации экрана загрузки
});
