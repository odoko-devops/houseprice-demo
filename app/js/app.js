'use strict';

angular.module('salesApp', [
  'ngRoute',
  'ngResource',
  'salesApp.listing',
  'salesApp.map',
])

.config(['$locationProvider', '$routeProvider', function($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('!');

  $routeProvider.otherwise({redirectTo: '/listing'});
}])
.factory("Sales",
  ['$resource', function($resource) { return $resource('/api/sales/', {}, {
    "get": {method: "GET", params:
    {
      postcode: "@postcode",
      date_start: "@date_start",
      date_end: "@date_end"
    }}});
  }]
)

.controller("MainController", function($scope, Sales) {

    $scope.postcode="GL5_";
    if ($scope.search) $scope.search();
});
