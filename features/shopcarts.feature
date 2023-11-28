Feature: The shopcarts service back-end
    As an E-Commerce Owner
    I need a RESTful catalog service
    So that I can keep track of all my shopcarts


Background:
    Given the following shopcarts

        | customer_id   | 
        | 0             | 
        | 1             | 
        | 2             | 
        | 3             | 


    Given the following items
        | customer_id | name      | quantity | price | description              |
        | 0           | itemOne   | 4        | 3.99  | itemOne for customer 0   |
        | 1           | itemTwo   | 3        | 2.99  | itemTwo for customer 1   |
        | 2           | itemThree | 1        | 0.77  | itemThree for customer 2 |
        | 3           | itemFour  | 299      | 29    | itemFour for customer 3  |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart Demo RESTful Service" in the title
    And I should not see "404 Not Found"


Scenario: read a shopcarts
    When I visit the "Home Page"
    And I set the "customer id" to "0"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field 
    And I paste the "Shopcart id" field 
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "0" in the "customer id" field


Scenario: read a item in a shopcart 
    When I visit the "Home Page"
    And I set the "customer id" to "0"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Item ID" field 
    And I paste the "item item id" field
    And I copy the "Shopcart ID" field 
    And I paste the "Item Shopcart id" field 
    And I press the "Item Retrieve" button
    Then I should see the message "Success"
    And I should see "itemOne" in the "item name" field

Scenario: Create a shopcart
    When I visit the "Home Page"
    And I set the "customer id" to "4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I press the "Clear" button
    Then the "Shopcart ID" field should be empty
    When I paste the "Shopcart ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "4" in the "Customer ID" field


Scenario: Create an item in the shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "0"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I paste the "Item Shopcart id" field
    And I set the "Item Name" to "Item6"
    And I set the "Item Quantity" to "6"
    And I set the "Item Price" to "666"
    And I set the "item description" to "the new created item"
    And I press the "Item add" button
    Then I should see the message "Success"
    When I press the "Item Clear" button
    Then the "Item Name" field should be empty
    And the "Item Quantity" field should be empty
    And the "Item Price" field should be empty
    When I copy the "Shopcart ID" field
    And I paste the "Item Shopcart id" field
    And I press the "Item Search" button
    Then I should see the message "Success"
    And I should see "Item6" in the item results
    And I should see "6" in the item results
    And I should see "the new created item" in the item results

Scenario: List all shopcarts
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "0" in the results
    And I should see "1" in the results
    And I should see "2" in the results
    And I should see "3" in the results


Scenario: List items in a shopcart 
    When I visit the "Home Page"
    And I set the "Customer ID" to "0"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I paste the "Item Shopcart id" field
    And I press the "Item search" button
    Then I should see the message "Success"
    And I should see "itemOne" in the item results

Scenario: Delete a Shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "0"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I press the "Clear" button
    Then the "Shopcart ID" field should be empty
    When I paste the "Shopcart ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I press the "Delete" button
    Then I should see the message "Shopcart has been Deleted!"   
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "Shopcart ID" in the results


