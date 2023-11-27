$(function() {

    // Массивы с элементами опций фильтрации: блок, стрелка и название опции
    const filterOptionsBlocks = [$('.price-options div'), $('.popularity-options div'), $('.category-options div'), $('.rating-options div')];
    const filterArrows = [$('#price-arrow'), $('#popularity-arrow'), $('#category-arrow'), $('#rating-arrow')];
    const filterTitles = [$('#h3-price'), $('#h3-popularity'), $('#h3-category'), $('#h3-rating')];

    // По умолчанию - скрыть все блоки опций фильтра
    filterOptionsBlocks.map((filterOptionBlock) => filterOptionBlock.hide());

    // Функция по скрытию или раскрытию стрелок
    function toggleArrow(toggledArrow) {
        for (let arrow of filterArrows) {
            if (arrow == toggledArrow) {
                if (toggledArrow.hasClass('rotated')) {
                    toggledArrow.removeClass('rotated');
                } else {
                    toggledArrow.addClass('rotated');
                }
            } else {
                arrow.removeClass('rotated');
            }
        }
    }

    // Функция по скрытию или раскрытию блоков опций фильтра
    function toggleFilterOptionBlock(toggledFilterBlock, toggledArrow) {
        toggleArrow(toggledArrow);

        for (let filterOptionBlock of filterOptionsBlocks) {
            if (filterOptionBlock != toggledFilterBlock) {
                filterOptionBlock.slideUp(300);
            }
        }
        
        toggledFilterBlock.slideToggle();
    }

    // Для каждого h3 применить функцию - раскрытия/скрытия соответствующего блока опции
    for (let i = 0; i < filterTitles.length; i++) {
        filterTitles[i].on('click', () => toggleFilterOptionBlock(filterOptionsBlocks[i], filterArrows[i]))
    }

});
