$(document).on('click', '#add-cart', function(e) {
    e.preventDefault();
    console.log("Button geklickt"); // Debug-Ausgabe
    
    let productId = $(this).val();
    console.log("Produkt-ID:", productId); // Debug-Ausgabe

    $.ajax({
        type: 'POST',
        url: '{% url "cart_add" %}',
        data: {
            product_id: productId,
            product_qty: 1, // Immer 1 Produkt pro Klick
            csrfmiddlewaretoken: '{{ csrf_token }}',
            action: 'post'
        },
        success: function(json) {
            console.log("Erfolgreich:", json); // Debug-Ausgabe
            if(json.success) {
                // Aktualisiere Warenkorb-Anzeige
                $('#cart_quantity').text(json.qty);
                // Visuelles Feedback
                $('#add-cart').text("✓ Hinzugefügt").prop('disabled', true);
                setTimeout(function() {
                    $('#add-cart').text("Zum Warenkorb").prop('disabled', false);
                }, 1500);
            }
        },
        error: function(xhr, errmsg, err) {
            console.error("Fehler:", xhr.status, errmsg); // Debug-Ausgabe
            alert("Fehler beim Hinzufügen zum Warenkorb");
        }
    });
});