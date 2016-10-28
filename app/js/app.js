'use strict';

angular.module('salesApp', [
  'ngRoute',
  'ngResource',
  'salesApp.listing',
  'salesApp.map',
  'uiGmapgoogle-maps'
])

.config(['$locationProvider', '$routeProvider', function($locationProvider, $routeProvider) {
  $locationProvider.hashPrefix('!');

  $routeProvider.otherwise({redirectTo: '/listing'});
}])
.config(function(uiGmapGoogleMapApiProvider) {
    uiGmapGoogleMapApiProvider.configure({
        key: 'AIzaSyATDZyez4PYWUJTK2uIHUm70kcdx9OX7eE',
        v: '3.23', //defaults to latest 3.X anyhow
        libraries: 'weather,geometry,visualization'
    });
})
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
