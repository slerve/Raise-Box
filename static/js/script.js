document.getElementById('paymentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const phone = document.getElementById('phone').value;
    const amount = document.getElementById('amount').value;

    fetch('/stk_push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, amount })
    })
        .then(response => response.json())
        .then(data => {
            const responseDiv = document.getElementById('response');
            responseDiv.innerHTML = `<p>${JSON.stringify(data)}</p>`;
        })
        .catch(err => console.error('Error:', err));
});
