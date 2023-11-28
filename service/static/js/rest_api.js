$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#customer_id").val(res.customer_id);
        if (res.items.length!=0) {
            $("#item_id").val(res.items[0].id);
        } else {
            $("#item_id").val("");
        }
        
        $("#max_total_price").val(res.total_price);
        $("#min_total_price").val(res.total_price);
    }

    function update_item_form_data(res) {
        $("#item_item_id").val(res.id);
        $("#item_shopcart_id").val(res.shopcart_id);
        $("#item_name").val(res.name);
        $("#item_price").val(res.price);
        $("#item_description").val(res.description);
        $("#item_quantity").val(res.quantity);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_id").val("");
        $("#customer_id").val("")
        $("#item_id").val("");
        $("#max_total_price").val("");
        $("#min_total_price").val("");
    }

    function clear_item_form_data() {
        $("#item_item_id").val("");
        $("#item_shopcart_id").val("");
        $("#item_name").val("");
        $("#item_price").val("");
        $("#item_description").val("");
        $("#item_quantity").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#customer_id").val();

        let data = {
            "customer_id":customer_id,
            "items":[]
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();
        let customer_id = $("#customer_id").val()
        
        let data = {
            "customer_id": customer_id,
            items: []
        }


        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${shopcart_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();


        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Empty a Shopcart
    // ****************************************

    $("#empty-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();
        console.log(shopcart_id)

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been emptied!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });


    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Shopcart
    // ****************************************

    $("#search-btn").click(function () {

        let item_id = $("#item_id").val();
        let max_price = $("#max_total_price").val();
        let min_price = $("#min_total_price").val();
        let customer_id = $("#customer_id").val();
        let queryString = ""

        if (item_id) {
            queryString += 'item=' + item_id
        }
        if (customer_id) {
            queryString += 'customer_id=' + customer_id
        }
        if (max_price) {
            if (queryString.length > 0) {
                queryString += '&maxprice=' + max_price
            } else {
                queryString += 'maxprice=' + max_price
            }
        }
        if (min_price) {
            if (queryString.length > 0) {
                queryString += '&minprice=' + min_price
            } else {
                queryString += 'minprice=' + min_price
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Total Price</th>'
            table += '<th class="col-md-2">Create Time</th>'
            table += '<th class="col-md-2">Last Update Time</th>'
            table += '<th class="col-md-2">Items</th>'
            table += '</tr></thead><tbody>'
            let firstCart = "";
            for(let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                let items = "";
                for (let j = 0; j < shopcart.items.length; j++) {
                    items = items + "id: "+shopcart.items[j].id + " name: " + shopcart.items[j].name + " ";
                }
                table +=  `<tr id="row_${i}"><td>${shopcart.id}</td><td>${shopcart.customer_id}</td><td>${shopcart.total_price}</td><td>${shopcart.creation_time}</td><td>${shopcart.last_updated_time}</td><td>${items}</td></tr>`;
                if (i == 0) {
                    firstCart = shopcart;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstCart != "") {
                update_form_data(firstCart)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Add an Item
    // ****************************************

    $("#item-add-btn").click(function () {

        let shopcart_id = $("#item_shopcart_id").val();
        let name = $("#item_name").val();
        let price = $("#item_price").val();
        let description = $("#item_description").val();
        let quantity = $("#item_quantity").val();

        let data = {
            "shopcart_id":shopcart_id,
            "name":name,
            "price":price,
            "description":description,
            "quantity":quantity
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update an Item
    // ****************************************

    $("#item-update-btn").click(function () {
        let item_id = $("#item_item_id").val();
        let shopcart_id = $("#item_shopcart_id").val();
        let name = $("#item_name").val();
        let price = $("#item_price").val();
        let description = $("#item_description").val();
        let quantity = $("#item_quantity").val();

        let data = {
            "shopcart_id":shopcart_id,
            "name":name,
            "price":price,
            "description":description,
            "quantity":quantity
        };
        


        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${shopcart_id}/items/${item_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Item
    // ****************************************

    $("#item-retrieve-btn").click(function () {

        let item_id = $("#item_item_id").val();
        let shopcart_id = $("#item_shopcart_id").val();


        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            //alert(res.toSource())
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_item_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#item-delete-btn").click(function () {

        let item_id = $("#item_item_id").val();
        let shopcart_id = $("#item_shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_item_form_data()
            flash_message("Item has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

     // ****************************************
    // Clear the item form
    // ****************************************

    $("#item-clear-btn").click(function () {
        $("#item_item_id").val("");
        $("#flash_message").empty();
        clear_item_form_data()
    });

    // ****************************************
    // Search for an Item
    // ****************************************

    $("#item-search-btn").click(function () {
        let shopcart_id = $("#item_shopcart_id").val();
        let name = $("#item_name").val();
        let price = $("#item_price").val();

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price
            } else {
                queryString += 'price=' + price
            }
        }


        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}/items?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#item_search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Shopcart ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for(let i = 0; i < res.length; i++) {
                let item = res[i];
                table +=  `<tr id="row_${i}"><td>${item.id}</td><td>${item.shopcart_id}</td><td>${item.name}</td><td>${item.price}</td><td>${item.description}</td><td>${item.quantity}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#item_search_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_item_form_data(firstItem)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
