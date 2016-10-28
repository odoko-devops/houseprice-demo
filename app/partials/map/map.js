'use strict';

angular.module('salesApp.map', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/map', {
    templateUrl: 'partials/map/map.html',
    controller: 'MapCtrl'
  });
}])

.controller('MapCtrl', function($scope, Sales) {
  $scope.$parent.tab = "map";

  $scope.click = function(data, name, marker) {
    $scope.lat = marker.latitude;
    $scope.lon = marker.longitude;
    if ($scope.clicked) {
      $scope.clicked.show = false;
    }
    $scope.clicked = marker;
  }

    $scope.drag = function(map, eventName, args) {
      console.dir(map.getBounds());
    }

  $scope.search = function() {
    Sales.get({postcode: $scope.postcode, rows: 100}, function(data) {
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
  $scope.$parent.search = $scope.search;
});

/*
Listing search: find fixed-n results
Map search (from text box):
 find up to 1000? results defined by search
Map drag/zoom:
 find up to 1000? results within map bounds

 Get clear first what it is supposed to do
 */