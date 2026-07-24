// Eventify Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
  // Realtime Ticket Quantity Price Calculator
  const quantityInput = document.getElementById('id_quantity');
  const unitPriceElem = document.getElementById('ticket_price_unit');
  const totalPriceElem = document.getElementById('total_price_calc');

  if (quantityInput && unitPriceElem && totalPriceElem) {
    const unitPrice = parseFloat(unitPriceElem.dataset.price || 0);

    function updatePrice() {
      const qty = parseInt(quantityInput.value) || 1;
      const total = unitPrice * qty;
      totalPriceElem.textContent = 'Rp ' + total.toLocaleString('id-ID');
    }

    quantityInput.addEventListener('input', updatePrice);
    quantityInput.addEventListener('change', updatePrice);
    updatePrice();
  }

  // Auto Dismiss Toast Alerts after 5s
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});

function printTicket() {
  window.print();
}
