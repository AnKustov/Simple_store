var categoryItems = document.querySelectorAll('.category-link');

categoryItems.forEach(function (item) {
    item.addEventListener('click', function (e) {
        e.stopPropagation();
    });
});

