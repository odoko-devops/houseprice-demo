'use strict';

angular.module('salesApp.listing', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/listing', {
    templateUrl: 'partials/listing/listing.html',
    controller: 'ListingCtrl'
  });
}])

.controller('ListingCtrl', function($scope, Sales) {
  $scope.$parent.tab = "listing";

  $scope.search = function() {
    $scope.rows=10;
    $scope.doSearch();
  }

  $scope.doSearch = function() {
    Sales.get({postcode: $scope.postcode, rows: $scope.rows}, function(data) {
      $scope.sales = data.sales;

      $scope.markers = [];
      for (var i in $scope.sales) {
        var sale = $scope.sales[i];
        $scope.markers.push({
          id: sale.id,
          latitude: sale.lat,
          longitude: sale.lon,
          title: sale
        })
      }
      $scope.map = {};
    })
  }

  $scope.more = function() {
    $scope.rows+=10;
    $scope.doSearch();
  }
    $scope.$parent.search = $scope.search;
});