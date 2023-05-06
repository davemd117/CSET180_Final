var subtotals = document.getElementsByClassName('subtotal');
var total = document.getElementById('total');
var total_input = document.getElementById('total_input');

function updateTotal() {
    var totalValue = 0;
    Array.from(subtotals).forEach(function (subtotal) {
        var subtotalValue = parseFloat(subtotal.innerHTML.replace('Subtotal: $',''));
        totalValue += subtotalValue;
    });
    total.innerHTML = `Total: $${totalValue.toFixed(2)}`;
    total_input.value = totalValue.toFixed(2);
}

updateTotal();