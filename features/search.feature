Feature: House prices can be searched by postcode and date

  Scenario: I can find house prices by postcode
    Given a house price search engine with July 2016 data
     When I open the search page
      And I enter the post code GL5 4TT
      And I click the search button
     Then all house prices should be in GL5

  Scenario: I can find house prices by date
    Given a house price search engine with July 2016 data
     When I open the search page
      And I enter a start date of 14 July
      And I enter an end date of 21 July
      And I click the search button
     Then all house prices should be for sales between 14 July and 21 July

  Scenario: I can find house prices by postcode and date
    Given a house price search engine with July 2016 data
     When I open the search page
      And I enter the post code GL5 4TT
      And I enter a start date of 14 July
      And I enter an end date of 21 July
      And I click the search button
     Then all house prices should be in GL5
      And all house prices should be for sales between 14 July and 21 July
