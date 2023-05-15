let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {   //types of places to look for
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    var geocoder= new google.maps.Geocoder()
    var address= document.getElementById('id_address').value;

    geocoder.geocode({'address':address},function(results,status){

        if(status == google.maps.GeocoderStatus.OK){
            var latitude=results[0].geometry.location.lat();
            var longitude=results[0].geometry.location.lng();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);
            $('#id_address').val(address);
        }
    });
    console.log(place.address_components);
    
    // autofill remaining fields

    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // fill country
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name);
            }
            // fill state
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name);
            }
            // fill city
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name);
            }
            // fill pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name);
            }else{
                $('#id_pin_code').val("");
            }
        }
    }
}

// cart fn
$(document).ready(function(){
    //ADD TO CART
 $('.add_to_cart').on('click',function(e){
    e.preventDefault();
    
    food_id=$(this).attr('data-id');
    url=$(this).attr('data-url');
    data={
        food_id:food_id,
    }
  
    $.ajax({
        type:"GET",
        url: url,
        data:data,
        success:function(response){
            console.log(response);
            if(response.status == 'login_required'){
                swal(response.message, '', 'info').then(function(){
                    window.location = '/login';
                })
            }else if(response.status == 'Failed'){
                swal(response.message, '', 'error')
            }else{

                console.log(response);
                // update cart count
                $('#cart_counter').html(response.cart_counter.cart_count)
                // update food count 
                $('#qty-'+food_id).html(response.quantity)
            }


        }
    })

 })

 
//  remove from cart
$('.decrease_cart').on('click',function(e){
    e.preventDefault();
    
    food_id=$(this).attr('data-id');
    cart_id=$(this).attr('id');
    url=$(this).attr('data-url');
    data={
        food_id:food_id,
    }
  
    $.ajax({
        type:"GET",
        url: url,
        data:data,
        success:function(response){
                console.log(response);
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login';
                    })
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else{

                 // update cart count
                 $('#cart_counter').html(response.cart_counter.cart_count)
                 // update food count 
                 $('#qty-'+food_id).html(response.quantity)

                 if(window.location.pathname =='/marketplace/show/cart'){
                  removeCartItem(response.quantity,cart_id)
                  showEmptyCart()
                 }

             }

        }
    })

 })

//Delete Cart
     $('.delete_cart').on('click',function(e){
        e.preventDefault();
        
        cart_id=$(this).attr('data-id');
        delete_url=$(this).attr('data-url');

        $.ajax({
            type:"GET",
            url: delete_url,

            success:function(response){
              
             if(response.status == 'Failed'){
                 swal(response.message, '', 'error')
                }else{

                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, "success")
                    removeCartItem(0,cart_id)
                    showEmptyCart()
                }
    
            }
        })
    
     })

    //  delete cart element if the qty is 0

    function removeCartItem(cartItemQty,cart_id){

        if(cartItemQty<=0 ){
            document.getElementById("cart-item-"+cart_id).remove();
        }
    }

    //  show empty cart if quantity is 0

    function showEmptyCart(){
        var cart_counter=document.getElementById('cart_counter').innerHTML

            if(cart_counter ==0){
                document.getElementById("empty-cart").style.display="block";
            }
        }

 //place the cartitem quantity on load  
 $('.item_qty').each(function(){
    var _id=$(this).attr('id')
    var quantity=$(this).attr('data-qty')

    //change the count 
    //<label id="qty-{{fooditem.pk}}">0</label> --> $('#'+_id)->qty-id
    $('#'+_id).html(quantity)
 })


});

