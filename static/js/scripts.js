// ========= CSRF =========
      function getCookie(name){
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
      }
      function getCsrf(){ return getCookie('csrftoken') || $('[name=csrfmiddlewaretoken]').val() || ''; }
      $.ajaxSetup({
        beforeSend: function(xhr, settings){
          if (!/^GET|HEAD|OPTIONS|TRACE$/i.test(settings.type)) {
            xhr.setRequestHeader('X-CSRFToken', getCsrf());
          }
        }
      });

      // ========= Helpers =========
      function setBadgeQty(q){ if (typeof q !== 'undefined' && q !== null) $('#cart_quantity').text(q); }
      function applyMiniCartUpdate(json){
        if (json && typeof json.body === 'string')  $('#mini-cart-body').html(json.body);
        if (json && typeof json.footer === 'string') $('#mini-cart-footer').html(json.footer);
        setBadgeQty(json?.qty ?? json?.cart_qty);
      }
      function openOffcanvas(selector){
        try{
          const el = document.querySelector(selector);
          if (!el) return;
          const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(el);
          bsOffcanvas.show();
        }catch(e){}
      }
      function parseQuery(href){
        try{ const u = new URL(href, window.location.origin); return Object.fromEntries(u.searchParams.entries()); }
        catch(e){ return {}; }
      }
      function clampQty(val, min, max){
        let n = parseInt(val, 10);
        if (isNaN(n)) n = min ?? 1;
        if (typeof min === 'number') n = Math.max(min, n);
        if (typeof max === 'number') n = Math.min(max, n);
        return n;
      }
      function debounce(fn, delay){
        let t; return function(...args){ clearTimeout(t); t = setTimeout(() => fn.apply(this, args), delay); };
      }

      // ========= Update helper =========
      function getUpdateUrlFor(productId){
        const $src = $('.qty-input[data-index="'+productId+'"], .qty-plus[data-index="'+productId+'"], .qty-minus[data-index="'+productId+'"]');
        const fromData = $src.data('update-url');
        if (fromData) return fromData;
        const $btn = $('.update-cart[data-index="'+productId+'"]');
        return $btn.data('update-url') || '/cart/update/';
      }
      function sendUpdate(productId, qty){
        const updateUrl = getUpdateUrlFor(productId);
        if (!updateUrl) return console.error('Missing update URL');

        $.ajax({
          type: 'POST',
          url: updateUrl,
          dataType: 'json',
          data: { product_id: productId, product_qty: qty, action: 'post' },
          success: function(json){
            applyMiniCartUpdate(json);
            if (!json?.body && !json?.footer) setBadgeQty(json?.qty ?? json?.cart_qty);
          },
          error: function(xhr){
            console.error('Update error', xhr.status, xhr.responseText);
            alert('Could not update cart.');
          }
        });
      }
      const debouncedSendUpdate = debounce(sendUpdate, 350);

      // ========= Add to cart =========
      $(document).on('click', '#add-cart, .add-to-cart', function(e){
        e.preventDefault();

        const $btn      = $(this);
        const productId = $btn.val() || $btn.data('product-id');
        const addUrl    = $btn.data('add-url') || '/cart/add/';
        const quantity  = 1;

        if (!productId) return console.error('Missing product id for add-to-cart');

        $btn.prop('disabled', true).html('Adding...');

        $.ajax({
          type: 'POST',
          url: addUrl,
          dataType: 'json',
          data: { product_id: productId, product_qty: quantity, action: 'post' },
          success: function(json){
            applyMiniCartUpdate(json);
            $btn.html('✓ Added').addClass('added');
            setTimeout(() => {
              $btn.prop('disabled', false)
                  .html('<i class="bi-cart-fill me-1"></i>')
                  .removeClass('added');
            }, 900);
            openOffcanvas('#offcanvasCart');
          },
          error: function(xhr){
            console.error('Add error', xhr.status, xhr.responseText);
            alert('Could not add to cart.');
            $btn.prop('disabled', false).html('<i class="bi-cart-fill me-1"></i>');
          }
        });
      });

      // ========= Update Cart =========
      $(document).on('click', '.update-cart', function(e){
        e.preventDefault();
        const $btn      = $(this);
        const productId = $btn.data('index');
        if (!productId) return console.error('Missing product id on .update-cart');

        const $input = $('.qty-input[data-index="'+productId+'"]');
        const min = parseInt($input.attr('min') || '1', 10);
        const max = parseInt($input.attr('max') || '99', 10);
        const qty = clampQty($input.val(), min, max);

        $btn.prop('disabled', true);
        sendUpdate(productId, qty);
        setTimeout(() => $btn.prop('disabled', false), 400);
      });

      // ========= Qty Plus/Minus =========
      $(document).on('click', '.qty-plus, .qty-minus', function(e){
        e.preventDefault();
        const $btn      = $(this);
        const productId = $btn.data('index');
        const $input    = $('.qty-input[data-index="'+productId+'"]');
        if (!$input.length) return;

        const min = parseInt($input.attr('min') || '1', 10);
        const max = parseInt($input.attr('max') || '99', 10);
        let qty   = clampQty($input.val(), min, max);

        if ($btn.hasClass('qty-plus'))  qty = clampQty(qty + 1, min, max);
        if ($btn.hasClass('qty-minus')) qty = clampQty(qty - 1, min, max);

        $input.val(qty).trigger('change');
      });

      // ========= Qty Tippen / Enter =========
      $(document).on('input change', '.qty-input', function(){
        const $input    = $(this);
        const productId = $input.data('index');
        const min = parseInt($input.attr('min') || '1', 10);
        const max = parseInt($input.attr('max') || '99', 10);
        const qty = clampQty($input.val(), min, max);
        if (String(qty) !== String($input.val())) $input.val(qty);
        debouncedSendUpdate(productId, qty);
      });
      $(document).on('keydown', '.qty-input', function(e){
        if (e.key === 'Enter'){
          e.preventDefault();
          const $input    = $(this);
          const productId = $input.data('index');
          const min = parseInt($input.attr('min') || '1', 10);
          const max = parseInt($input.attr('max') || '99', 10);
          const qty = clampQty($input.val(), min, max);
          sendUpdate(productId, qty);
        }
      });

      // ========= Delete from Cart =========
      $(document).on('click', '.delete-product', function(e){
        e.preventDefault();

        const $btn     = $(this);
        const dataId   = $btn.data('index');
        const urlAttr  = $btn.data('delete-url') || $btn.attr('href') || '/cart/delete/';

        let productId = dataId;
        if (!productId) {
          const q = parseQuery(urlAttr);
          if (q.product_id) productId = parseInt(q.product_id, 10);
        }
        if (!productId) return console.error('Missing product id for delete');

        $btn.prop('disabled', true);

        $.ajax({
          type: 'POST',
          url: urlAttr.split('?')[0],
          dataType: 'json',
          data: { product_id: productId, action: 'post' },
          success: function(json){
            applyMiniCartUpdate(json);
          },
          error: function(xhr){
            console.error('Delete error', xhr.status, xhr.responseText);
            alert('Could not remove item.');
          },
          complete: function(){
            $btn.prop('disabled', false);
          }
        });
      });