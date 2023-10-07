let h3_price = document.getElementById('h3-price');


function showFilterOptions(blockName) {
    let block = document.getElementById(blockName);
    let optionsBlock = document.defaultView.getComputedStyle(block);

    if (optionsBlock.display == 'flex') {
        block.style.display = 'none';
    } else if (optionsBlock.display == 'none') {
        block.style.display = 'flex';
    }
}